import os

import questionary
import tiktoken
from halo import Halo
from langchain import FAISS
from langchain.callbacks.manager import CallbackManager
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter

from talk_codebase.utils import StreamStdOut, load_files


def calculate_cost(texts):
    enc = tiktoken.get_encoding("cl100k_base")
    all_text = ''.join([text.page_content for text in texts])
    tokens = enc.encode(all_text)
    token_count = len(tokens)
    rate_per_thousand_tokens = 0.0004
    cost = (token_count / 1000) * rate_per_thousand_tokens
    return cost


def create_vector_store(root_dir, openai_api_key):
    docs = load_files(root_dir)
    if len(docs) == 0:
        print("✘ No documents found")
        exit(0)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(docs)

    cost = calculate_cost(docs)
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
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    db = FAISS.from_documents(texts, embeddings)
    spinners.succeed(f"Created vector store with {len(docs)} documents")

    return db


def send_question(question, vector_store, openai_api_key, model_name):
    model = ChatOpenAI(model_name=model_name, openai_api_key=openai_api_key, streaming=True,
                       callback_manager=CallbackManager([StreamStdOut()]))
    qa = ConversationalRetrievalChain.from_llm(model,
                                               retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
                                               return_source_documents=True)
    answer = qa({"question": question, "chat_history": []})
    print('\n' + '\n'.join([f'📄 {os.path.abspath(s.metadata["source"])}:' for s in answer["source_documents"]]))
    return answer
