import os
from typing import Optional

import questionary
from halo import Halo
from langchain import FAISS
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain.llms import GPT4All
from langchain.schema import HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter

from talk_codebase.consts import MODEL_TYPES
from talk_codebase.utils import load_files, get_local_vector_store, calculate_cost, StreamStdOut


class BaseLLM:

    def __init__(self, root_dir, config):
        self.config = config
        self.llm = self._create_model()
        self.root_dir = root_dir
        self.vector_store = self._create_store(root_dir)

    def _create_store(self, root_dir):
        raise NotImplementedError("Subclasses must implement this method.")

    def _create_model(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def embedding_search(self, query, k):
        return self.vector_store.search(query, k=k, search_type="similarity")

    def _create_vector_store(self, embeddings, index, root_dir):
        index_path = os.path.join(root_dir, f"vector_store/{index}")
        new_db = get_local_vector_store(embeddings, index_path)
        if new_db is not None:
            approve = questionary.select(
                f"Found existing vector store. Do you want to use it?",
                choices=[
                    {"name": "Yes", "value": True},
                    {"name": "No", "value": False},
                ]
            ).ask()
            if approve:
                return new_db

        docs = load_files(root_dir)
        if len(docs) == 0:
            print("✘ No documents found")
            exit(0)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(self.config.get("chunk_size")),
                                                       chunk_overlap=int(self.config.get("chunk_overlap")))
        texts = text_splitter.split_documents(docs)
        if index == MODEL_TYPES["OPENAI"]:
            cost = calculate_cost(docs, self.config.get("model_name"))
            approve = questionary.select(
                f"Creating a vector store will cost ~${cost:.5f}. Do you want to continue?",
                choices=[
                    {"name": "Yes", "value": True},
                    {"name": "No", "value": False},
                ]
            ).ask()
            if not approve:
                exit(0)

        spinners = Halo(text=f"Creating vector store", spinner='dots').start()
        db = FAISS.from_documents(texts, embeddings)
        db.add_documents(texts)
        db.save_local(index_path)
        spinners.succeed(f"Created vector store")
        return db


class LocalLLM(BaseLLM):

    def _create_store(self, root_dir: str) -> Optional[FAISS]:
        embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
        return self._create_vector_store(embeddings, MODEL_TYPES["LOCAL"], root_dir)

    def _create_model(self):
        llm = GPT4All(model=self.config.get("model_path"), n_ctx=int(self.config.get("max_tokens")), streaming=True)
        return llm

    def send_query(self, query):
        k = self.config.get("k")
        docs = self.embedding_search(query, k=int(k))

        content = "\n".join([f"content: \n```{s.page_content}```" for s in docs])
        template = "Given the following content, your task is to answer the question.\nQuestion: {question}\n{content}"

        prompt = PromptTemplate(template=template, input_variables=["content", "question"]).partial(content=content)
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)

        llm_chain.run(query)

        file_paths = [os.path.abspath(s.metadata["source"]) for s in docs]
        print('\n'.join([f'📄 {file_path}:' for file_path in file_paths]))


class OpenAILLM(BaseLLM):
    def _create_store(self, root_dir: str) -> Optional[FAISS]:
        embeddings = OpenAIEmbeddings(openai_api_key=self.config.get("api_key"))
        return self._create_vector_store(embeddings, MODEL_TYPES["OPENAI"], root_dir)

    def _create_model(self):
        return ChatOpenAI(model_name=self.config.get("model_name"),
                          openai_api_key=self.config.get("api_key"),
                          streaming=True,
                          max_tokens=int(self.config.get("max_tokens")),
                          callback_manager=CallbackManager([StreamStdOut()]),
                          temperature=float(self.config.get("temperature")))

    def send_query(self, query):
        k = self.config.get("k")
        docs = self.embedding_search(query, k=int(k))

        content = "\n".join([f"content: \n```{s.page_content}```" for s in docs])
        prompt = f"Given the following content, your task is to answer the question. \n{content}"

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=query),
        ]

        self.llm(messages)

        file_paths = [os.path.abspath(s.metadata["source"]) for s in docs]
        print('\n'.join([f'📄 {file_path}:' for file_path in file_paths]))


def factory_llm(root_dir, config):
    if config.get("model_type") == "openai":
        return OpenAILLM(root_dir, config)
    else:
        return LocalLLM(root_dir, config)
