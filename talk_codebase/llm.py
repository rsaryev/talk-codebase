from langchain.callbacks.manager import CallbackManager
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from talk_codebase.utils import StreamStdOut


def send_question(question, retriever, openai_api_key, model_name):
    model = ChatOpenAI(model_name=model_name, openai_api_key=openai_api_key, streaming=True,
                       callback_manager=CallbackManager([StreamStdOut()]))
    qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever)
    answer = qa({"question": question, "chat_history": []})
    return answer
