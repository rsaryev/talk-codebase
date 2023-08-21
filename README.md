# talk-codebase

[![Node.js Package](https://github.com/rsaryev/talk-codebase/actions/workflows/python-publish.yml/badge.svg)](https://github.com/rsaryev/talk-codebase/actions/workflows/python-publish.yml)

Talk-codebase is a tool that allows you to converse with your codebase using Large Language Models (LLMs) to answer your
queries. It supports offline code processing using LlamaCpp and [GPT4All](https://github.com/nomic-ai/gpt4all) without
sharing your code with third parties, or you can use OpenAI if privacy is not a concern for you. Please note that
talk-codebase is still under development and is recommended for educational purposes, not for production use.

<p align="center">
  <img src="https://github.com/rsaryev/talk-codebase/assets/70219513/b5d338f9-14a5-417b-9690-83f5cd66facf" width="800" alt="chat">
</p>

## Installation

Requirement Python 3.8.1 or higher
Your project must be in a git repository

```bash
pip install talk-codebase
```

After installation, you can use it to chat with your codebase in the current directory by running the following command:

```bash
talk-codebase chat <path>
```

Select model type: Local or OpenAI

<img width="300" alt="select_type" src="https://github.com/rsaryev/talk-codebase/assets/70219513/05196fe5-78ff-44ff-8ca3-0313ccef572a">

OpenAI

If you use the OpenAI model, you need an OpenAI API key. You can get it from [here](https://beta.openai.com/). Then you
will be offered a choice of available models.

<img width="300" alt="select" src="https://github.com/rsaryev/talk-codebase/assets/70219513/889ad7c8-a489-4ce8-83af-148b7df09229">


Local

<img width="696" alt="Снимок экрана 2023-07-12 в 03 47 58" src="https://github.com/rsaryev/talk-codebase/assets/70219513/16988911-c605-4570-bfb4-4a34a03cd4a1">

If you want some files to be ignored, add them to .gitignore.

## Reset configuration

To reset the configuration, run the following command:

```bash
talk-codebase configure
```

## Advanced configuration

You can manually edit the configuration by editing the `~/.config.yaml` file. If you cannot find the configuration file,
run the tool and it will output the path to the configuration file at the very beginning.

## Supported Extensions

- [x] `.csv`
- [x] `.doc`
- [x] `.docx`
- [x] `.epub`
- [x] `.md`
- [x] `.pdf`
- [x] `.txt`
- [x] `popular programming languages`

## Contributing

* If you find a bug in talk-codebase, please report it on the project's issue tracker. When reporting a bug, please
  include as much information as possible, such as the steps to reproduce the bug, the expected behavior, and the actual
  behavior.
* If you have an idea for a new feature for Talk-codebase, please open an issue on the project's issue tracker. When
  suggesting a feature, please include a brief description of the feature, as well as any rationale for why the feature
  would be useful.
* You can contribute to talk-codebase by writing code. The project is always looking for help with improving the
  codebase, adding new features, and fixing bugs.
