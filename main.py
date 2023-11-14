from utilities import *
from commands import *


def main():
    parseArguments()
    input_cmd = InputCommands(sets=Global.SETS, ways=Global.WAYS)
    file_handle = readFile()
    lines = file_handle.readlines()
    if Global.mode == 'v':
        print("Reading {} file line by line for parsing".format(filename))
    for line in lines:
        n, address = getNextCommand(line)
        if n is None:
            if Global.mode == 'n':
                print("****** Error: Invalid Command or address")
        else:
            input_cmd.commandOperations(command=n, address=address)
    input_cmd.outputStatistics()
    file_handle.close()


if __name__ == '__main__':
    main()
