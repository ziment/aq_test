import pytest

import aqp.lib.tokens as tokens
from aqp.lib.lexer import Lexer
from aqp.lib.reader import StringReader


def get_tokens(input_text: str) -> list[tokens.Token]:
    reader = StringReader(input_text)
    lex = Lexer(reader)
    return lex.tokenise()


def test_id_token_numeric() -> None:
    input_text = "#123"
    toks = get_tokens(input_text)

    assert len(toks) == 1
    assert isinstance(toks[0], tokens.Id)
    assert toks[0].value == 123


def test_id_token_with_prefix() -> None:
    # The lexer supports an optional "id:" prefix
    input_text = "#id: 456"
    toks = get_tokens(input_text)

    assert len(toks) == 1
    assert isinstance(toks[0], tokens.Id)
    assert toks[0].value == 456


def test_mode_token() -> None:
    input_text = "#mode:    dir"
    toks = get_tokens(input_text)

    assert len(toks) == 1
    assert isinstance(toks[0], tokens.Mode)
    assert toks[0].value == "dir"


def test_path_token() -> None:
    input_text = "#path: /some/path  "
    toks = get_tokens(input_text)

    assert len(toks) == 1
    assert isinstance(toks[0], tokens.Path)
    assert toks[0].value == "/some/path"


def test_action_token() -> None:
    input_text = "#action:   string   \n"
    toks = get_tokens(input_text)

    assert len(toks) == 1
    assert isinstance(toks[0], tokens.Action)
    assert toks[0].value == "string"


def test_multiple_tokens() -> None:
    input_text = "#1\n#mode: dir\n#path: /some/path  \n#action: string\n"
    toks = get_tokens(input_text)

    assert len(toks) == 4

    assert isinstance(toks[0], tokens.Id)
    assert toks[0].value == 1

    assert isinstance(toks[1], tokens.Mode)
    assert toks[1].value == "dir"

    assert isinstance(toks[2], tokens.Path)
    assert toks[2].value == "/some/path"

    assert isinstance(toks[3], tokens.Action)
    assert toks[3].value == "string"


def test_multiple_tokens_signle_line() -> None:
    # Test multiple tokens in one input.
    input_text = "#1#mode: dir#path: /some/path  #action: string"
    toks = get_tokens(input_text)

    assert len(toks) == 4

    assert isinstance(toks[0], tokens.Id)
    assert toks[0].value == 1

    assert isinstance(toks[1], tokens.Mode)
    assert toks[1].value == "dir"

    assert isinstance(toks[2], tokens.Path)
    assert toks[2].value == "/some/path"

    assert isinstance(toks[3], tokens.Action)
    assert toks[3].value == "string"


def test_missing_statement_marker() -> None:
    input_text = "123"
    toks = get_tokens(input_text)

    assert len(toks) == 1
    assert isinstance(toks[0], tokens.ErrorToken)


def test_incomplete_token() -> None:
    input_text = "#"
    toks = get_tokens(input_text)

    assert len(toks) == 1
    assert isinstance(toks[0], tokens.ErrorToken)


def test_escaped_string() -> None:
    input_text = "#path: /some/file\\#"
    toks = get_tokens(input_text)

    assert len(toks) == 1
    assert isinstance(toks[0], tokens.Path)
    assert toks[0].value == "/some/file#"


def test_escaped_slash() -> None:
    input_text = "#path: /some/file\\\\#mode: dir"
    toks = get_tokens(input_text)

    assert len(toks) == 2
    assert isinstance(toks[0], tokens.Path)
    assert toks[0].value == "/some/file\\"

    assert isinstance(toks[1], tokens.Mode)
    assert toks[1].value == "dir"
