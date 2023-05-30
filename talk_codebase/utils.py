import glob
import multiprocessing
import os
import sys

import tiktoken
from git import Repo
from halo import Halo
from langchain import FAISS
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from talk_codebase.consts import LOADER_MAPPING, EXCLUDE_FILES


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


@Halo(text='📂 Loading files', spinner='dots')
def load_files(root_dir):
    num_cpus = multiprocessing.cpu_count()
    loaded_files = []
    with multiprocessing.Pool(num_cpus) as pool:
        futures = []
        for file_path in glob.glob(os.path.join(root_dir, '**/*'), recursive=True):
            if is_ignored(file_path, root_dir):
                continue
            if any(
                    file_path.endswith(exclude_file) for exclude_file in EXCLUDE_FILES):
                continue
            for ext in LOADER_MAPPING:
                if file_path.endswith(ext):
                    loader = LOADER_MAPPING[ext]['loader']
                    args = LOADER_MAPPING[ext]['args']
                    load = loader(file_path, **args)
                    futures.append(pool.apply_async(load.load_and_split))
                    loaded_files.append(file_path)
        docs = []
        for future in futures:
            docs.extend(future.get())

    print('\n' + '\n'.join([f'📄 {os.path.abspath(file_path)}:' for file_path in loaded_files]))
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
