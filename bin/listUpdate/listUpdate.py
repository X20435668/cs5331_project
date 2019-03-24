import http.client
import json


class UpdateLister:
    def __init__(self, patch_info, changelog, timeout=5):
        self.__timeout = timeout
        self.__server_list = []
        self.patch_info = patch_info.patch
        self.changelog = changelog
        with open('settings.json') as settings_file:
            data = json.load(settings_file)
            for server in data['server_list']:
                self.server_list.extend(server)

    def list_all(self):
        patch_info_new = self.get_not_applied_patch()
        return [{key: package[key] for key in {"update_id", "version", "package_name"}} for package in
                patch_info_new]

    def list_package_by_name(self, name):
        path = self.compute_path(name)
        # Temporarily only one server
        client = http.client.HTTPConnection(self.server_list[0], timeout=self.timeout)
        client.request('GET', path)
        response = client.getresponse()
        content = response.read().decode('UTF-8')
        data = json.loads(content)
        return data

    def get_not_applied_patch(self):
        not_patched = []
        for patch_info_single in self.patch_info:
            if self.changelog.appliable(patch_info_single):
                not_patched.append(patch_info_single)
        return not_patched

    def get_versions_of_package(self):
        pass
