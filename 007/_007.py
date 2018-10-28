import sys
from my_parser import CommandParser

if __name__ == '__main__':

    command = CommandParser()
    if not command.run(sys.argv[1:]):
      print("Используйте -h или --help для вызова справки")
    
    print("Всего доброго:)")