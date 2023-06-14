## talk-codebase: Tool for chatting with your codebase and docs using OpenAI, LlamaCpp, and GPT-4-All

[![Node.js Package](https://github.com/rsaryev/talk-codebase/actions/workflows/python-publish.yml/badge.svg)](https://github.com/rsaryev/talk-codebase/actions/workflows/python-publish.yml)

<p align="center">
  <img src="https://github.com/rsaryev/talk-codebase/assets/70219513/b5d338f9-14a5-417b-9690-83f5cd66facf" width="800" alt="chat">
</p>

## Description

Talk-codebase is a tool that allows you to converse with your codebase using LLMs to answer your queries. It supports
offline code processing using [GPT4All](https://github.com/nomic-ai/gpt4all) without sharing your code with third
parties, or you can use OpenAI if privacy is not a concern for you. It is only recommended for educational purposes and
not for production use.

## Installation

To install `talk-codebase`, you need to have Python 3.9 and an OpenAI API
key [api-keys](https://platform.openai.com/account/api-keys).
Additionally, if you want to use the GPT4All model, you need to download
the [ggml-gpt4all-j-v1.3-groovy.bin](https://gpt4all.io/models/ggml-gpt4all-j-v1.3-groovy.bin) model. If you prefer a
different model, you can download it from [GPT4All](https://gpt4all.io) and configure path to it in the configuration
and specify its
path in the configuration. If you want some files to be ignored, add them to .gitignore.

To install `talk-codebase`, run the following command in your terminal:

```bash
pip install talk-codebase
```

Once `talk-codebase` is installed, you can use it to chat with your codebase by running the following command:

```bash
talk-codebase chat <path-to-your-codebase>
```

If you need to configure or edit the configuration, you can run:

```bash
talk-codebase configure
```

You can also edit the configuration manually by editing the `~/.config.yaml` file.
If for some reason you cannot find the configuration file, just run the tool and at the very beginning it will output
the path to the configuration file.

```yaml
# The OpenAI API key. You can get it from https://beta.openai.com/account/api-keys
api_key: sk-xxx
# maximum overlap between chunks. It can be nice to have some overlap to maintain some continuity between chunks
chunk_overlap: "50"
# maximum size of a chunk
chunk_size: "500"
# number of samples to generate for each prompt.
k: "4"
# maximum tokens for the LLMs
max_tokens: "1048"
# token limit for the LLM model only OpenAI
model_name: gpt-3.5-turbo
# path to the llm file on disk.
model_path: models/ggml-gpt4all-j-v1.3-groovy.bin
# type of the LLM model. It can be either local or openai
model_type: openai
```

## The supported extensions:

- [x] `.csv`
- [x] `.doc`
- [x] `.docx`
- [x] `.epub`
- [x] `.md`
- [x] `.pdf`
- [x] `.txt`
- [x] `popular programming languages`

## Running from Source

1. Clone the repository:

```bash
git clone https://github.com/rsaryev/talk-codebase.git
cd talk-codebase
```

2. Create a Python virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the dependencies:

If you use Poetry, you can install the dependencies from the `pyproject.toml` and `poetry.lock` files with:

```bash
poetry install
```

Alternatively, if you use pip, you can install from the `requirements.txt` file with:

```bash
pip install -r requirements.txt
```

4. You can now run the tool from source using Python:

```bash
python talk_codebase/cli.py <command>
```

Replace `<command>` with any of the commands described in the project's usage instructions (e.g., `chat`, `configure`).

## Contributing

Contributions to the `talk-codebase` project are welcome. Here's how to get started:

1. Fork the repository and create a new branch for your work.

2. Make your changes or additions to the codebase. Be sure to follow the existing code style.

3. If you've added code that should be tested, add tests.

4. Ensure all tests pass.

5. Submit a pull request with your changes. Please include a detailed description of your changes in the pull request.

Before contributing, it may be a good idea to open an issue to discuss the changes you wish to make. This allows the maintainers to provide guidance and ensure your changes align with the project's direction.

Please note that this project is released with a [Contributor Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/). By participating in this project, you agree to abide by its terms.
