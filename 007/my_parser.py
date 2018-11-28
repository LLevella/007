import argparse
from pprint import pprint

from datarequests import VkRequests
from dataloader import DataLoader

class CommandParser:
    def __init__(self):
        #парсер для аргументов командной строки
        self.parser = argparse.ArgumentParser(
                prog = '007',
                description = '''Агент 007''',
                            add_help = False
                )
        # Вызов помощи 
        parent_group = self.parser.add_argument_group (title='Параметры')
        parent_group.add_argument ('--help', '-h', action='help', help='Справка')
        
        subparsers = self.parser.add_subparsers (dest = 'command',
                title = 'Возможные команды')
 
        # Создаем парсер для команды infile
        load_in_file_parser = subparsers.add_parser ('infile',
                add_help = False,
                help = 'Запуск поиска в режиме выгрузки в файл',
                description = '''Выгружает список групп в ВК, в которых состоит 
                            пользователь, но не состоит никто из его друзей в файл''')
 
        # Создаем новую группу параметров 
        load_in_file_parser_args = load_in_file_parser.add_argument_group (title='Параметры')
 
        # Добавляем параметры
        load_in_file_parser_args.add_argument ('--user', '-u', help = 'Имя пользователя', metavar = 'ИМЯ')
        load_in_file_parser_args.add_argument ('--id', '-i', help = 'ID пользователя', metavar = 'ID')
        load_in_file_parser_args.add_argument ('--help', '-h', action='help', help='Справка')


        # Создаем парсер для команды onscreen
        load_on_screen_parser = subparsers.add_parser ('onscreen',
                add_help = False,
                help = 'Запуск поиска в режиме вывода на экран',
                description = '''Выводит на экран список групп в ВК, в которых состоит 
                            пользователь, но не состоит никто из его друзей''')
        # Создаем новую группу параметров
        load_on_screen_parser_args = load_on_screen_parser.add_argument_group (title='Параметры')
 
        # Добавляем параметры
        load_on_screen_parser_args.add_argument ('--user', '-u', help = 'Имя пользователя', metavar = 'ИМЯ')
        load_on_screen_parser_args.add_argument ('--id', '-i', help = 'ID пользователя', metavar = 'ID')
        load_on_screen_parser_args.add_argument ('--help', '-h', action='help', help='Справка')
 
    def run(self,*args):
        self.namespace = self.parser.parse_args(*args)

        if (not self.namespace) or (not self.namespace.command):
            print("Возможные аргументы:\n infile (-i/-u/-h) \n onscreen (-i/-u/-h)")
            return False

        if self.namespace.command == "infile":
            self.get_file_name()

        if not self.run_loader():
            print("!\tЗапуск загрузки данных без параметров невозможен")
            return False
        self.write_result()
        return True

    def get_file_name(self):
        print("Имя файла:")
        self.file_name = input()
        if not self.file_name:
            print("будет использоваться имя файла по умолчанию:")
            if self.namespace.id:
                self.file_name = "id={}.json".format(self.namespace.id)
            elif self.namespace.user:
                self.file_name = "user={}.json".format(self.namespace.user)
            else:
                print("!\tИмя невозможно вычислить - режим переведен на выгрузку на экран")
                self.file_name = ""
            print(self.file_name)
     
    def run_loader(self):
        if not (self.namespace.user or self.namespace.id):
            return False
        if self.namespace.user:
            vk_request = VkRequests(user_name = self.namespace.user)
        else: 
            vk_request = VkRequests(user_id = self.namespace.id)
        self.data_loader = DataLoader(vk_request)
        self.data_loader.mp_load()
        return True
    
    def write_result(self):
        intersec = self.data_loader.result_of_intersection(N = 10, eqv = "<")
        diff = self.data_loader.result_of_defferencial()
        if not self.file_name:
            self.write_result_onscreen(intersec, diff,  N = 10, eqv = "<")
        else:
            self.write_result_infile(intersec, diff,  N = 10, eqv = "" )

    def write_result_onscreen(self, intersec, diff, N = 10, eqv = "<" ):
        print("Группы, в которых нет никого из друзей пользователя:")
        pprint(diff)
        print("Группы, в которых {} {} друзей:".format(eqv, N))
        pprint(intersec)

    def write_result_infile(self, intersec, diff, N = 10, eqv = "<" ):
      with open(self.file_name, 'wt') as outintersect:
          pprint(intersec, stream=outintersect)
      print("Группы, в которых нет никого из друзей пользователя, в файле: {}".format(self.file_name))
      with open("Nles10-"+self.file_name, 'wt') as outdiff:
          pprint(diff, stream=outdiff)
      print("Группы, в которых {} {} друзей, в файле: {}".format(eqv, N, "Nles10-" + self.file_name))



