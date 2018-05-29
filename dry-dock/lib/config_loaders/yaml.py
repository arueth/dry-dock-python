import yaml

from os import environ
from re import compile
from string import Template

secret_pattern = compile(r'^<%= SECRET\((.*)\) %>(.*)$')
yaml.add_implicit_resolver("!secret_loader", secret_pattern)


def secret_loader(loader, node):
    entry = loader.construct_scalar(node)
    secret_file = entry[entry.find("(") + 1:entry.find(")")]

    secret = open(secret_file).read()

    return secret.strip()


yaml.add_constructor('!secret_loader', secret_loader)


class Yaml:
    def __init__(self, file):
        self.file = file

        return

    def load(self):
        config_template = Template(open(self.file).read())
        config = config_template.substitute(environ)

        return yaml.load(config)
