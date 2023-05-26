import os
import sys

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.document_loaders import TextLoader

from talk_codebase.consts import EXCLUDE_DIRS, EXCLUDE_FILES, ALLOW_FILES


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
    docs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if any(exclude_dir in dirpath for exclude_dir in EXCLUDE_DIRS):
            continue
        if not filenames:
            continue
        for file in filenames:
            if any(file.endswith(allow_file) for allow_file in ALLOW_FILES) and not any(
                    file == exclude_file for exclude_file in EXCLUDE_FILES):
                try:
                    loader = TextLoader(os.path.join(dirpath, file), encoding='utf-8')
                    docs.extend(loader.load_and_split())
                except Exception as e:
                    print(f"Error loading file {file}: {e}")
    print(f"🤖 Loaded {len(docs)} documents")
    return docs
