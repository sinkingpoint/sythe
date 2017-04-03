import argparse
import fileio

def main():
    parser = argparse.ArgumentParser(description='A rule engine for resources')
    parser.add_argument('config', help='The config file containing rules')
    args = parser.parse_args()

    config_file_path = args.config
    rules = fileio.parse_rules_from_file(config_file_path)
