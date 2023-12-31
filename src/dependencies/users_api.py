from flask import (
    session,
)
import json
from src import config
import requests


class UserApi:

    def __init__(self):
        self.base_url = config.USER_API_URL
        self.headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "Authorization": f"Bearer {session.get('access_token')}"
        }

    def _make_post_request(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        response = requests.request("POST", url, data=json.dumps(data), headers=self.headers)
        return json.loads(response.text)

    def _make_post_request_files(self, endpoint, files):
        url = f"{self.base_url}/{endpoint}"
        headers = {'Authorization': f"Bearer {session.get('access_token')}"}
        response = requests.post(url, files=files, headers=headers)
        return json.loads(response.text)

    def _make_get_request(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        response = requests.request("GET", url, headers=self.headers)
        return json.loads(response.text)

    def register_user(self, data):
        endpoint = "register"
        return self._make_post_request(endpoint, data)

    def create_folder(self, folder_id):
        endpoint = f"create_folder/{folder_id}"
        return self._make_post_request(endpoint, {})

    def login(self, data):
        endpoint = "login"
        return self._make_post_request(endpoint, data)

    def update_pass(self, data):
        endpoint = "update_pass"
        return self._make_post_request(endpoint, data)

    def new_extract(self, data):
        endpoint = "new_extract"
        return self._make_post_request(endpoint, data)

    def get_documents(self, folder_id):
        endpoint = f"get_document_list/{folder_id}"
        return self._make_get_request(endpoint)

    def get_document_urls(self, data):
        endpoint = "get_documents"
        return self._make_post_request(endpoint, data)

    def post_document(self, folder_id, file_name, file_content):
        endpoint = f"post_document_extract/{folder_id}"
        file_store = {file_name: file_content}
        return self._make_post_request_files(endpoint, file_store)
