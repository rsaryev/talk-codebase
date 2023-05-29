## talk-codebase: tool for Chatting with Your Codebase. OpenAI, LlamaCpp, GPT4All

[![Node.js Package](https://github.com/rsaryev/talk-codebase/actions/workflows/python-publish.yml/badge.svg)](https://github.com/rsaryev/talk-codebase/actions/workflows/python-publish.yml)

<p align="center">
  <img src="https://github.com/rsaryev/talk-codebase/assets/70219513/b5d338f9-14a5-417b-9690-83f5cd66facf" width="800" alt="chat">
</p>

## Description

Talk-codebase is a powerful tool that allows you to converse with your codebase. It uses LLMs to answer your queries.

You can use [GPT4All](https://github.com/nomic-ai/gpt4all) for offline code processing without sharing your code with
third parties. Alternatively, you can use OpenAI if privacy is not a concern for you. You can switch between these two
options quickly and easily.

Project created for educational purposes. It is not recommended to use it in production.

## Installation

```bash
pip install talk-codebase
```

## Usage

Talk-codebase works only with files of popular programming languages and .txt files. All other files will be ignored.
If you want some files to be ignored, add them to .gitignore.

```bash
# Start chatting with your codebase
talk-codebase chat <directory>

# Configure or edit configuration ~/.config.yaml
talk-codebase configure

# Help
talk-codebase --help
```

## Requirements

- Python 3.9
- OpenAI API key [api-keys](https://platform.openai.com/account/api-keys)
- If you want to use GPT4All, you need to download the
  model [ggml-gpt4all-j-v1.3-groovy.bin](https://gpt4all.io/models/ggml-gpt4all-j-v1.3-groovy.bin) and specify the path
  to it in the configuration.

## Contributing

Contributions are always welcome!