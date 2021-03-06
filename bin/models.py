import json
from collections import OrderedDict


class ChangeLog(object):
    def __init__(self, file):
        self.filename = file
        with open(file, 'r') as f:
            content = f.read()
        self._changelog = json.loads(content)
        self.__build__()

    def __build__(self):
        self.result_changelog = {}
        for ele in self._changelog['changelog']:
            app_name = ele['application']
            if app_name not in self.result_changelog:
                self.result_changelog[app_name] = OrderedDict()
            dictionary = self.result_changelog[app_name]
            if ele['action'] == 'rollback':
                if len(dictionary) == 0:
                    raise RuntimeError('Rollback for empty list')
                key = next(reversed(dictionary))
                if ele['update_id'] == key:
                    dictionary.pop(ele['update_id'])
                    if len(dictionary) == 0:
                        self.result_changelog.pop(app_name)
                else:
                    raise RuntimeError()
            else:
                if ele['update_id'] in dictionary:
                    raise RuntimeError()
                else:
                    dictionary[ele['update_id']] = ele

    def can_roll_back(self, update_id):        
        for _, app in self.result_changelog.items():            
            key = next(reversed(app))
            if key == update_id:
                return True
            else:
                return False
        return False

    def applicable(self, change):
        application_name = change['application']
        if application_name in self.result_changelog:
            ordered_dict = self.result_changelog[application_name]
        else:
            return True

        latest_version = self.get_applied_latest_version(application_name)
        return change['update_id'] not in ordered_dict and change['version'] > latest_version

    def get_change(self, update_id):
        change = None
        for _, value in self.result_changelog.items():
            if update_id in value:
                change = value[update_id]
                break
        return change

    def apply_change(self, change):
        self._changelog['changelog'].append(change)
        with open(self.filename, 'w+') as f:
            json.dump(self._changelog, f, indent=4,
                      separators=(',', ': '), sort_keys=True)
        self.__build__()

    def get_applied_latest_version(self, application_name):
        latest_version = ''
        for key, change_log in self.result_changelog[application_name].items():
            if latest_version < change_log['version']:
                latest_version = change_log['version']
        return latest_version

class PatchInfo(object):
    def __init__(self, data):
        self.patch = data
