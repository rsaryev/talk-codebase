# talk-codebase is a powerful tool for chatting with your codebase

[![Node.js Package](https://github.com/rsaryev/talk-codebase/actions/workflows/python-publish.yml/badge.svg)](https://github.com/rsaryev/talk-codebase/actions/workflows/python-publish.yml)

<p align="center">
  <img src="https://github.com/rsaryev/talk-codebase/assets/70219513/b5d338f9-14a5-417b-9690-83f5cd66facf" width="800" alt="chat">
</p>

## Installation

```bash
pip install talk-codebase
```

## Usage

talk-codebase works only with files of popular programming languages and additionally with .txt files. All other files
will be ignored.

```bash
# Start chatting with your codebase
talk-codebase chat <directory>

# Configure
talk-codebase configure

# Help
talk-codebase --help
```

## Requirements

- Python 3.9
- OpenAI API key [api-keys](https://platform.openai.com/account/api-keys)