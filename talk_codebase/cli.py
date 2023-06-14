import os

import fire
import questionary
import yaml

from talk_codebase.LLM import factory_llm
from talk_codebase.consts import DEFAULT_CONFIG

config_path = os.path.join(os.path.expanduser("~"), ".talk_codebase_config.yaml")


def get_config():
    print(f"🤖 Loading config from {config_path}:")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    return config


def save_config(config):
    home_dir = os.path.expanduser("~")
    with open(config_path, "w") as f:
        yaml.dump(config, f)


def configure():
    config = get_config()
    model_type = questionary.select(
        "🤖 Select model type:",
        choices=[
            {"name": "OpenAI", "value": "openai"},
            {"name": "Local", "value": "local"},
        ]
    ).ask()
    config["model_type"] = model_type
    if model_type == "openai":
        api_key = input("🤖 Enter your OpenAI API key: ")
        model_name = input(f"🤖 Enter your model name (default: {DEFAULT_CONFIG['model_name']}): ")
        config["model_name"] = model_name if model_name else DEFAULT_CONFIG["model_name"]
        config["api_key"] = api_key
    elif model_type == "local":
        model_path = input(f"🤖 Enter your model path: (default: {DEFAULT_CONFIG['model_path']}) ")
        config["model_path"] = model_path if model_path else DEFAULT_CONFIG["model_path"]
    save_config(config)
    print("🤖 Configuration saved!")


def loop(llm):
    while True:
        query = input("👉 ").lower().strip()
        if not query:
            print("🤖 Please enter a query")
            continue
        if query in ('exit', 'quit'):
            break
        llm.send_query(query)


def validate_config(config):
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
    if config.get("model_type") == "openai":
        api_key = config.get("api_key")
        if not api_key:
            print("🤖 Please configure your API key. Use talk-codebase configure")
            exit(0)
    elif config.get("model_type") == "local":
        model_path = config.get("model_path")
        if not model_path:
            print("🤖 Please configure your model path. Use talk-codebase configure")
            exit(0)
    save_config(config)
    return config


def chat(root_dir):
    config = validate_config(get_config())
    llm = factory_llm(root_dir, config)
    loop(llm)


def main():
    try:
        fire.Fire({
            "chat": chat,
            "configure": configure
        })
    except KeyboardInterrupt:
        print("\n🤖 Bye!")
    except Exception as e:
        if str(e) == "<empty message>":
            print("🤖 Please configure your API key. Use talk-codebase configure")
        else:
            raise e


if __name__ == "__main__":
    main()
