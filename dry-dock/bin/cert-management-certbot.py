import argparse
import glob
import os

from config_loader import ConfigLoader
from dtr_api import DtrApi
from execute_command import ExecuteCommand
from logger import Logger
from ucp_api import UcpApi

config = None
dtr_api = None
logger = None
path = os.path.dirname(os.path.realpath(__file__))
ucp_api = None


def apply_dtr_certs():
    global dtr_api

    dtr_api = DtrApi(endpoint=config['dtr']['endpoint'],
                     username=config['dtr']['credentials']['username'],
                     password=config['dtr']['credentials']['password'],
                     use_ssl=config['dtr']['use_ssl'],
                     verify_ssl=False,
                     logger=logger)

    dtr_api.create_token('cert-management')

    cert_directory = sorted(
        glob.glob(f"{path}/../certs/certbot/config/live/{config['dtr']['ssl_certificate']['domain_name']}**"),
        reverse=True)[0]

    body = {"dtrHost": config['dtr']['ssl_certificate']['domain_name'],
            "webTLSCA": open(f"{cert_directory}/chain.pem").read(),
            "webTLSKey": open(f"{cert_directory}/privkey.pem").read(),
            "webTLSCert": open(f"{cert_directory}/fullchain.pem").read()}

    response = dtr_api.update_certs(body)

    dtr_api.delete_token()

    return response


def apply_ucp_certs():
    global ucp_api

    ucp_api = UcpApi(config['ucp']['endpoint'],
                     config['ucp']['username'],
                     config['ucp']['password'],
                     config['ucp']['use_ssl'],
                     verify_ssl=False,
                     logger=logger)

    ucp_api.login()

    cert_directory = sorted(
        glob.glob(f"{path}/../certs/certbot/config/live/{config['ucp']['ssl_certificate']['domain_name']}**"),
        reverse=True)[0]

    body = {"ca": open(f"{cert_directory}/chain.pem").read(),
            "key": open(f"{cert_directory}/privkey.pem").read(),
            "cert": open(f"{cert_directory}/fullchain.pem").read()}

    response = ucp_api.update_certs(body)

    ucp_api.logout()

    return response


def generate_dtr_certs():
    environment = {
        'AWS_ACCESS_KEY_ID': config['certbot']['aws']['access_key_id'],
        'AWS_SECRET_ACCESS_KEY': config['certbot']['aws']['secret_access_key']
    }

    command = ["certbot", "certonly",
               "--authenticator", "dns-route53",
               "--email", config['certbot']['email'],
               "--agree-tos",
               "--no-eff-email",
               "--keep-until-expiring",
               "--dns-route53",
               "--config-dir", f'{path}/../certs/certbot/config',
               "--logs-dir", f"{path}/../certs/certbot/log",
               "--work-dir", f"{path}/../certs/certbot/work",
               "-d", config['dtr']['ssl_certificate']['domain_name']]

    if 'sans' in config['dtr']['ssl_certificate'] and config['dtr']['ssl_certificate']['sans']:
        for san in config['dtr']['ssl_certificate']['sans']:
            command.append("-d")
            command.append(san)

    logger.debug(f"Preparing to execute command: {' '.join(command)}")

    execution = ExecuteCommand(command, environment)

    logger.debug(f"Execution results: {logger.prepare_execution(execution)}")

    if execution.result.returncode != 0:
        logger.error(f"Execution failed: {logger.prepare_execution(execution)}")
        raise Exception("Execution failed!")

    if 'Certificate not yet due for renewal; no action taken.' in execution.result.stdout:
        logger.info("DTR certificates are not yet due for renewal")
        return False

    return True


def generate_ucp_certs():
    environment = {
        'AWS_ACCESS_KEY_ID': config['certbot']['aws']['access_key_id'],
        'AWS_SECRET_ACCESS_KEY': config['certbot']['aws']['secret_access_key']
    }

    command = ["certbot", "certonly",
               "--authenticator", "dns-route53",
               "--email", config['certbot']['email'],
               "--agree-tos",
               "--no-eff-email",
               "--keep-until-expiring",
               "--dns-route53",
               "--config-dir", f'{path}/../certs/certbot/config',
               "--logs-dir", f"{path}/../certs/certbot/log",
               "--work-dir", f"{path}/../certs/certbot/work",
               "-d", config['ucp']['ssl_certificate']['domain_name']]

    if 'sans' in config['ucp']['ssl_certificate'] and config['ucp']['ssl_certificate']['sans']:
        for san in config['ucp']['ssl_certificate']['sans']:
            command.append("-d")
            command.append(san)

    logger.debug(f"Executing command: {' '.join(command)}")

    execution = ExecuteCommand(command, environment)

    logger.debug(f"Execution results: {logger.prepare_execution(execution)}")

    if execution.result.returncode != 0:
        logger.error(f"Execution failed: {logger.prepare_execution(execution)}")
        raise Exception("Execution failed!")

    if 'Certificate not yet due for renewal; no action taken.' in execution.result.stdout:
        logger.info("UCP certificates are not yet due for renewal")
        return False

    return True


def manage_certs():
    global config
    global logger

    logger.info("Starting certificate management")

    manage_ucp_certs()
    manage_dtr_certs()

    logger.info("Certificate management complete")

    return


def manage_dtr_certs():
    logger.info("DTR certificate management started...")

    cert_applied = False
    if generate_dtr_certs() or config['certbot']['always_apply_certs']['dtr']:
        cert_applied = True

        logger.info("Applying DTR certificates")
        apply_dtr_certs()
        logger.info("DTR certificates applied")

    logger.info("DTR certificate management complete")

    return cert_applied


def manage_ucp_certs():
    logger.info("UPC certificate management started...")

    cert_applied = False
    if generate_ucp_certs() or config['certbot']['always_apply_certs']['ucp']:
        cert_applied = True

        logger.info("Applying UCP certificates")
        apply_ucp_certs()
        logger.info("UCP certificates applied")

    logger.info("UCP certificate management complete")

    return cert_applied


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf_dir", help="Configuration directory to use")
    args = parser.parse_args()

    config = ConfigLoader(args.conf_dir).load()
    logger = Logger(filename=__file__,
                    log_level=config['logging']['log_level'])

    manage_certs()
