import os

import gpt4all
import questionary
import yaml

from talk_codebase.consts import MODEL_TYPES

config_path = os.path.join(os.path.expanduser("~"), ".talk_codebase_config.yaml")


def get_config():
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    return config


def save_config(config):
    with open(config_path, "w") as f:
        yaml.dump(config, f)


def configure_model_name_local(config):
    if config.get("model_type") != MODEL_TYPES["LOCAL"] or config.get("local_model_name"):
        return

    list_models = gpt4all.GPT4All.list_models()

    def get_model_info(model):
        return (
            f"{model['name']} "
            f"| {model['filename']} "
            f"| {model['filesize']} "
            f"| {model['parameters']} "
            f"| {model['quant']} "
            f"| {model['type']}"
        )

    choices = [
        {"name": get_model_info(model), "value": model['filename']} for model in list_models
    ]

    model_name = questionary.select("🤖 Select model name:", choices).ask()
    config["local_model_name"] = model_name
    save_config(config)
    print("🤖 Model name saved!")


def configure_api_key(config):
    if config.get("model_type") != MODEL_TYPES["OPENAI"] or config.get("api_key"):
        return
    api_key = input("🤖 Enter your OpenAI API key: ")
    config["api_key"] = api_key
    save_config(config)
    print("🤖 API key saved!")


def remove_api_key():
    config = get_config()
    config["api_key"] = None
    save_config(config)


def remove_model_type():
    config = get_config()
    config["model_type"] = None
    save_config(config)


def configure_model_type(config):
    if config.get("model_type"):
        return

    model_type = questionary.select(
        "🤖 Select model type:",
        choices=[
            {"name": "Local", "value": MODEL_TYPES["LOCAL"]},
            {"name": "OpenAI", "value": MODEL_TYPES["OPENAI"]},
        ]
    ).ask()
    config["model_type"] = model_type
    save_config(config)
    print("🤖 Model type saved!")


CONFIGURE_STEPS = [
    configure_model_type,
    configure_model_name_local,
    configure_api_key,
]
