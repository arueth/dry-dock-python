import requests


class DtrApi:

    def __init__(self, endpoint, username, password, use_ssl=True, verify_ssl=True, logger=None):
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.logger = logger

        self.uri = f"https://{endpoint}" if use_ssl else f"https://{endpoint}"

        self.__token = None
        self.__hashed_token = None

        return

    def update_certs(self, body):
        url = f"{self.uri}/api/v0/meta/settings"

        response = self.__post_request(url=url, body=body)

        if response.status_code != 202:
            raise Exception(f"Failed to update certs - {response.status_code}")

        return response.json()

    def create_token(self, token_label):
        if self.__token is not None:
            return

        url = f"{self.uri}/api/v0/api_tokens"
        body = {"tokenLabel": token_label}

        response = requests.post(url=url,
                                 auth=requests.auth.HTTPBasicAuth(self.username, self.password),
                                 json=body,
                                 verify=self.verify_ssl)

        if response.status_code != 200:
            raise Exception(f"Failed to create DTR token for {self.endpoint} - {response.status_code}")

        if 'token' in response.json():
            self.__token = response.json()['token']
            self.__hashed_token = response.json()['hashedToken']
        else:
            raise Exception("Failed to extract DTR token")

        return True

    def delete_token(self):
        if self.__token is None:
            return

        url = f"{self.uri}/api/v0/api_tokens/{self.__hashed_token}"

        response = self.__delete_request(url=url)

        if response.status_code != 200:
            raise Exception(f"Failed to delete DTR token for {self.endpoint} - {response.status_code}")

        self.__token = None
        self.__hashed_token = None

        return True

    def __delete_request(self, url):
        return requests.delete(url=url,
                               auth=self.__get_auth(),
                               verify=self.verify_ssl)

    def __get_request(self, url, params=None):
        return requests.get(url=url,
                            auth=self.__get_auth(),
                            params=params,
                            verify=self.verify_ssl)

    def __post_request(self, url, body=None):
        return requests.post(url=url,
                             auth=self.__get_auth(),
                             json=body,
                             verify=self.verify_ssl)

    def __get_auth(self):
        return requests.auth.HTTPBasicAuth(self.username, self.__token)

    def __is_authenticated(self):
        url = f"{self.uri}/api/v0/api_tokens/{self.__hashed_token}"

        response = self.__get_request(url=url)

        if response.status_code != 200:
            return False

        return True
