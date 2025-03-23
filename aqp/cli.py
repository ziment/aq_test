import argparse
import json
import pathlib

from aqp.lib.functions import execute_config, load


def main() -> None:
    parser = argparse.ArgumentParser(prog="aqp", description="Parses AQC config files")

    parser.add_argument("config_path", help="path to the AQC config file")
    parser.add_argument("id", type=int, help="configuration id to parse")
    parser.add_argument("-o", "--output", help="output file path")

    args = parser.parse_args()

    with open(args.config_path, "r") as file:
        config_dict = load(file)

    # todo add a func for loading a specific id
    config = config_dict[args.id]
    config.path_to_config = args.config_path

    json_dict = execute_config(config)

    if args.output is None:
        config_path = pathlib.Path(args.config_path)
        args.output = config_path.with_stem(config_path.stem + "_out").with_suffix(
            ".json"
        )

    with open(args.output, "w") as file:
        json.dump(json_dict, file, indent=4)


if __name__ == "__main__":
    main()
