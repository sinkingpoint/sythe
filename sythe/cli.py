import argparse
import sythe.fileio as fileio
import sythe.resources as resources

def main():
    parser = argparse.ArgumentParser(description='A rule engine for resources')
    parser.add_argument('config', help='The config file containing rules')
    args = parser.parse_args()

    config_file_path = args.config
    rules = fileio.parse_rules_from_file(config_file_path)
    for rule in rules:
        print("Applying rule: {}".format(rule))
        affected_resources = resources.filter_resources(resources.get_ec2_instances(), rule.condition)
        print("Would affect: {}".format(affected_resources))
