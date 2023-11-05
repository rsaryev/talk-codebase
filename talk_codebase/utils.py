import sys

import tiktoken
from git import Repo
from langchain.vectorstores import FAISS
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from talk_codebase.consts import LOADER_MAPPING, EXCLUDE_FILES


def get_repo():
    try:
        return Repo()
    except:
        return None


class StreamStdOut(StreamingStdOutCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        sys.stdout.write(token)
        sys.stdout.flush()

    def on_llm_start(self, serialized, prompts, **kwargs):
        sys.stdout.write("🤖 ")

    def on_llm_end(self, response, **kwargs):
        sys.stdout.write("\n")
        sys.stdout.flush()


def load_files():
    repo = get_repo()
    if repo is None:
        return []
    files = []
    tree = repo.tree()
    for blob in tree.traverse():
        path = blob.path
        if any(
                path.endswith(exclude_file) for exclude_file in EXCLUDE_FILES):
            continue
        for ext in LOADER_MAPPING:
            if path.endswith(ext):
                print('\r' + f'📂 Loading files: {path}')
                args = LOADER_MAPPING[ext]['args']
                loader = LOADER_MAPPING[ext]['loader'](path, *args)
                files.extend(loader.load())
    return files


def calculate_cost(texts, model_name):
    enc = tiktoken.encoding_for_model(model_name)
    all_text = ''.join([text.page_content for text in texts])
    tokens = enc.encode(all_text)
    token_count = len(tokens)
    cost = (token_count / 1000) * 0.0004
    return cost


def get_local_vector_store(embeddings, path):
    try:
        return FAISS.load_local(path, embeddings)
    except:
        return None
