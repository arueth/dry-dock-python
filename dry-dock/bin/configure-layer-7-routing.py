import argparse

from config_loader import ConfigLoader
from logger import Logger
from ucp_api import UcpApi

config = None
logger = None
ucp_api = None


def configure_layer_7_routing():
    global config
    global ucp_api

    logger.info("Starting Layer 7 routing configuration")

    ucp_api = UcpApi(endpoint=config['ucp']['endpoint'],
                     username=config['ucp']['username'],
                     password=config['ucp']['password'],
                     use_ssl=config['ucp']['use_ssl'],
                     verify_ssl=config['ucp']['verify_ssl'],
                     logger=logger)

    ucp_api.login()

    logger.info("Retrieving Interlock configuration")

    get_response = ucp_api.get_interlock()
    get_response_json = get_response.json()

    logger.info("Interlock configuration retrieved")

    create_request = True
    if get_response_json['InterlockEnabled']:
        if get_response_json['HTTPPort'] == config['interlock']['http_port'] and \
                get_response_json['HTTPSPort'] == config['interlock']['https_port'] and \
                get_response_json['Arch'] == config['interlock']['architecture']:
            create_request = False

            logger.info("Interlock is already enabled and configured with the specified parameters")
            logger.debug(f"get_response_json: {get_response_json}, config['interlock']: {config['interlock']}")
        else:
            logger.info("Existing Interlock configuration does not match specified parameters, "
                        "removing existing Interlock configuration")
            logger.debug(f"get_response_json: {get_response_json}, config['interlock']: {config['interlock']}")

            delete_response = ucp_api.delete_interlock()

            logger.info("Existing Interlock configuration removed")

    if create_request:
        logger.info("Creating Interlock configured with the specified parameters")
        logger.debug(f"config['interlock']: {config['interlock']}")

        create_response = ucp_api.create_interlock(http_port=config['interlock']['http_port'],
                                                   https_port=config['interlock']['https_port'],
                                                   arch=config['interlock']['architecture'])
        logger.info("Interlock configuration created")

    ucp_api.logout()

    logger.info("Layer 7 routing configuration complete")

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf_dir", help="Configuration directory to use")
    args = parser.parse_args()

    config = ConfigLoader(args.conf_dir).load()
    logger = Logger(filename=__file__,
                    log_level=config['logging']['log_level'])

    configure_layer_7_routing()
