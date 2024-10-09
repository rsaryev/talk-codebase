import os
import time
import logging
from typing import Optional, List, Dict, Any

import questionary
import requests
from halo import Halo
from langchain.vectorstores import FAISS
from langchain.callbacks.manager import CallbackManager
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.llms.base import LLM
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import Field

from talk_codebase.consts import MODEL_TYPES
from talk_codebase.utils import load_files, get_local_vector_store, calculate_cost, StreamStdOut

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaEmbeddings(Embeddings):
    def __init__(self, model: str, api_url: str):
        self.model = model
        self.api_url = api_url
        logger.info(f"Ollama Embeddings API URL: {self.api_url}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            response = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": text}
            )
            embeddings.append(response.json()['embedding'])
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        response = requests.post(
            self.api_url,
            json={"model": self.model, "prompt": text}
        )
        return response.json()['embedding']


class OllamaChatModel(LLM):
    model: str = Field(..., description="The name of the Ollama model to use")
    api_url: str = Field(..., description="The API URL for the Ollama service")

    def __init__(self, model: str, api_url: str):
        super().__init__()
        self.model = model
        self.api_url = api_url
        logger.info(f"Ollama Chat API URL: {self.api_url}")

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = requests.post(
            self.api_url,
            json={"model": self.model, "prompt": prompt, "stream": False}
        )
        return response.json()['response']

    @property
    def _llm_type(self) -> str:
        return "ollama"


class BaseLLM:

    def __init__(self, root_dir, config):
        self.config = config
        self.root_dir = root_dir
        self.embedding_model = self._create_embedding_model()
        self.chat_model = self._create_chat_model()
        logger.info("Creating vector store...")
        self.vector_store = self._create_store(root_dir)
        logger.info("Vector store created successfully.")

    def _create_store(self, root_dir):
        raise NotImplementedError("Subclasses must implement this method.")

    def _create_embedding_model(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def _create_chat_model(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def embedding_search(self, query, k):
        return self.vector_store.search(query, k=k, search_type="similarity")

    def _create_vector_store(self, embeddings, index, root_dir):
        k = int(self.config.get("k", 2))
        index_path = os.path.join(root_dir, f"vector_store/{index}")
        new_db = get_local_vector_store(embeddings, index_path)
        if new_db is not None:
            logger.info("Using existing vector store.")
            return new_db.as_retriever(search_kwargs={"k": k})

        logger.info("Creating new vector store...")
        docs = load_files()
        if len(docs) == 0:
            logger.error("No documents found")
            exit(0)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(self.config.get("chunk_size", 2056)),
                                                       chunk_overlap=int(self.config.get("chunk_overlap", 256)),
                                                       separators=["\n\n", "\n", " ", ""])
        texts = text_splitter.split_documents(docs)
        
        model_type = self.config.get("embedding_model_type")
        cost = calculate_cost(texts, self.config.get("embedding_model_name"), model_type)
        
        if cost > 0:
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
        logger.info("New vector store created successfully.")
        return db.as_retriever(search_kwargs={"k": k})

    def send_query(self, query):
        logger.info(f"Processing query: {query}")
        qa = RetrievalQA.from_chain_type(
            llm=self.chat_model,
            chain_type="stuff",
            retriever=self.vector_store,
            return_source_documents=True
        )
        # Add a custom prompt to encourage more relevant responses
        custom_prompt = f"""
        You are an AI assistant specialized in analyzing codebases. 
        Given the following query about the codebase, provide the most relevant and helpful response possible.
        If you're not entirely sure, make an educated guess based on the context of the codebase.
        Query: {query}
        """
        docs = qa({"query": custom_prompt})
        
        # Print the response
        print("\n🤖 Response:")
        print(docs['result'])
        
        # Print the source files
        file_paths = [os.path.abspath(s.metadata["source"]) for s in docs['source_documents']]
        print('\n📁 Source files:')
        print('\n'.join([f'- {file_path}' for file_path in file_paths]))
        logger.info("Query processed successfully.")


class OllamaLLM(BaseLLM):

    def _create_store(self, root_dir: str) -> Optional[FAISS]:
        return self._create_vector_store(self.embedding_model, MODEL_TYPES["OLLAMA"], root_dir)

    def _create_embedding_model(self):
        embedding_model = self.config.get("embedding_model_name")
        embedding_api_url = self.config.get("embedding_api_endpoint")
        logger.info(f"Creating Ollama Embedding model: {embedding_model} with API URL: {embedding_api_url}")
        return OllamaEmbeddings(
            model=embedding_model,
            api_url=embedding_api_url
        )

    def _create_chat_model(self):
        chat_model = self.config.get("chat_model_name")
        chat_api_url = self.config.get("chat_api_endpoint")
        logger.info(f"Creating Ollama Chat model: {chat_model} with API URL: {chat_api_url}")
        return OllamaChatModel(
            model=chat_model,
            api_url=chat_api_url
        )


class OpenAILLM(BaseLLM):
    def _create_store(self, root_dir: str) -> Optional[FAISS]:
        return self._create_vector_store(self.embedding_model, MODEL_TYPES["OPENAI"], root_dir)

    def _create_embedding_model(self):
        logger.info("Creating OpenAI Embedding model")
        return OpenAIEmbeddings(
            model=self.config.get("embedding_model_name"),
            openai_api_key=self.config.get("openai_compatible_api_key")
        )

    def _create_chat_model(self):
        logger.info("Creating OpenAI Chat model")
        return ChatOpenAI(
            model_name=self.config.get("chat_model_name"),
            openai_api_key=self.config.get("openai_compatible_api_key"),
            streaming=True,
            max_tokens=int(self.config.get("max_tokens", 2056)),
            callback_manager=CallbackManager([StreamStdOut()]),
            temperature=float(self.config.get("temperature", 0.7)),
            presence_penalty=0.6,  # Encourage the model to talk about new topics
            frequency_penalty=float(self.config.get("frequency_penalty", 0.0))  # Use configured value or default to 0.0
        )


class OpenAICompatibleLLM(BaseLLM):
    def _create_store(self, root_dir: str) -> Optional[FAISS]:
        return self._create_vector_store(self.embedding_model, MODEL_TYPES["OPENAI_COMPATIBLE"], root_dir)

    def _create_embedding_model(self):
        logger.info("Creating OpenAI Compatible Embedding model")
        return OpenAIEmbeddings(
            model=self.config.get("embedding_model_name"),
            openai_api_key=self.config.get("openai_compatible_api_key"),
            openai_api_base=self.config.get("openai_compatible_endpoint")
        )

    def _create_chat_model(self):
        logger.info("Creating OpenAI Compatible Chat model")
        return ChatOpenAI(
            model_name=self.config.get("chat_model_name"),
            openai_api_key=self.config.get("openai_compatible_api_key"),
            openai_api_base=self.config.get("openai_compatible_endpoint"),
            streaming=True,
            max_tokens=int(self.config.get("max_tokens", 2056)),
            callback_manager=CallbackManager([StreamStdOut()]),
            temperature=float(self.config.get("temperature", 0.7)),
            frequency_penalty=float(self.config.get("frequency_penalty", 0.0))  # Use configured value or default to 0.0
        )


def factory_llm(root_dir, config):
    embedding_type = config.get("embedding_model_type")
    chat_type = config.get("chat_model_type")

    if embedding_type != chat_type:
        raise ValueError("Embedding and chat model types must be the same.")

    logger.info(f"Creating LLM of type: {embedding_type}")
    if embedding_type == MODEL_TYPES["OPENAI"]:
        return OpenAILLM(root_dir, config)
    elif embedding_type == MODEL_TYPES["OPENAI_COMPATIBLE"]:
        return OpenAICompatibleLLM(root_dir, config)
    elif embedding_type == MODEL_TYPES["OLLAMA"]:
        return OllamaLLM(root_dir, config)
    else:
        raise ValueError(f"Invalid model type: {embedding_type}")
