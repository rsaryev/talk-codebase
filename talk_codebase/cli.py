import sys

import fire

from talk_codebase.config import CONFIGURE_STEPS, save_config, get_config, config_path, remove_api_key, \
    remove_model_type, remove_model_name_local
from talk_codebase.consts import DEFAULT_CONFIG
from talk_codebase.llm import factory_llm
from talk_codebase.utils import get_repo


def check_python_version():
    if sys.version_info < (3, 8, 1):
        print("🤖 Please use Python 3.8.1 or higher")
        sys.exit(1)


def update_config(config):
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
    return config


def configure(reset=True):
    if reset:
        remove_api_key()
        remove_model_type()
        remove_model_name_local()
    config = get_config()
    config = update_config(config)
    for step in CONFIGURE_STEPS:
        step(config)
    save_config(config)


def chat_loop(llm):
    while True:
        query = input("👉 ").lower().strip()
        if not query:
            print("🤖 Please enter a query")
            continue
        if query in ('exit', 'quit'):
            break
        llm.send_query(query)


def chat():
    configure(False)
    config = get_config()
    repo = get_repo()
    if not repo:
        print("🤖 Git repository not found")
        sys.exit(1)
    llm = factory_llm(repo.working_dir, config)
    chat_loop(llm)


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
