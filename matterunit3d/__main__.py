import argparse
import asyncio
import configparser
import json

from . import consts
from .application import application

def main():
    arg = argparse.ArgumentParser(description = consts.product_description)
    config = configparser.ConfigParser()
    arg.add_argument("config_path", help = consts.config_path_help)
    args = arg.parse_args()
    config.read(args.config_path)
    
    instance = application(config["unit3d"], config["matterbridge"])
    asyncio.run(instance.run())

if __name__ == "__main__":
    main()
