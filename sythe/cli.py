import argparse

def main():
    parser = argparse.ArgumentParser(description='A rule engine for resources')
    parser.add_argument('config', help='The config file containing rules')
    args = parser.parse_args()

