## talk-codebase 
[![Node.js Package](https://github.com/rsaryev/talk-codebase/actions/workflows/python-publish.yml/badge.svg)](https://github.com/rsaryev/talk-codebase/actions/workflows/python-publish.yml)

* Talk-codebase is a tool that allows you to converse with your codebase using LLMs (Large Language Models) to answer your queries.
* It supports offline code processing using [GPT4All](https://github.com/nomic-ai/gpt4all) without sharing your code with third parties, or you can use OpenAI if privacy is not a concern for you.
* Talk-codebase is still under development, but it is a tool that can help you to improve your code. It is only recommended for educational purposes and not for production use.

<p align="center">
  <img src="https://github.com/rsaryev/talk-codebase/assets/70219513/b5d338f9-14a5-417b-9690-83f5cd66facf" width="800" alt="chat">
</p>

## Installation

To install talk-codebase, you need to have:

* Python 3.9
* An OpenAI API [api-keys](https://platform.openai.com/account/api-keys)
* (Optional) [GPT4All](https://gpt4all.io) model

```bash
# Install talk-codebase
pip install talk-codebase

# Configure talk-codebase
talk-codebase configure

# If you want some files to be ignored, add them to .gitignore.
# Once `talk-codebase` is installed, you can use it to chat with your codebase in the current directory by running the following command:
talk-codebase chat .
```

## Advanced configuration

You can also edit the configuration manually by editing the `~/.config.yaml` file.
If for some reason you cannot find the configuration file, just run the tool and at the very beginning it will output
the path to the configuration file.

```yaml
# The OpenAI API key. You can get it from https://beta.openai.com/account/api-keys
api_key: sk-xxx

# Configuration for chunking
chunk_overlap: 50
chunk_size: 500

# Configuration for sampling
k: 4
max_tokens: 1048

# Configuration for the LLM model
model_name: gpt-3.5-turbo
model_path: models/ggml-gpt4all-j-v1.3-groovy.bin
model_type: openai
```

## Supports the following extensions:

- [x] `.csv`
- [x] `.doc`
- [x] `.docx`
- [x] `.epub`
- [x] `.md`
- [x] `.pdf`
- [x] `.txt`
- [x] `popular programming languages`

## Contributing

* If you find a bug in talk-codebase, please report it on the project's issue tracker. When reporting a bug, please include as much information as possible, such as the steps to reproduce the bug, the expected behavior, and the actual behavior.
* If you have an idea for a new feature for Talk-codebase, please open an issue on the project's issue tracker. When suggesting a feature, please include a brief description of the feature, as well as any rationale for why the feature would be useful.
* You can contribute to talk-codebase by writing code. The project is always looking for help with improving the codebase, adding new features, and fixing bugs.
