import argparse
import base64
import collections
import re
import toml

from config_loader import ConfigLoader
from logger import Logger
from ucp_api import UcpApi

config = None
logger = None
ucp_api = None


#
# Reference: https://docs.docker.com/ee/ucp/admin/configure/external-auth/enable-ldap-config-file/
#

def configure_authentication_and_authorization():
    global config
    global ucp_api

    logger.info("Starting LDAP configuration")

    ucp_api = UcpApi(endpoint=config['ucp']['endpoint'],
                     username=config['ucp']['username'],
                     password=config['ucp']['password'],
                     use_ssl=config['ucp']['use_ssl'],
                     verify_ssl=config['ucp']['verify_ssl'],
                     logger=logger)

    ucp_api.login()

    current_config = find_current_config()
    new_config = create_new_ucp_config(current_config)

    ucp_agent_service = find_ucp_agent_service()
    update_ucp_agent_service_config(ucp_agent_service, new_config)

    ucp_api.logout()

    logger.info("LDAP configuration complete")

    return


def update(orig_dict, update_dict):
    for key, value in update_dict.items():
        if isinstance(value, collections.Mapping):
            orig_dict[key] = update(orig_dict.get(key, {}), value)
        else:
            orig_dict[key] = value

    return orig_dict


def find_current_config():
    logger.info("Finding latest com.docker.ucp.config")

    filter = '{"name":["com.docker.ucp.config"]}'

    configs = ucp_api.find_configs(filter)

    config_file = {}
    for config_entry in configs:
        config_file[config_entry['Spec']['Name']] = config_entry

    latest = natural_sort(config_file.keys())[-1]

    return config_file[latest]


def find_ucp_agent_service():
    logger.info("Finding latest ucp-agent service")

    ucp_agent_filter = '{"name":["ucp-agent"]}'

    services = ucp_api.find_services(ucp_agent_filter)

    ucp_agent_service = []
    for service_entry in services:
        if service_entry['Spec']['Name'] == 'ucp-agent':
            ucp_agent_service.append(service_entry)

    if len(ucp_agent_service) > 1:
        raise Exception(f"Multiple ucp-agent services found: {len(ucp_agent_service)}")

    return ucp_agent_service.pop()


def modify_config_data(current_config):
    logger.info("Modifying LDAP settings")

    prev_config_data = toml.loads(base64.b64decode(current_config['Spec']['Data']).decode('utf-8'))

    new_config_data = update(prev_config_data, config['auth'])
    new_config_data_toml = toml.dumps(new_config_data)
    new_config_data_toml_base64 = base64.b64encode(new_config_data_toml.encode('utf-8')).decode('utf-8')

    return new_config_data_toml_base64


def create_new_ucp_config(current_config):
    logger.info("Creating new com.docker.ucp.config")

    new_config_data = modify_config_data(current_config)

    current_config_number = current_config['Spec']['Name'].split('-')[1]
    new_config_number = int(current_config_number) + 1

    body = {'Name': f"com.docker.ucp.config-{new_config_number}",
            'Data': new_config_data}

    response_json = ucp_api.create_config(body)

    logger.debug(f"Created com.docker.ucp.config-{new_config_number} with ID {response_json['ID']}")

    new_config = ucp_api.get_config(response_json['ID'])

    return new_config


def update_ucp_agent_service_config(service, new_config):
    logger.info("Applying new com.docker.ucp.config to ucp-agent")

    configs = service['Spec']['TaskTemplate']['ContainerSpec']['Configs']
    config_index = next(
        (index for (index, entry) in enumerate(configs) if entry['ConfigName'].startswith('com.docker.ucp.config-')),
        None)

    body = service['Spec']
    body['TaskTemplate']['ContainerSpec']['Configs'][config_index]['ConfigID'] = new_config['ID']
    body['TaskTemplate']['ContainerSpec']['Configs'][config_index]['ConfigName'] = new_config['Spec']['Name']

    response_json = ucp_api.update_service(service, body)

    return response_json


def natural_sort(list_to_sort):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(list_to_sort, key=alphanum_key)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf_dir", help="Configuration directory to use")
    args = parser.parse_args()

    config = ConfigLoader(args.conf_dir).load()
    logger = Logger(filename=__file__,
                    log_level=config['logging']['log_level'])

    configure_authentication_and_authorization()
