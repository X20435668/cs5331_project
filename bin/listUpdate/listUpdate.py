import http.client
import json


class UpdateLister:
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.server_list = []
        with open('settings.json') as settings_file:
            data = json.load(settings_file)
            for server in data.server_list:
                self.server_list.extend(server)

    def list_all(self):
        # Temporarily only one server
        client = http.client.HTTPConnection(self.server_list[0], timeout=self.timeout)
        client.request('GET', path)
        response = client.getresponse()
        content = response.read().decode('UTF-8')
        data = json.loads(content)
        return_data = data.update_info
        return [{key: package[key] for key in {"update_id", "version", "package_name"}} for package in return_data]

    def list_package_by_name(self, name):
        path = self.compute_path(name)
        # Temporarily only one server
        client = http.client.HTTPConnection(self.server_list[0], timeout=self.timeout)
        client.request('GET', path)
        response = client.getresponse()
        content = response.read().decode('UTF-8')
        data = json.loads(content)
        return data

    def get_versions_of_package(self):
        pass
