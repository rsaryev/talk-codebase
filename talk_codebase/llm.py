import os
import time
from typing import Optional

import gpt4all
import questionary
from halo import Halo
from langchain.vectorstores import FAISS
from langchain.callbacks.manager import CallbackManager
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain.llms import LlamaCpp
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
        k = int(self.config.get("k"))
        index_path = os.path.join(root_dir, f"vector_store/{index}")
        new_db = get_local_vector_store(embeddings, index_path)
        if new_db is not None:
            return new_db.as_retriever(search_kwargs={"k": k})

        docs = load_files()
        if len(docs) == 0:
            print("✘ No documents found")
            exit(0)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(self.config.get("chunk_size")),
                                                       chunk_overlap=int(self.config.get("chunk_overlap")))
        texts = text_splitter.split_documents(docs)
        if index == MODEL_TYPES["OPENAI"]:
            cost = calculate_cost(docs, self.config.get("openai_model_name"))
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
        db = FAISS.from_documents([texts[0]], embeddings)
        for i, text in enumerate(texts[1:]):
            spinners.text = f"Creating vector store ({i + 1}/{len(texts)})"
            db.add_documents([text])
            db.save_local(index_path)
            time.sleep(1.5)

        spinners.succeed(f"Created vector store")
        return db.as_retriever(search_kwargs={"k": k})

    def send_query(self, query):
        retriever = self._create_store(self.root_dir)
        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        docs = qa(query)
        file_paths = [os.path.abspath(s.metadata["source"]) for s in docs['source_documents']]
        print('\n'.join([f'📄 {file_path}:' for file_path in file_paths]))


class LocalLLM(BaseLLM):

    def _create_store(self, root_dir: str) -> Optional[FAISS]:
        embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
        return self._create_vector_store(embeddings, MODEL_TYPES["LOCAL"], root_dir)

    def _create_model(self):
        os.makedirs(self.config.get("model_path"), exist_ok=True)
        gpt4all.GPT4All.retrieve_model(model_name=self.config.get("local_model_name"),
                                       model_path=self.config.get("model_path"))
        model_path = os.path.join(self.config.get("model_path"), self.config.get("local_model_name"))
        model_n_ctx = int(self.config.get("max_tokens"))
        model_n_batch = int(self.config.get("n_batch"))
        callbacks = CallbackManager([StreamStdOut()])
        llm = LlamaCpp(model_path=model_path, n_ctx=model_n_ctx, n_batch=model_n_batch, callbacks=callbacks,
                       verbose=False)
        llm.client.verbose = False
        return llm


class OpenAILLM(BaseLLM):
    def _create_store(self, root_dir: str) -> Optional[FAISS]:
        embeddings = OpenAIEmbeddings(openai_api_key=self.config.get("api_key"))
        return self._create_vector_store(embeddings, MODEL_TYPES["OPENAI"], root_dir)

    def _create_model(self):
        return ChatOpenAI(model_name=self.config.get("openai_model_name"),
                          openai_api_key=self.config.get("api_key"),
                          streaming=True,
                          max_tokens=int(self.config.get("max_tokens")),
                          callback_manager=CallbackManager([StreamStdOut()]),
                          temperature=float(self.config.get("temperature")))


def factory_llm(root_dir, config):
    if config.get("model_type") == "openai":
        return OpenAILLM(root_dir, config)
    else:
        return LocalLLM(root_dir, config)
