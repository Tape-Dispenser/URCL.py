import sys,os,time
import clean,lex,parse

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
    startTime = time.perf_counter()
    x = clean.clean(f,args)
    if x == 'error':
        exit()
    if os.path.isfile(x):
        endTime = time.perf_counter()
        print(f"file successfully cleaned and outputted to \"{x}\" in {endTime-startTime} seconds.")


elif command == 'lex':
    startTime = time.perf_counter()
    x = lex.lex(f,args)
    if x == 'error':
        exit()
    if os.path.isfile(x):
        endTime = time.perf_counter()
        print(f"file successfully lexed and outputted to \"{x}\" in {endTime-startTime} seconds.")

elif command == 'parse':
    startTime = time.perf_counter()
    x = parse.parse(f,args)
    if x == 'error':
        exit()
    if os.path.isfile(x):
        endTime = time.perf_counter()
        print(f"file successfully parsed and outputted to \"{x}\" in {endTime-startTime} seconds.")