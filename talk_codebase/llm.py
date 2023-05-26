import os

from langchain import FAISS
from langchain.callbacks.manager import CallbackManager
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter

from talk_codebase.utils import StreamStdOut, load_files


def create_vector_store(root_dir, openai_api_key):
    docs = load_files(root_dir)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    db = FAISS.from_documents(texts, embeddings)

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
