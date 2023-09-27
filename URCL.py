import sys,os,clean,lex,parse

def print_info():
    print('bruh more args pls') # TODO: make this print actual info

command = ""
f = ""
args = []

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_info()
        exit()
    for i, arg in enumerate(sys.argv):
        if i == 0:
            pass
        elif i == 1:
            command = arg.lower()
        elif i == 2:
            if os.path.isfile(arg):
                f = arg
            else:
                args.append(arg)
        else:
            if os.path.isfile(arg):
                args.append(arg)
            else:
                args.append(arg)


#parse command

if command == 'clean':
    x = clean.clean(f,args)
    if x == 'error':
        exit()
    if os.path.isfile(x):
        print(f"file successfully cleaned and outputted to \"{x}\"")

elif command == 'lex':
    x = lex.lex(f,args)
    if x == 'error':
        exit()

elif command == 'parse':
    x = parse.parse(f,args)
    if x == 'error':
        exit()