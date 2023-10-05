import re,urcl_rules,os
labelList = []

def info():
    print('Parses URCL code')
    print('Available options:')
    print('\t-h : display this message')
    print('\t-e <command> : command to run next in chain')
    return

def parseLine(opcode, operands, originalLineNum, realLineNum):
    global labelList

    outputOperands = []

    for operand in operands:
        if opcode[0] == '.':
            linetype = 'label'
            labelEntry = (opcode, originalLineNum)
            labelList.append(labelEntry)
        elif opcode[0] == '@':
            linetype = 'macro'
        elif opcode.lower() == 'dw':
            linetype = 'dw'
        elif opcode.lower() == 'bits':
            linetype = 'header'
        elif opcode.lower() == 'minreg':
            linetype = 'header'
        elif opcode.lower() == 'minheap':
            linetype = 'header'
        elif opcode.lower() == 'run':
            linetype = 'header'
        elif opcode.lower() == 'minstack':
            linetype = 'header'
        else:
            try:
                urcl_rules.urclOperationLengths[opcode.lower()]
                linetype = 'instruction'
            except KeyError:
                print(f'Error on line {originalLineNum}: "{f"{opcode} {operand}"}": Unrecognized instruction "{opcode}"')
                return 'error'

        if linetype == 'instruction':

            #TODO : make this a pattern maching thingy
            
            regex = re.fullmatch(r'~[+-]?[0-9]+', operand)              # check for relative address
            if type(regex) == re.match:
                outputOperands.append( (operand,'relative address') )
                continue
            
            regex = re.fullmatch(r'[rR$][-+]?[0-9]+', operand)               # check for register
            if type(regex) == re.match:
                outputOperands.append( (operand,'register') )
                continue

            regex = re.fullmatch(r'[-+]?0[xX][-+]?[0-9]+', operand)               # check for hex immediate    
            if type(regex) == re.match:
                outputOperands.append( (operand,'hex immediate') )
                continue

            regex = re.fullmatch(r'[-+]?0[bB][-+]?[01]+', operand)                # check for binary immediate
            if type(regex) == re.match:
                outputOperands.append( (a,'binary immediate') )
                continue
            
            regex = re.fullmatch(r'[-+]?[0-9]+', operand)                    # check for decimal immediate
            if type(regex) == re.match:
                outputOperands.append( (operand,'decimal immediate') )
                continue

            regex = re.fullmatch(r'\'.\'', operand)                     # check for character immediate
            if type(regex) == re.match:
                a = ord(operand[1])
                outputOperands.append( (a,'immediate') )
                continue

            regex = re.fullmatch(r'\.[a-zA-Z0-9-_]', operand)           # check for labels, check that label is defined
            if type(regex) == re.match:
                try:
                    labelList.index(operand)
                    outputOperands.append(operand, '')
                    continue
                except ValueError:
                    print(f'Error: Undefined label "{operand}" referenced on line {originalLineNum}')
                    return('error')

            regex = re.fullmatch(r'[mM#][0-9]+', operand)               # check for heap pointer
            if type(regex) == re.match:
                outputOperands.append( (operand,'heap pointer') )
                continue

            regex = re.fullmatch(r'%[a-zA-Z0-9-_]', operand)            # check for port
            if type(regex) == re.match:
                outputOperands.append( (operand, 'port') )
                continue

            regex = re.fullmatch(r'@[a-zA-Z0-9-_]', operand)            # check for macro
            if type(regex) == re.match:
                # TODO: implement something similar to labels for keeping track of and detecting undefined macros
                outputOperands.append( (operand, 'macro') )
                continue

            print(f'Error: Unrecognized operand "{operand}" on line {originalLineNum}')
            return('error')
    return (linetype, outputOperands)

def parse(file, options=[]):
    outFile = './output/out.urcl'                                       # default output file
    if file == "":                                                      # if file is blank just print info and exit
        info()
        return 'success'
    
    # argument handling loop
    for c,v in enumerate(options):                          
        if v.lower() == '-h':
            info()
            return 'success'
        if v.lower() == '-e':
            try:
                endCommand = options[c+1]
            except IndexError:
                print('Error parsing command: -e flag used but no command provided')
                return 'error'
    
    # open file and read it as string
    if os.path.isfile(file):
        with open(file, 'r') as f:
            lines = [line.rstrip('\n') for line in f]                    # strip newlines from each line in f, append each line to code
    else:
        print('Error parsing command: no source file provided.')
        return 'error'
    
    for lineNum,line in enumerate(lines):
        #linenum is the actual urcl line, and can be used for relative calculations
        parsedLine = parseLine()