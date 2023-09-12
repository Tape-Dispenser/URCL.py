import sys,os,clean

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
                args.append(arg.lower())
        else:
            args.append(arg.lower())

#check to see file exists


    #parse command
if command == 'clean':
    x = clean.cleanCode(f,args)
    if x == 'error':
        exit()