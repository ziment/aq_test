from typing import Collection, Optional, Sequence, cast

import pytest
from pytest_mock import MockerFixture

from aqp.lib.config import Action as ConfigAction
from aqp.lib.config import FileMode
from aqp.lib.lexer import Lexer
from aqp.lib.parser import Parser, ParserError
from aqp.lib.tokens import Action, ErrorToken, Id, Mode, Path, Token


def create_parser(mocker: MockerFixture, tokens: list[Token]) -> Parser:
    tokens.append(None)  # type: ignore
    lexer = mocker.MagicMock()
    lexer.next_token.side_effect = tokens
    return Parser(lexer)


def test_parser_valid(mocker: MockerFixture) -> None:
    tokens = [
        Id(1),
        Path("/path/to/file, /another/path"),
        Mode("files"),
        Action("count"),
    ]

    parser = create_parser(mocker, tokens)
    result = parser.parse()

    assert 1 in result
    config = result[1]
    assert config.action_path == ["/path/to/file", "/another/path"]
    assert config.mode == FileMode.FILES
    assert config.action == ConfigAction.COUNT


def test_parser_missing_action(mocker: MockerFixture) -> None:
    tokens = [Id(2), Path("/some/path"), Mode("dir")]
    parser = create_parser(mocker, tokens)

    with pytest.raises(ParserError):
        parser.parse()


def test_parser_error_token(mocker: MockerFixture) -> None:
    tokens = [Id(4), ErrorToken("Error message")]
    parser = create_parser(mocker, tokens)

    with pytest.raises(ParserError):
        parser.parse()


def test_parser_invalid_mode(mocker: MockerFixture) -> None:
    tokens = [Id(5), Mode("invalid_mode"), Path("/valid/path"), Action("replace")]
    parser = create_parser(mocker, tokens)

    with pytest.raises(ParserError):
        parser.parse()


def test_parser_multiple_configs(mocker: MockerFixture) -> None:
    tokens = [
        Id(1),
        Path("/first/path"),
        Mode("files"),
        Action("count"),
        Id(2),
        Path("/second/path"),
        Mode("dir"),
        Action("replace"),
    ]
    parser = create_parser(mocker, tokens)
    result = parser.parse()

    assert 1 in result
    assert 2 in result
    assert result[1].action_path == ["/first/path"]
    assert result[1].mode == FileMode.FILES
    assert result[1].action == ConfigAction.COUNT
    assert result[2].action_path == ["/second/path"]
    assert result[2].mode == FileMode.DIR
    assert result[2].action == ConfigAction.REPLACE


def test_parser_empty(mocker: MockerFixture) -> None:
    tokens: list[Token] = []
    parser = create_parser(mocker, tokens)

    with pytest.raises(ParserError):
        parser.parse()


def test_parser_partial_config(mocker: MockerFixture) -> None:
    tokens = [Id(6), Path("/partial/path")]
    parser = create_parser(mocker, tokens)

    with pytest.raises(ParserError):
        parser.parse()
