import os
from typing import Optional

import questionary
from halo import Halo
from langchain import FAISS
from langchain.callbacks.manager import CallbackManager
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain.llms import GPT4All
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

    def send_query(self, question):
        k = self.config.get("k")
        qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff",
                                         retriever=self.vector_store.as_retriever(search_kwargs={"k": int(k)}),
                                         return_source_documents=True)
        answer = qa(question)
        print('\n' + '\n'.join([f'📄 {os.path.abspath(s.metadata["source"])}:' for s in answer["source_documents"]]))

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
                f"Creating a vector store for {len(docs)} documents will cost ~${cost:.5f}. Do you want to continue?",
                choices=[
                    {"name": "Yes", "value": True},
                    {"name": "No", "value": False},
                ]
            ).ask()
            if not approve:
                exit(0)

        spinners = Halo(text=f"Creating vector store for {len(docs)} documents", spinner='dots').start()
        db = FAISS.from_documents(texts, embeddings)
        db.add_documents(texts)
        db.save_local(index_path)
        spinners.succeed(f"Created vector store for {len(docs)} documents")
        return db


class LocalLLM(BaseLLM):

    def _create_store(self, root_dir: str) -> Optional[FAISS]:
        embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
        return self._create_vector_store(embeddings, MODEL_TYPES["LOCAL"], root_dir)

    def _create_model(self):
        llm = GPT4All(model=self.config.get("model_path"), n_ctx=int(self.config.get("max_tokens")), streaming=True)
        return llm


class OpenAILLM(BaseLLM):
    def _create_store(self, root_dir: str) -> Optional[FAISS]:
        embeddings = OpenAIEmbeddings(openai_api_key=self.config.get("api_key"))
        return self._create_vector_store(embeddings, MODEL_TYPES["OPENAI"], root_dir)

    def _create_model(self):
        return ChatOpenAI(model_name=self.config.get("model_name"), openai_api_key=self.config.get("api_key"),
                          streaming=True,
                          max_tokens=int(self.config.get("max_tokens")),
                          callback_manager=CallbackManager([StreamStdOut()]))


def factory_llm(root_dir, config):
    if config.get("model_type") == "openai":
        return OpenAILLM(root_dir, config)
    else:
        return LocalLLM(root_dir, config)
