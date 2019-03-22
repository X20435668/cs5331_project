import json

class ChangeLog(object):
    def __init__(self, file):
        self._changelog = json.loads(file)
        self.filename = file
    def can_roll_back(self, change):
        application_name = change['application']
        rollback_stack = []
        for ele in reversed(self._changelog['changelog']):
            if application_name == ele['application']:
                if ele['action'] == 'rollback':
                    rollback_stack.append(ele)
                else:
                    roll_len = len(rollback_stack)
                    if roll_len>0:
                        last_rollback = rollback_stack[roll_len-1]
                        if last_rollback['update_id'] == ele['update_id']:
                            rollback_stack.pop(roll_len-1)
                        else:
                            raise RuntimeError()
                    else:
                        if ele['update_id'] == change['update_id']:
                            return True
                        else:
                            return False
        return True

    def appliable(self, change):
        application_name = change['application']
        result_set = {} 
        for ele in self._changelog['changelog']:
            if application_name == ele['application']:
                if ele['action'] == 'rollback':
                    if ele['update_id'] in result_set:
                        result_set.pop(ele['update_id'])
                    else:
                        raise RuntimeError()
                else:
                    if ele['update_id'] in result_set:
                        raise RuntimeError()
                    else:
                        result_set[ele['update_id']] == ele
        return change['update_id'] not in result_set
    def get_not_applied_patch(self, patch_info_list):
        pass
        

    def apply_change(self,change):
        self._changelog['changelog'].append(change)
        json.dump(self._changelog, self.filename)
class PatchInfo(object):
    def __init__(self, data):
        self.patch = json.loads(data)
