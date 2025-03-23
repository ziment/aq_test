# AQC Parser

A command-line application for executing AQC (Aquarius Config) files, along with a library that provides a lexer and parser for the format. The project is fully type annotated. Type annotations are checked with [mypy](https://github.com/python/mypy).

## AQC Specification

An AQC file follows this structure:

```text
#id: <configuration_id>
#mode: <dir | files>
#path: <comma-separated file paths | directory path>
#action: <string | count | replace>
```

Each file can contain multiple configurations.

## Installation

Since this project is not published on PyPI, you will need to clone the repository to install it.

```bash
git clone <repo_url>
cd <repo_directory>
pip install .
```

## Usage

After installation, the `aqp` command should be available in your PATH. To see available options, run:

```bash
aqp -h
```

## Running Tests

To run tests, first install the development dependencies:

```bash
pip install -r dev-requirements.txt
```

Ensure the project is installed for proper imports in tests:

```bash
pip install .
```

For an editable install, use:

```bash
pip install -e .
```

After installing, execute tests from the root directory:

```bash
pytest
```
