import os
import sys

from git import Repo
from halo import Halo
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.document_loaders import TextLoader

from talk_codebase.consts import EXCLUDE_DIRS, EXCLUDE_FILES, ALLOW_FILES


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
    spinners = Halo(text='Loading files', spinner='dots')
    docs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if is_ignored(dirpath, root_dir):
            continue
        if any(exclude_dir in dirpath for exclude_dir in EXCLUDE_DIRS):
            continue
        if not filenames:
            continue
        for file in filenames:
            if is_ignored(os.path.join(dirpath, file), root_dir):
                continue
            if any(file.endswith(allow_file) for allow_file in ALLOW_FILES) and not any(
                    file == exclude_file for exclude_file in EXCLUDE_FILES):
                try:
                    loader = TextLoader(os.path.join(dirpath, file), encoding='utf-8')
                    docs.extend(loader.load_and_split())
                except Exception as e:
                    print(f"Error loading file {file}: {e}")
    spinners.succeed(f"Loaded {len(docs)} documents")
    return docs
