import os

import gpt4all
import openai
import anthropic
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


def api_key_is_invalid(api_key, api_type):
    if not api_key:
        return True
    try:
        if api_type == "openai":
            openai.api_key = api_key
            openai.Engine.list()
        elif api_type == "anthropic":
            client = anthropic.Anthropic(api_key=api_key)
            client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=5,
                messages=[
                    {"role": "user", "content": "Hello, world"}
            ])
    except Exception as e:
        print(e)
        return True
    return False


def get_gpt_models(openai):
    try:
        model_lst = openai.Model.list()
    except Exception:
        print("✘ Failed to retrieve model list")
        return []

    return [i['id'] for i in model_lst['data'] if 'gpt' in i['id']]


def configure_model_name_openai(config):
    api_key = config.get("openai_api_key")

    if config.get("model_type") != MODEL_TYPES["OPENAI"] or config.get("openai_model_name"):
        return

    openai.api_key = api_key
    gpt_models = get_gpt_models(openai)
    choices = [{"name": model, "value": model} for model in gpt_models]

    if not choices:
        print("ℹ No GPT models available")
        return

    model_name = questionary.select("🤖 Select model name:", choices).ask()

    if not model_name:
        print("✘ No model selected")
        return

    config["openai_model_name"] = model_name
    save_config(config)
    print("🤖 Model name saved!")

def configure_model_name_anthropic(config):
    api_key = config.get("anthropic_api_key")
    if config.get("model_type") != MODEL_TYPES["ANTHROPIC"] or config.get("anthropic_model_name"):
        return
    
    choices = [ {"name": "Claude 3 Opus", "value": "claude-3-opus-20240229"}, {"name": "Claude 3 Sonnet", "value": "claude-3-sonnet-20240229"}]

    model_name = questionary.select("🤖 Select model name:", choices).ask()

    if not model_name:
        print("✘ No model selected")
        return
    
    config["anthropic_model_name"] = model_name
    save_config(config)
    print("🤖 Model name saved!")

def remove_model_name_openai():
    config = get_config()
    config["openai_model_name"] = None
    save_config(config)


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


def remove_model_name_local():
    config = get_config()
    config["local_model_name"] = None
    save_config(config)


def get_and_validate_api_key(api_type):
    prompt = f"🤖 Enter your {api_type.capitalize()} API key: "
    api_key = input(prompt)
    while api_key_is_invalid(api_key, api_type):
        print("✘ Invalid API key")
        api_key = input(prompt)
    return api_key


def configure_api_keys(config):
    if config.get("model_type") == MODEL_TYPES["OPENAI"]:
        if api_key_is_invalid(config.get("openai_api_key"), "openai"):
            openai_api_key = get_and_validate_api_key("openai")
            config["openai_api_key"] = openai_api_key

    if config.get("model_type") == MODEL_TYPES["ANTHROPIC"]:
        if api_key_is_invalid(config.get("openai_api_key"), "openai"):
            openai_api_key = get_and_validate_api_key("openai")
            config["openai_api_key"] = openai_api_key
        if api_key_is_invalid(config.get("anthropic_api_key"), "anthropic"):
            anthropic_api_key = get_and_validate_api_key("anthropic")
            config["anthropic_api_key"] = anthropic_api_key

    save_config(config)


def remove_api_keys():
    config = get_config()
    config["openai_api_key"] = None
    config["anthropic_api_key"] = None
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
            {"name": "Anthropic", "value": MODEL_TYPES["ANTHROPIC"]},
        ]
    ).ask()
    config["model_type"] = model_type
    save_config(config)


CONFIGURE_STEPS = [
    configure_model_type,
    configure_api_keys,
    configure_model_name_openai,
    configure_model_name_anthropic,
    configure_model_name_local,
]