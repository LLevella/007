from datarequests import VkRequests

def count_points_in_dict(cur_dict):
    count_points = 0
    if cur_dict['response']:
        if cur_dict['response']['count']:
            count_points =  cur_dict['response']['count']
    return count_points

def list_from_dict(cur_dict):
    cur_list = list()
    if cur_dict['response']:
        if cur_dict['response']['items']:
            cur_list = cur_dict['response']['items']
    return cur_list

def set_to_list(cur_set):
    list_tmp = list(cur_set)
    return list_tmp

def get_list_and_count_from_dict(cur_dict):
  count_tmp = count_points_in_dict(cur_dict)
  list_tmp = list_from_dict(cur_dict)
  return count_tmp, list_tmp
    
def get_set_and_count_from_dict(cur_dict):
    count_tmp = count_points_in_dict(cur_dict)
    print(count_tmp)
    set_tmp = set(list_from_dict(cur_dict))
    return count_tmp, set_tmp

class DataLoader:
    def __init__(self, requester):
        self.requester = requester

    def load(self):
        friends_dict = self.requester.get_friends_from_request()
        print(friends_dict)
        if self.requester.error_handler(friends_dict):
            return False
        friends_count, friends_list = get_list_and_count_from_dict(friends_dict)
        print("++++++++++++++")
        print(friends_count)
        print(friends_list)
        print("++++++++++++++")
        if not friends_count or not friends_list:
            return False
        self.friends = friends_list
        self.friends_count = friends_count
        
        user_groups_dict = self.requester.get_groups_from_request()
        print(user_groups_dict)
        if self.requester.error_handler(user_groups_dict):
            return False
        user_groups_count, user_groups_set = get_set_and_count_from_dict(user_groups_dict)
        print(user_groups_count)
        print(user_groups_set)
        if not user_groups_count or not user_groups_set:
            return False
        self.user_groups = user_groups_set
        self.user_groups_count = user_groups_count

        for friend in self.friends:
            print(friend)
            user_groups_dict = self.requester.get_groups_from_request(friend)
            if not self.requester.error_handler(user_groups_dict):
                user_groups_count, user_groups_set = get_set_and_count_from_dict(user_groups_dict)
            if not user_groups_count or not user_groups_set:
                friends_count -= 1
                continue
            self.user_groups -= user_groups_set
            if len(self.user_groups) == 0: 
                break
            friends_count -= 1
            print("друзей осталось")
            print(friends_count)
            