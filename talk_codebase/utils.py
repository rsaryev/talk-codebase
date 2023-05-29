import glob
import os
import sys

import tiktoken
from git import Repo
from halo import Halo
from langchain import FAISS
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.document_loaders import TextLoader

from talk_codebase.consts import EXCLUDE_FILES, ALLOW_FILES


def get_repo(root_dir):
    try:
        return Repo(root_dir)
    except:
        return None


def is_ignored(path, root_dir):
    repo = get_repo(root_dir)
    if repo is None:
        return False
    if not os.path.exists(path):
        return False
    ignored = repo.ignored(path)
    return len(ignored) > 0


class StreamStdOut(StreamingStdOutCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        sys.stdout.write(token)
        sys.stdout.flush()

    def on_llm_start(self, serialized, prompts, **kwargs):
        sys.stdout.write("🤖 ")

    def on_llm_end(self, response, **kwargs):
        sys.stdout.write("\n")
        sys.stdout.flush()


def load_files(root_dir):
    spinners = Halo(text='Loading files', spinner='dots').start()
    docs = []
    for file_path in glob.glob(os.path.join(root_dir, '**/*'), recursive=True):
        if is_ignored(file_path, root_dir):
            continue
        if any(file_path.endswith(allow_file) for allow_file in ALLOW_FILES) and not any(
                file_path.endswith(exclude_file) for exclude_file in EXCLUDE_FILES):
            loader = TextLoader(file_path, encoding='utf-8')
            docs.extend(loader.load_and_split())
    spinners.succeed(f"Loaded {len(docs)} documents")
    return docs


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
