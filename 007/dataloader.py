from multiprocessing import Process, Queue, Lock
import sys
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
    set_tmp = set(list_from_dict(cur_dict))
    return count_tmp, set_tmp

class DataLoader:
    def __init__(self, requester):
        self.requester = requester
        self.groups = Queue()
        self.groups_intersections = Queue()
        self.lock = Lock()

    def loader(self):
        friends_count = self.friends_count
        for friend in self.friends:
            user_groups_dict = self.requester.get_groups_from_request(friend)
            if not self.requester.error_handler(user_groups_dict):
                user_groups_count, user_groups_set = get_set_and_count_from_dict(user_groups_dict)
            if not user_groups_count or not user_groups_set:
                friends_count -= 1
                continue
            self.groups.put(user_groups_set)
            friends_count -= 1
            self.print_data_without_lock("\r\x1b[K->загрузка групп: осталось ", int(100*friends_count/self.friends_count),  is_flush = True, end = "%")
            if friends_count < 1:
                break
        self.groups.put("END")
        self.print_data_with_lock("\nLoader закончил загрузку")

    def groups_handler(self):
        while True:
            user_groups_set = self.groups.get()
            if user_groups_set == "END":
                break
            self.groups_differ -= user_groups_set
            self.groups_intersections.put(self.user_groups & user_groups_set)
        self.groups_intersections.put("END")
        self.print_data_with_lock("Groups_handler закончил обработку")

    def intersections_handler(self):
        while True:
            groups_intersection = self.groups_intersections.get()
            if groups_intersection == "END":
                break
            self.count_users_in_acrossing_groups(groups_intersection)
        self.print_data_with_lock("Intersections_handler закончил обработку")
            
    def count_users_in_acrossing_groups(self, groups_intersection):
        for group in groups_intersection:
                self.groups_dict[group] += 1

    def print_data_with_lock(self, str="", eqv = "", is_flush = False):
        self.lock.acquire()
        try:
            self.print_data_without_lock(str, eqv, is_flush = False)
        finally:
            self.lock.release()
    
    def print_data_without_lock(self, str = "", eqv = "", end = "\n",  is_flush = False):
        print("{} {}".format(str, eqv), end = end)
        if is_flush:
            sys.stdout.flush()

    def init_load(self):
        friends_dict = self.requester.get_friends_from_request()
        print("Загружен список друзей")
        if self.requester.error_handler(friends_dict):
            return False
        friends_count, friends_list = get_list_and_count_from_dict(friends_dict)
        if not friends_count or not friends_list:
            return False
        self.friends = friends_list
        self.friends_count = friends_count
        
        user_groups_dict = self.requester.get_groups_from_request()
        print("Заугржен список групп пользователя")
        if self.requester.error_handler(user_groups_dict):
            return False
        user_groups_count, user_groups_set = get_set_and_count_from_dict(user_groups_dict)
        if not user_groups_count or not user_groups_set:
            return False
        self.user_groups = user_groups_set
        self.user_groups_count = user_groups_count
        self.groups_differ = user_groups_set
        self.groups_dict = dict.fromkeys(user_groups_set, 0)


    def load(self): # последовательная процедура
        self.init_load()        
        for friend in self.friends:
            # print(friend)
            user_groups_dict = self.requester.get_groups_from_request(friend)
            if not self.requester.error_handler(user_groups_dict):
                user_groups_count, user_groups_set = get_set_and_count_from_dict(user_groups_dict)
            if not user_groups_count or not user_groups_set:
                friends_count -= 1
                continue
            self.groups_differ -= user_groups_set
            groups_intersection = self.user_groups & user_groups_set
            self.count_users_in_acrossing_groups(groups_intersection)
            friends_count -= 1
            print("\r\x1b[K друзей осталось {}".format(friends_count), end= "")
            sys.stdout.flush()

    def mp_load(self): # мультипроцессная 
        self.init_load()
        procs = []
        
        proc_load = Process(target=self.loader, args=())
        procs.append(proc_load)
        proc_load.start()

        proc_groups_handler = Process(target=self.groups_handler, args=())
        procs.append(proc_groups_handler)
        proc_groups_handler.start()
        
        proc_intersections_handler = Process(target=self.intersections_handler, args=())
        procs.append(proc_intersections_handler)
        proc_intersections_handler.start()

        for proc in procs:
            proc.join()

    def get_intersection(self, N = 10, eqv = "<"):
        if (eqv == "="):
            str_group_ids = ', '.join(str(s) for s in self.groups_dict.keys() if self.groups_dict[s] == N)
        if (eqv == ">"):
            str_group_ids = ', '.join(str(s) for s in self.groups_dict.keys() if self.groups_dict[s] > N)
        if (eqv == "<"):
            str_group_ids = ', '.join(str(s) for s in self.groups_dict.keys() if self.groups_dict[s] < N)
        if (eqv == ">="):
            str_group_ids = ', '.join(str(s) for s in self.groups_dict.keys() if self.groups_dict[s] >= N)
        if (eqv == "<="):
            str_group_ids = ', '.join(str(s) for s in self.groups_dict.keys() if self.groups_dict[s] <= N)
        return str_group_ids

    def get_differ_str(self):
        str_group_ids = ', '.join(str(s) for s in self.user_groups)
        return str_group_ids

    def result_of_intersection(self, N = 10, eqv = "<"):
        str_inter = self.get_intersection(N = 10, eqv = "<")
        inter_groups_dict = self.requester.get_group_data_from_request(str_inter)
        if self.requester.error_handler(inter_groups_dict):
            return 
        return inter_groups_dict
    
    def result_of_defferencial(self):
      str_diff = self.get_differ_str()
      diff_groups_dict = self.requester.get_group_data_from_request(str_diff)
      if self.requester.error_handler(diff_groups_dict):
          return 
      return diff_groups_dict