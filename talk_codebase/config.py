import os
import questionary
import yaml
import requests

from talk_codebase.consts import MODEL_TYPES

config_path = os.path.join(os.path.expanduser("~"), ".talk_codebase_config.yaml")

def get_config():
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    
    # Set default value for frequency_penalty if not present
    if 'frequency_penalty' not in config:
        config['frequency_penalty'] = 0.0
    
    return config

def save_config(config):
    with open(config_path, "w") as f:
        yaml.dump(config, f)

def get_ollama_models(purpose):
    try:
        if purpose == "chat":
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json()
                return [model['name'] for model in models['models']]
        elif purpose == "embedding":
            # For now, we'll use a predefined list of Ollama embedding models
            return ["nomic-embed-text", "all-MiniLM-L6-v2"]
    except requests.RequestException:
        print(f"Error: Unable to fetch Ollama {purpose} models. Make sure Ollama is running.")
    return []

def configure_api_key(config, model_type):
    if model_type in [MODEL_TYPES["OPENAI"], MODEL_TYPES["OPENAI_COMPATIBLE"]]:
        api_key = questionary.password("🤖 Enter your API key:").ask()
        config["openai_compatible_api_key"] = api_key
        save_config(config)
        print("API key saved successfully.")

def configure_api_endpoint(config, purpose):
    if config.get(f"{purpose}_model_type") == MODEL_TYPES["OPENAI_COMPATIBLE"]:
        endpoint = questionary.text("🤖 Enter the API endpoint:").ask()
        config["openai_compatible_endpoint"] = endpoint
        save_config(config)
        print(f"API endpoint for {purpose} set to: {endpoint}")
    elif config.get(f"{purpose}_model_type") == MODEL_TYPES["OLLAMA"]:
        if purpose == "chat":
            config[f"{purpose}_api_endpoint"] = "http://localhost:11434/api/generate"
        elif purpose == "embedding":
            config[f"{purpose}_api_endpoint"] = "http://localhost:11434/api/embeddings"
        save_config(config)
        print(f"Ollama API endpoint for {purpose} set to: {config[f'{purpose}_api_endpoint']}")

def configure_model_name(config, purpose):
    model_type = config.get(f"{purpose}_model_type")
    
    if model_type == MODEL_TYPES["OLLAMA"]:
        ollama_models = get_ollama_models(purpose)
        if not ollama_models:
            print(f"❌ No Ollama models found for {purpose}. Please make sure Ollama is running and you have pulled some models.")
            return
        choices = [{"name": model, "value": model} for model in ollama_models]
        model_name = questionary.select(f"🤖 Select Ollama model for {purpose}:", choices).ask()
    elif model_type in [MODEL_TYPES["OPENAI"], MODEL_TYPES["OPENAI_COMPATIBLE"]]:
        prompt = f"🤖 Enter the model name for {purpose} (e.g., text-embedding-ada-002 for embedding, gpt-3.5-turbo for chat):"
        model_name = questionary.text(prompt).ask()
    else:
        print(f"Invalid model type: {model_type}")
        return

    config[f"{purpose}_model_name"] = model_name
    save_config(config)
    print(f"🤖 {purpose.capitalize()} model name saved!")

def configure_section(config, purpose):
    choices = [
        {"name": "OpenAI", "value": MODEL_TYPES["OPENAI"]},
        {"name": "OpenAI Compatible", "value": MODEL_TYPES["OPENAI_COMPATIBLE"]},
        {"name": "Ollama (Local)", "value": MODEL_TYPES["OLLAMA"]}
    ]

    model_type = questionary.select(
        f"🤖 Select model type for {purpose}:",
        choices=choices
    ).ask()

    config[f"{purpose}_model_type"] = model_type
    save_config(config)

    if model_type in [MODEL_TYPES["OPENAI"], MODEL_TYPES["OPENAI_COMPATIBLE"]]:
        configure_api_key(config, model_type)
        if model_type == MODEL_TYPES["OPENAI_COMPATIBLE"]:
            configure_api_endpoint(config, purpose)
    elif model_type == MODEL_TYPES["OLLAMA"]:
        configure_api_endpoint(config, purpose)

    configure_model_name(config, purpose)

def configure_embedding():
    config = get_config()
    configure_section(config, "embedding")

def configure_chat():
    config = get_config()
    configure_section(config, "chat")
    
    # Add configuration for frequency_penalty
    frequency_penalty = questionary.text(
        "🤖 Enter the frequency penalty (default is 0.0, range is -2.0 to 2.0):",
        default="0.0"
    ).ask()
    try:
        frequency_penalty = float(frequency_penalty)
        if -2.0 <= frequency_penalty <= 2.0:
            config["frequency_penalty"] = frequency_penalty
            save_config(config)
            print(f"Frequency penalty set to: {frequency_penalty}")
        else:
            print("Invalid frequency penalty value. Using default (0.0).")
    except ValueError:
        print("Invalid input. Using default frequency penalty (0.0).")

def remove_configuration():
    config = get_config()
    keys_to_remove = [
        "embedding_model_type", "embedding_model_name",
        "chat_model_type", "chat_model_name",
        "openai_compatible_api_key", "openai_compatible_endpoint",
        "embedding_api_endpoint", "chat_api_endpoint",
        "frequency_penalty"
    ]
    for key in keys_to_remove:
        config.pop(key, None)
    save_config(config)
    print("Configuration removed successfully.")

CONFIGURE_STEPS = [
    configure_embedding,
    configure_chat,
]

def configure(reset=False):
    if reset:
        remove_configuration()
    
    config = get_config()
    for step in CONFIGURE_STEPS:
        step()
    
    print("Configuration completed successfully.")
