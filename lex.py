import urcl_rules,os,re

def info():
    print('Lexes URCL code')
    print('Available options:')
    print('\t-o <file_path> : declare output file path (default is URCL.py/output/out.urcl)')
    print('\t-h : display this message')
    return

def lexLine(line):
    global labelList,defineDict
    # this no longer does parsing

    pieces = line[0].split()                                # split line into a list of components (opcode and operands)
    # detect what the line is (label, macro, dw, header, or instruction)
    opcode = pieces[0].strip()                             
    
    # now do operand lexing
    inList = False
    operands = []
    listRegex = r"\[.*\]"
    operandRegex = r"'.'|'..'|[.$%@#RrMm]?[A-Za-z0-9-_]+|~[+-]?[0-9]+"
    operandsString = " ".join(pieces[1:])
    result = re.fullmatch(listRegex, operandsString)
    if type(result) == re.match:
        operandsString = operandsString[1:-1]
        inList = True                                
    try:   
        result = re.finditer(operandRegex, operandsString)
        for x in result:
            operands.append(x.group(0))
    except IndexError:
        return (opcode,operands)
    if inList:
        pass
        #this seemed like it might be useful for something, might have to delete this later

    print(f'{opcode} {operands}')
    return (opcode,operands)

def lex():
    pass
    # command handling as well as the lex loop setup is done here
    # line by line lexing is done in lexLine() obviously
