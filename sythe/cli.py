import argparse
import sythe.fileio as fileio
import sythe.resources

def main():
    parser = argparse.ArgumentParser(description='A rule engine for resources')
    parser.add_argument('config', help='The config file containing rules')
    args = parser.parse_args()

    config_file_path = args.config
    rules = fileio.parse_rules_from_file(config_file_path)
    resources = sythe.resources.get_ec2_instances()
    for rule in rules:
        print("Applying rule: {}".format(rule))
        for resource in resources:
            rule.execute(resource)
