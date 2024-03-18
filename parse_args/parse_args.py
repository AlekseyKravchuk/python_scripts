#!/usr/bin/env /usr/bin/python3
import os.path
import sys
import getopt


def usage():
    fname = os.path.basename(__file__)
    print(f"{fname}/prefix or {fname} -m 255.255.255.0 or {fname} --mask 255.255.255.0")


# печатает полное имя после получения имени и фамилии из командной строки
def full_name():
    first_name = None
    last_name = None
    opts = []

    arg_list = sys.argv[1:]

    try:
        # Опции, требующие аргумента, должны сопровождаться двоеточием (':')
        short_options = "f:l:"          # option definition string for single character options

        # Длинные опции, требующие аргумента, должны сопровождаться знаком равно ('=')
        long_optons = ["first_name=",
                       "last_name="]  # sequence of the long-style option names
        opts, args = getopt.getopt(arg_list, short_options, long_optons)
    except:
        usage()
        sys.exit()

    for opt, arg in opts:
        if opt in ['-f', '--first_name']:
            first_name = arg
        elif opt in ['-l', '--last_name']:
            last_name = arg
        else:  # необработанный вариант
            usage()
            sys.exit()

    print(f"{first_name} {last_name}")


def main():
    # script_name = sys.argv[0]
    # arg_list = sys.argv[1:]
    full_name()


if __name__ == '__main__':
    main()
