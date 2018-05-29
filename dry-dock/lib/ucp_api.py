import requests


class UcpApi:

    def __init__(self, endpoint, username, password, use_ssl=True, verify_ssl=True, logger=None):
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.logger = logger

        self.uri = f"https://{endpoint}" if use_ssl else f"https://{endpoint}"
        self.__session_token = None

        return

    def create_config(self, body):
        url = f"{self.uri}/configs/create"

        response = self.__post_request(url=url, body=body)

        if response.status_code != 200:
            raise Exception("Failed to create config - %s" % response.status_code)

        return response.json()

    def create_interlock(self, http_port, https_port, arch):
        url = f"{self.uri}/api/interlock"
        body = {"HTTPPort": http_port,
                "HTTPSPort": https_port,
                "Arch": arch}

        response = self.__post_request(url=url, body=body)

        if response.status_code == 400:
            self.logger.warning(response.json()['message'])
        elif response.status_code != 204:
            raise Exception(f"Failed to create interlock - {response.status_code}")

        return response

    def delete_interlock(self):
        url = f"{self.uri}/api/interlock"

        response = self.__delete_request(url=url)

        if response.status_code != 204:
            raise Exception(f"Failed to delete interlock - {response.status_code}")

        return response

    def get_config(self, config_id):
        url = f"{self.uri}/configs/{config_id}"

        response = self.__get_request(url=url)

        if response.status_code != 200:
            raise Exception(f"Failed to find configs - {response.status_code}")

        return response.json()

    def get_interlock(self):
        url = f"{self.uri}/api/interlock"

        response = self.__get_request(url=url)

        if response.status_code != 200:
            raise Exception(f"Failed to get interlock - {response.status_code}")

        return response

    def find_configs(self, filters=None):
        url = f"{self.uri}/configs"

        params = None
        if filters:
            params = {'filters': filters}

        response = self.__get_request(url=url, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to find configs - {response.status_code}")

        return response.json()

    def find_services(self, filters=None):
        url = f"{self.uri}/services"

        params = None
        if filters:
            params = {'filters': filters}

        response = self.__get_request(url=url, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to find services - {response.status_code}")

        return response.json()

    def login(self):
        if self.__session_token is not None:
            return

        url = f"{self.uri}/id/login"
        body = {"password": self.password,
                "username": self.username}

        response = requests.post(url=url, json=body, verify=self.verify_ssl)

        if response.status_code != 200:
            raise Exception(f"Failed to login to the UCP API at {self.endpoint} - {response.status_code}")

        if 'sessionToken' in response.json():
            self.__session_token = response.json()['sessionToken']
        else:
            raise Exception("Failed to extract login sessionToken")

        return True

    def logout(self):
        if self.__session_token is None:
            return

        url = f"{self.uri}/id/logout"

        response = self.__post_request(url=url)

        if response.status_code != 204:
            raise Exception(f"Failed to logout of the UCP API at {self.endpoint} - {response.status_code}")

        self.__session_token = None

        return True

    def update_certs(self, body):
        url = f"{self.uri}/api/nodes/certs"

        response = self.__post_request(url=url, body=body)

        if response.status_code != 200:
            raise Exception(f"Failed to update certs - {response.status_code}")

        return response

    def update_service(self, service, body):
        url = f"{self.uri}/services/{service['ID']}/update?version={service['Version']['Index']}"

        response = self.__post_request(url=url, body=body)

        if response.status_code != 200:
            raise Exception(f"Failed to update service[{service['Spec']['Name']}] - {response.status_code}")

        return response.json()

    def __delete_request(self, url):
        return requests.delete(url=url,
                               headers=self.__get_auth_header(),
                               verify=self.verify_ssl)

    def __get_request(self, url, params=None):
        return requests.get(url=url,
                            headers=self.__get_auth_header(),
                            params=params,
                            verify=self.verify_ssl)

    def __post_request(self, url, body=None):
        return requests.post(url=url,
                             headers=self.__get_auth_header(),
                             json=body,
                             verify=self.verify_ssl)

    def __get_auth_header(self):
        return {'Authorization': f"Bearer {self.__session_token}"}

    def __is_authenticated(self):
        url = f"{self.uri}/id"

        response = self.__get_request(url=url)

        if response.status_code != 200:
            return False

        return True
