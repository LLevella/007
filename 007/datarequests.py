
import requests
import urllib
import json
import pprint
import sys

def get_dict_for_load_data(server_name, params_data):
    requests_data = requests.get(server_name, params=params_data)
    dict_from_request = requests_data.json()
    return dict_from_request


class VkRequests:
    APP_ID = '6633040'
    API_VERSION = '5.80'
    AUTH_SERVER = 'https://oauth.vk.com/authorize'
    API_SERVER = 'https://api.vk.com/method/'
    FRIENDS_METHOD = 'friends.get'
    USERS_METHOD = 'users.get'
    GROUPS_METHOD = 'groups.get'
    GROUPS_NAME_METHOD = 'groups.getById'
    TOKEN = 'ed1271af9e8883f7a7c2cefbfddfcbc61563029666c487b2f71a5227cce0d1b533c4af4c5b888633c06ae'

    def __init__(self, user_id = 0, user_name = ""):
        if user_id != 0:
            self.user_id = user_id
        elif user_name:
            self.user_id = self.get_user_id_from_request(user_name)
    
    def create_straddres_for_token_extraction(self):
        auth_data = {
            'client_id': self.APP_ID,
            'display': 'popup',
            'redirect_uri': 'https://oauth.vk.com/blank.html',
            'scope': 'friends',
            'response_type': 'token',
            'v': self.API_VERSION
            }
        return '?'.join((self.AUTH_SERVER, urllib.parse.urlencode(auth_data)))

    def error_handler(self, dict):
        if 'error' in dict:
            print(dict['error']['error_msg'])
            print('Пройдите по адресу для получения токена: {}'.format(self.create_straddres_for_token_extraction()))
            return True
        print(dict)
        return False
    
    def get_user_id_from_request(self, user_name):
        users_get_params = {
            'user_id': user_name,
            'access_token': self.TOKEN,
            'v': self.API_VERSION
            }
        user_id_tmp = 0
        user_server = self.API_SERVER + self.USERS_METHOD
        user_id_dict = get_dict_for_load_data(user_server, users_get_params)
        
        if self.error_handler(user_id_dict):
          return 0

        if user_id_dict['response']:
            if user_id_dict['response'][0]:
                if user_id_dict['response'][0]['id']:
                    user_id_tmp =  user_id_dict['response'][0]['id']
            elif user_id_dict['response']['id']:
                user_id_tmp = user_id_dict['response']['id']
        return user_id_tmp

    def get_friends_from_request(self):
        friends_get_params = {
            'user_id': self.user_id,
            'access_token': self.TOKEN,
            'v': self.API_VERSION
            }
        friends_server = self.API_SERVER + self.FRIENDS_METHOD
        self.users_friends_id_dict = get_dict_for_load_data(friends_server, friends_get_params)
        return self.users_friends_id_dict

    def get_groups_from_request(self, user_id = 0, count = 1000):
        if not user_id or user_id == 0:
          user_id = self.user_id
        groups_get_params = {
            'user_id': user_id,
            'access_token': self.TOKEN,
            'v': self.API_VERSION,
            'count': count
            }
        groups_server = self.API_SERVER + self.GROUPS_METHOD
        self.users_groups_id_dict = get_dict_for_load_data(groups_server, groups_get_params)
        return self.users_groups_id_dict

    def get_group_data_from_request(self, group_id = 0):
        groups_get_params = {
            'group_id': group_id,
            'access_token': self.TOKEN,
            'v': self.API_VERSION
            }
        groups_server = self.API_SERVER + self.GROUPS_NAME_METHOD
        self.users_groups_id_dict = get_dict_for_load_data(groups_server, groups_get_params)
        return self.users_groups_id_dict


