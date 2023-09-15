import urcl_rules,os,re

labelList = []

def info():
    print('Cleans up urcl code and checks for errors')
    print('Usage: URCL.py clean [code.urcl] [-options]')
    print('Available options:')
    print('\t-o <file_path> : declare output file path (default is URCL.py/output/out.urcl)')
    print('\t-h : display this message')
    return

def lexLine(line,i):
    global labelList

    pieces = line[0].split()                                # split line into a list of components (opcode and operands)
    # detect what the line is (label, macro, dw, header, or instruction)
    opcode = pieces[0].strip()                             
    if opcode[0] == '.':
        lineType = 'label'
        labelEntry = (line[0], i)
        labelList.append(labelEntry)
    elif opcode[0] == '@':
        lineType = 'macro'
    elif opcode.lower() == 'dw':
        lineType = 'dw'
    elif opcode.lower() == 'bits':
        lineType = 'header'
    elif opcode.lower() == 'minreg':
        lineType = 'header'
    elif opcode.lower() == 'minheap':
        lineType = 'header'
    elif opcode.lower() == 'run':
        lineType = 'header'
    elif opcode.lower() == 'minstack':
        lineType = 'header'
    else:
        try:
            urcl_rules.urclOperationLengths[opcode.lower()]
            lineType = 'instruction'
        except KeyError:
            print(f'Error on line {line[1]}: "{line[0]}": Unrecognized instruction "{opcode}"')
            return 'error'
    
    # now do operand lexing
    operands = []
    operandRegex = r"'.'|[.$%@#RrMm][A-Za-z0-9]+"
    operandsString = " ".join(pieces[1:])                                     
    try:
        if operandsString[0] == '[':
            operands.append(operandsString[1:-1])
        else:
            result = re.finditer(operandRegex, operandsString)
            for x in result:
                operands.append(x.group(0))
    except IndexError:
        return (opcode,lineType,operands)

    print(f'{lineType} : {opcode} {operands}')
    return (opcode,lineType,operands)


def cleanCode(file, options=[]):
    global labelList
    outFile = './output/out.urcl'                                       # default output file
    if file == "":                                                      # if file is blank just print info and exit
        info()
        return 'success'
    
    for c,v in enumerate(options):                          
        if v.lower() == '-o':
            try:
                outFile = options[c+1]                                  # argument immediately after -o should be a file path
                if not (os.path.isfile(outFile)):
                    print('Error parsing command: -o flag used but no output path provided')
                    return 'error'
            except IndexError:
                print('Error parsing command: -o flag used but no output path provided')
                return 'error'
        if v.lower() == '-h':
            info()
            return 'success'

    if os.path.isfile(file):
        with open(file, 'r') as f:
            code = [line.rstrip('\n') for line in f]                    # strip newlines from each line in f, append each line to code
    else:
        print('Error parsing command: no source file provided.')
        return 'error'

    templist = []
    for i,line in enumerate(code):
        line = line.strip()                                             # remove leading and trailing whitespace
        if line != '':                                                  # check to make sure line isn't blank
            line = line.split('//')                                     # anything after a comment is useless
            if line[0] != '':                                           # make sure there is code before the comment
                lineout = (line[0].strip(),i+1)                         # add original line number to output for more readable errors
                templist.append(lineout)
#                                                                         templist is structured as a list of tuples
#                                                                         tuple is structured as ({line of code}, {original line number})

    for i,line in enumerate(templist):
        if '/*' in line[0] or '*/' in line[0]:
            print(f'ERROR ON LINE {line[1]}: {line[0]}: Multiline Comments Not Supported!')
            return 'error'
            # TODO: actually support multiline comments lmao

    for i,line in enumerate(templist):
        
        lexResult = lexLine(line,i)
        opcode = lexResult[0]
        lineType = lexResult[1]
        operands = lexResult[2]

        # the rest of this for loop is error detection
        # TODO: check for errors in urcl code (invalid number or type of operands)

        # TODO: look at opcode variable and determine if it's a header or macro or something before assuming it's an operand
        try:
            correctOpCount = urcl_rules.urclOperationLengths[opcode]    # get expected operand count for opcode
            if correctOpCount != len(operands):
                print(f'Error on line {line[1]}: "{line[0]}": Invalid operand count for instruction {opcode.upper()}, expected {correctOpCount}, got {len(operands)}')
                return 'error'
        except KeyError:
            pass
        
    

        templist[i] = (f'{opcode} {" ".join(operands)}\n', line[1])     # add original line number back



    # TODO: Decide what macros i want to implement and then handle them (this may have to be handled in a different program)
   
    with open(outFile, 'w') as f:                                       # output cleaned code to file
        for line in templist:
            f.write(f'{line[0]}')                                       # original line number no longer needed (although some way to preserve this might be useful for debugging)
    #print(labelList)
    return outFile                                                      # return output file for other functions to reference
    

