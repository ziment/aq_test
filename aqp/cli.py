import argparse

from src.parser import loads


def main() -> None:
    parser = argparse.ArgumentParser(prog="aqp", description="Parses AQP config files")

    parser.add_argument("path", help="path to the AQP config file")
    parser.add_argument("id", help="configuration id to parse")

    args = parser.parse_args()

    print(args.path)
    print(args.id)


if __name__ == "__main__":
    main()
