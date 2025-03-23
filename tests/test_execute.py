import os
from itertools import product

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from aqp import (
    Action,
    Config,
    FileMode,
    execute_config,
)

file_modes = [FileMode.FILES, FileMode.DIR]

action_outputs = [
    (
        Action.STRING,
        {
            1: {1: "hello world", 2: "pytest is great"},
            2: {1: "this is a test", 2: "execute config"},
        },
    ),
    (
        Action.COUNT,
        {
            1: {1: "2", 2: "3"},
            2: {1: "4", 2: "2"},
        },
    ),
    (
        Action.REPLACE,
        {
            1: {1: "hello world", 2: "pytest is gre12t"},
            2: {1: "this is 11 test", 2: "exe32ute 32onfig"},
        },
    ),
]


@pytest.mark.parametrize(
    "mode, action, expected_output",
    (
        (mode, action, expected_output)
        for mode, (action, expected_output) in product(file_modes, action_outputs)
    ),
)
def test_execute_config(
    fs: FakeFilesystem, mode: FileMode, action: Action, expected_output: dict
) -> None:
    temp_dir = "/fake_dir"
    fs.create_dir(temp_dir)

    file1 = os.path.join(temp_dir, "file1.txt")
    file2 = os.path.join(temp_dir, "file2.txt")
    fs.create_file(file1, contents="hello world\nthis is a test\n")
    fs.create_file(file2, contents="pytest is great\nexecute config\n")

    action_path = [file1, file2] if mode == FileMode.FILES else [temp_dir]

    config = Config(
        config_id=1,
        path_to_config="/path/to/config",
        mode=mode,
        action=action,
        action_path=action_path,
    )

    result = execute_config(config)

    assert result["out"] == expected_output
    assert result["configurationId"] == config.config_id
    assert result["configFile"] == config.path_to_config
    assert result["configurationData"]["mode"] == str(config.mode)
    assert result["configurationData"]["path"] == ", ".join(action_path)
