import os,re,ast
import urcl_rules
#import numpy

compiler_extras = True

labelDict = {}
macroDict = {}

operandRegexDict = {
    r'[rR$][-+]?[0-9]+'  : "register",
    r'[-+]?[0-9]+'       : "decimal immediate",
    r'\.[a-zA-Z0-9-_]+'  : "label",
    r'~[+-]?[0-9]+'      : "relative address",
    r'%[a-zA-Z0-9-_]+'   : "port",
    r'@[a-zA-Z0-9-_]+'   : "macro",
    r'[mM#][0-9]+'       : "heap pointer",

    r'0[xX][0-9a-fA-F]+' : "hex immediate",
    r'0[bB][01]+'        : "binary immediate",

    r'SP'                : "stack pointer",
    r'PC'                : "program counter",    
}


escapeCodeDict = {
    "\\b":8,
    "\\t":9,
    "\\n":10,
    "\\v":11,
    "\\f":12,
    "\\r":13,
    "\\\\":92,
    "\\'":39,
    "\\\"":34,
    "\\0":0,
}


class Opcode:
    string = ""
    type = ""

    def __init__(self, str):
        self.string = str
    def __str__(self):
        return self.string
    
    def __bytes__(self):
        self.data['string'] = self.string
        self.data['type'] = self.type
        return str(self.data).encode('utf-8')
    
    def fromBase64(self, data_bytes):
        self.data = ast.literal_eval(data_bytes.decode('utf-8'))
        self.string = self.data['string']
        self.type = self.data['type']

class Operand:
    string = ""
    type = ""

    data = {
        'string': "",
        'type': ""
    }

    def __init__(self, str):
        self.string = str
    def __init__(self, str, optype):
        self.string = str
        self.type = optype
    def __str__(self):
        return self.string
    
    def __bytes__(self):
        self.data['string'] = self.string
        self.data['type'] = self.type
        return str(self.data).encode('utf-8')
    
    def fromBase64(self, data_bytes):
        self.data = ast.literal_eval(data_bytes.decode('utf-8'))
        self.string = self.data['string']
        self.type = self.data['type']

class Line:
    string = ''
    linetype = 'unknown'
    opcode = 'unknown'
    
    ogLineNum = 0
    realLineNum = 0

    operands = []
    tokens = []

    data = {
        'string': '',
        'linetype': 'unknown',
        'opcode': 'unknown',

        'tokens': [],
        'operands': [],
        
        'ogLineNum': 0,
        'realLineNum': 0
    }
    

    

    def __init__(self, line:str, lineNum:int):
        self.string = line
        self.ogLineNum = lineNum
    

    def __str__(self):
        return self.string
    

    def __bytes__(self):

        self.data['string'] = self.string
        self.data['linetype'] = self.linetype
        self.data['tokens'] = self.tokens
        self.data['ogLineNum'] = self.ogLineNum
        self.data['realLineNum'] = self.realLineNum

        if type(self.opcode) == Opcode:
            self.data['opcode'] = bytes(self.opcode)
        else:
            self.data['opcode'] = self.opcode

        #for operand in self.operands:
        #    if type(operand) == Operand:
        #        self.data['operands'].append(bytes(operand))
        #    else:
        #        self.data['operands'].append(operand)
        self.data['operands'] = [bytes(operand) if (type(operand) == Operand) else operand for operand in self.operands]

        return str(self.data).encode('utf-8')
        #TODO: encode operands and opcodes properly
    
    def fromBytes(self, line_bytes):
        self.data = ast.literal_eval(line_bytes.decode('utf-8'))
        # TODO: decode operands and opcodes
        self.string = self.data['string']
        self.linetype = self.data['linetype']
        self.opcode = self.data['opcode']
        self.tokens = self.data['tokens']
        self.operands = self.data['operands']
        self.ogLineNum = self.data['ogLineNum']
        self.realLineNum = self.data['realLineNum']
    



    def lex(self):
        opcode = ""
        operands = []
        if self.string.strip() != "":
        
            #print(self.string) # DEBUG LINE
            pieces = self.string.split()
            opcode = pieces[0].strip()      # pretty self-explanitory.
    
            # now do operand lexing
            operands = []
            listRegex = r"\[.*?\]"
            operandRegex = r"'.'|'..'|[.$%@#RrMm]?[A-Za-z0-9-_]+|~[+-]?[0-9]+"
            operandsString = " ".join(pieces[1:])
            isList = False # this might be useful one day
            result = re.fullmatch(listRegex, operandsString)
            if type(result) == re.match:
                operandsString = operandsString[1:-1]
                isList = True                                
            try:   
                result = re.finditer(operandRegex, operandsString)
                for x in result:
                    operands.append(x.group(0))
            except IndexError:
                pass
        operands.insert(0, opcode)
        self.tokens = operands

    def parse(self):
    
        global labelDict,macroDict

        outputOperands = []

        match self.tokens[0][0], self.tokens[0].lower():
            case ('.', *tok):
                self.linetype = 'label'
                try:
                    labelDict[tok[0]]
                    raise Exception(f'URCL Error on line {self.ogLineNum}: Duplicate label name "{tok}"')
                except KeyError:
                    labelDict[tok[0]] = self.ogLineNum
            case ('@', *tok):
                self.linetype = 'macro'
                try:
                    macroDict[tok]
                    raise Exception(f'URCL Error on line {self.ogLineNum}: Duplicate label name "{tok}"')
                except KeyError:
                    macroDict[tok] = self.ogLineNum
            case (*char, 'dw'):
                self.linetype = 'dw'
            case (*char, 'bits'):
                self.linetype = 'header'
            case (*char, 'minreg'):
                self.linetype = 'header'
            case (*char, 'minheap'):
                self.linetype = 'header'
            case (*char, 'run'):
                self.linetype = 'header'
            case (*char, 'minstack'):
                self.linetype = 'header'
            case _:
                try:
                    urcl_rules.urclOperationLengths[self.tokens[0].lower()]
                    self.linetype = 'instruction'
                except KeyError:
                    raise Exception(f'Error on line {self.ogLineNum}: "{self.string}": Unrecognized instruction "{self.tokens[0]}"')


        for operand in self.tokens[1:]:
            operand = operand.strip()
            validOperand = False
            for index,pattern in enumerate(operandRegexDict):
                regex = re.fullmatch(pattern, operand)
                
                #print(f"{pattern} {operand} {regex}")
                
                if type(regex) == re.Match:
                    validOperand = True
                    opType = operandRegexDict[pattern]
                    outputOperands.append(Operand(operand, opType))
                    break

            
            if not validOperand:
                raise Exception(f'Error on line {self.ogLineNum}: "{self.string}": Unrecognized operand "{operand}"')
            # TODO: check if operand labels and macros are valid (this probably has to be done in a different Line function)
        self.operands = outputOperands


def info():
    print('Cleans URCL code')
    print('')
    print('Available options:')
    print('\t--o <file_path> : declare output file path (default is URCL.py/output/out.urcl)')
    print('\t--n <command> : next URCL.py command to run in chain (NOT IMPLEMENTED)')
    print('')
    print('\t-h : display this message')
    print('\t-c : disable extra lexing and parsing info for compiler')
    return

def clean(file, options=[]):

    global compiler_extras, labelDict, macroDict

    outFile = './output/out.urcl'                                       # default output file
    if file == "":                                                      # if file is blank just print info and exit
        info()
        return
    
    # argument handling loop
    endCommand = ""
    for c,v in enumerate(options):                          
        if v.lower() == '--o':
            try:
                outFile = options[c+1].strip()                                  # argument immediately after -o should be a file path
                if not (os.path.isfile(outFile)):
                    raise Exception(f'Error parsing command: "{outFile}" is not a valid file path')  
            except IndexError:
                raise Exception('Error parsing command: -o flag used but no output path provided')
        
        if v.lower() == '-h':
            info()
            return
        if v.lower() == '-c':
            compiler_extras = False

        if v.lower() == '-e':
            try:
                endCommand = options[c+1]
            except IndexError:
                raise Exception('Error parsing command: -e flag used but no command provided')
    
    # open file and read it as string
    if os.path.isfile(file):
        with open(file, 'r') as f:
            codeString = f.read()
    else:
        print('Error parsing command: no source file provided.')
        return 'error'


    # finds all strings in urcl code and replaces them with a key value (&1, &2, etc.)
    # once all strings are gone then cleaning can happen
    # strings have to be replaced at the end of the code
    strings = {}
    matches = re.finditer(r'".*?"', codeString)
    for count,m in enumerate(matches):
        string = m.group(0)
        key = f"&S_{count}"
        strings[key] = string
        codeString = codeString.replace(string, key, 1) # only replace 1 instance

    # i do the same with chars
    chars = {}
    matches = re.finditer(r"'.*?'", codeString)
    for count,m in enumerate(matches):
        char = m.group(0)
        key = f"&C_{count}"
        chars[key] = char
        codeString = codeString.replace(char, key, 1) # only replace 1 instance

    codeString = re.sub(r'\/\*.*\*\/', "", codeString) # remove all internal "multiline" comments (example: ADD /* comment */ R1 R2 R3)
    
    codeList = codeString.split("\n")  

    lines = []
    for i,line in enumerate(codeList):
        line = line.strip()                                             # remove leading and trailing whitespace

        if line != '':                                                  # check to make sure line isn't blank
            line = line.split('//')[0]                                     # anything after a comment is useless
            if line.strip() != '':                                   # make sure there is code before the comment
                line = line.strip()                               
                lineNum = i+1
                
                lineList = line.split(" ")                           # line[0] is everything before the comment
                outList = []
                for piece in lineList:
                    piece = piece.strip()
                    if piece != '':
                        outList.append(piece)
                outLine = " ".join(outList)
                x = outLine.find("/*")
                if x != -1:
                    lines.append(outLine[:x] + f"// {lineNum}" + outLine[x:]) # add original line number to output for more readable errors
                else:
                    lines.append(outLine + f"// {lineNum}")

    codeString = "\n".join(lines)
    
    # find and remove multiline comments
    matches = re.finditer(r'\/\*.*?\*\/', codeString, flags=re.DOTALL)
    for m in matches:
        text = m.group(0)
        # prevent putting two instructions on the same line
        if "\n" in text:
            codeString = codeString.replace(text, "\n")
        else:
            codeString = codeString.replace(text, "")

    # put chars and strings back
    # it may be smart to convert these to decimal immediates while i'm at it  
    
    for key in strings:
        immString = strings[key][1:-1]                                    # remove quote marks
        immList = []
        # find escape codes with regex
        matches = re.finditer(r'(\\[a-wy-zA-WY-Z0-9])|(\\x[0-9A-Fa-f]{2})', immString) # TODO: i still need to implement the \xXX escape codes
        for m in matches:
            escCode = m.group(0)
            try:
                charInt = escapeCodeDict[escCode]
                immString = immString.replace(escCode, chr(charInt))
            except KeyError:
                print(f"Warning: Invalid escape code \"{escCode}\", ignoring") # TODO: make this a cli flag on whether or not to ignore invalid escape codes

        for char in immString: 
            immList.append(str(ord(char)))     
                                 
        listString = f"[{' '.join(immList)}]"                               # this should output an array of decimal immediates equivalent to the bytes of the given string
        codeString = codeString.replace(key, listString)
 
    for key in chars:
        immChar = chars[key][1:-1]                                    # remove quote marks
        if (len(immChar) == 2)&(immChar[0] == '\\'):                    # replace escape codes
            try:
                imm = str(escapeCodeDict[immChar])
            except KeyError:
                print(f'Warning! ignored escape code \"{immChar}\"')
        else:
            imm = str(ord(immChar))
        codeString = codeString.replace(key, imm)

    # cleaning done, now all that's left to do is output (and optionally lex and parse code)

    codeList = codeString.split("\n")

    lines = []

    for index,line in enumerate(codeList):
        line = line.strip()
        temp = line.split("//")
        if temp[0].strip() != '':
            lines.append(Line(temp[0].strip(),int(temp[1])))

    


    if compiler_extras:

        extra_outFile = outFile.split("/") # split on forward slash
        extra_outFile[-1] = '.'+extra_outFile[-1]
        extra_outFile:str = '/'.join(extra_outFile)
        
        for line in lines:
            line.lex()
            line.parse()


        #print(lines)
        
        with open(extra_outFile, 'wb') as f:
            for line in lines:

                f.write(bytes(line))
                f.write("\n".encode('utf-8'))
    

    codeString = "\n".join([str(line)for line in lines])

    with open(outFile, 'w') as f:                                       # output cleaned code to file
        f.write(codeString)

    return outFile                                                      # return output file for other functions to reference
