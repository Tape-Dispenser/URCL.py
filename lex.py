import urcl_rules,os,re

def info():
    print('Lexes URCL code')
    print('Available options:')
    print('\t-o <file_path> : declare output file path (default is URCL.py/output/out.urcl)')
    print('\t-h : display this message')
    return

def lexLine(line:str):
    # this no longer does parsing

    if line.strip() != "":
        
        #print(line) # DEBUG LINE
        pieces = line.split()
        opcode = pieces[0].strip()      # pretty self-explanitory.
    
        # now do operand lexing
        inList = False
        operands = []
        listRegex = r"\[.*?\]"
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
    else:
        return 'blank line'
    print(f'{opcode} {operands}')
    return (opcode,operands)

def lex(file, options=[]):
    outFile = './output/out.urcl'                                       # default output file
    if file == "":                                                      # if file is blank just print info and exit
        info()
        return 'success'
    
    
    # command handling as well as the lex loop setup is done here
    # line by line lexing is done in lexLine() obviously
    
    for c,v in enumerate(options):  # TODO: REWORK THIS FOR LEXING OPTIONS@!!!!!!!                     
        if v.lower() == '-o':
            try:
                outFile = options[c+1]                                  # argument immediately after -o should be a file path
                if not (os.path.isfile(outFile)):
                    print('Error parsing command: -o flag used but no output path provided/bad file path')
                    return 'error'
            except IndexError:
                print('Error parsing command: -o flag used but no output path provided')
                return 'error'
        if v.lower() == '-h':
            info()
            return 'success'
    

    if os.path.isfile(file):
        with open(file, 'r') as f:
            lines = [line.rstrip('\n') for line in f]                    # strip newlines from each line in f, append each line to code
    else:
        print('Error parsing command: no source file provided.')
        return 'error'

    for i,line in enumerate(lines):
        lexResult = lexLine(line)
        if type(lexResult) != str:
            opcode = lexResult[0]
            operands = lexResult[1]
            lines[i] = (opcode, operands, )     # add original line number back
        else:
            if lexResult == 'blank line':
                lines.pop(i)
            if lexResult == 'error':
                exit()

    with open(outFile, 'w') as f:                                       # output cleaned code to file
        for line in lines:
            f.write(f'{line[0]},{line[1]},{line[2]}\n')                                       # original line number no longer needed (although some way to preserve this might be useful for debugging)
    return outFile