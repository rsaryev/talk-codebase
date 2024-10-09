import sys
import subprocess
import requests
import shutil

import fire

from talk_codebase.config import CONFIGURE_STEPS, save_config, get_config, config_path, configure, remove_configuration
from talk_codebase.consts import DEFAULT_CONFIG, MODEL_TYPES
from talk_codebase.llm import factory_llm
from talk_codebase.utils import get_repo


def check_python_version():
    if sys.version_info < (3, 8, 1):
        print("🤖 Please use Python 3.8.1 or higher")
        sys.exit(1)


def check_ollama_installed():
    return shutil.which("ollama") is not None


def check_ollama_running():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except requests.RequestException:
        return False


def update_config(config):
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
    return config


def chat_loop(llm):
    print("\n🤖 I'm here to help you understand the codebase. Feel free to ask any questions!")
    while True:
        query = input("👉 ").lower().strip()
        if not query:
            print("🤖 Please enter a query")
            continue
        if query in ('exit', 'quit'):
            break
        print("\n🤖 Analyzing the codebase to provide the best possible answer...")
        llm.send_query(query)


def chat():
    config = get_config()
    if not config.get("embedding_model_type") or not config.get("chat_model_type"):
        print("🤖 Configuration not found. Running configuration process...")
        configure(False)
        config = get_config()

    repo = get_repo()
    if not repo:
        print("🤖 Git repository not found")
        sys.exit(1)

    if config.get("embedding_model_type") != config.get("chat_model_type"):
        print("Error: Embedding and chat model types must be the same.")
        print("Please run 'talk-codebase configure' to set up your configuration correctly.")
        sys.exit(1)

    model_type = config.get("embedding_model_type")

    if model_type in [MODEL_TYPES["OPENAI"], MODEL_TYPES["OPENAI_COMPATIBLE"]]:
        if not config.get("openai_compatible_api_key"):
            print("Error: API key is missing. Please run 'talk-codebase configure' to set up your API key.")
            sys.exit(1)
        
        if model_type == MODEL_TYPES["OPENAI_COMPATIBLE"] and not config.get("openai_compatible_endpoint"):
            print("Error: API endpoint is missing for OpenAI-compatible setup. Please run 'talk-codebase configure' to set up your API endpoint.")
            sys.exit(1)

    elif model_type == MODEL_TYPES["OLLAMA"]:
        if not check_ollama_installed():
            print("⚠️ Ollama is not found in PATH. Please ensure Ollama is installed and added to your system PATH.")
            print("You can download Ollama from: https://ollama.ai/download")
            sys.exit(1)

        if not check_ollama_running():
            print("⚠️ Ollama is installed but not running. Please start Ollama with 'ollama serve' command.")
            sys.exit(1)

    try:
        llm = factory_llm(repo.working_dir, config)
        chat_loop(llm)
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please run 'talk-codebase configure' to set up your configuration correctly.")
        sys.exit(1)


def main():
    check_python_version()
    print(f"🤖 Config path: {config_path}:")
    try:
        fire.Fire({
            "chat": chat,
            "configure": lambda: configure(True)
        })
    except KeyboardInterrupt:
        print("\n🤖 Bye!")
    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
