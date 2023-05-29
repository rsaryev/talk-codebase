import os

import questionary
import tiktoken
from halo import Halo
from langchain import FAISS
from langchain.callbacks.manager import CallbackManager
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from talk_codebase.utils import StreamStdOut, load_files


def calculate_cost(texts, model_name):
    enc = tiktoken.encoding_for_model(model_name)
    all_text = ''.join([text.page_content for text in texts])
    tokens = enc.encode(all_text)
    token_count = len(tokens)
    cost = (token_count / 1000) * 0.0004
    return cost


def get_local_vector_store(embeddings):
    try:
        return FAISS.load_local("vector_store", embeddings)
    except:
        return None


def create_vector_store(root_dir, openai_api_key, model_name):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    new_db = get_local_vector_store(embeddings)
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
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(docs)

    cost = calculate_cost(docs, model_name)
    approve = questionary.select(
        f"Creating a vector store for {len(docs)} documents will cost ~${cost:.5f}. Do you want to continue?",
        choices=[
            {"name": "Yes", "value": True},
            {"name": "No", "value": False},
        ]
    ).ask()

    if not approve:
        exit(0)

    spinners = Halo(text='Creating vector store', spinner='dots').start()
    db = FAISS.from_documents(texts, embeddings)
    db.save_local("vector_store")
    spinners.succeed(f"Created vector store with {len(docs)} documents")

    return db


def send_question(question, vector_store, openai_api_key, model_name):
    model = ChatOpenAI(model_name=model_name, openai_api_key=openai_api_key, streaming=True,
                       callback_manager=CallbackManager([StreamStdOut()]))
    qa = ConversationalRetrievalChain.from_llm(model,
                                               retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
                                               return_source_documents=True)
    answer = qa({"question": question, "chat_history": []})
    print('\n' + '\n'.join([f'📄 {os.path.abspath(s.metadata["source"])}:' for s in answer["source_documents"]]))
    return answer
