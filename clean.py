import os,re,base64
import urcl_rules

labelDict = {}
macroDict = {}
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

class Operand:
    string = ""
    type = ""

    def __init__(self, str):
        self.string = str
    def __str__(self):
        return self.string

class Line:
        
    string = ""
    tokens = []
    originalLineNum = 0
    realLineNum = 0
    opcode = Opcode("")
    operands = []
    
    
    
    def __init__(self, line, lineNum):
        self.string = line
        self.originalLineNum = lineNum
    def __str__(self):
        return self.string
    
    def lex(self):
        opcode = ""
        operands = []
        if self.string.strip() != "":
        
            #print(self.string) # DEBUG LINE
            pieces = self.string.split()
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
                pass
            if inList:
                pass # this seemed like it might be useful some time    
        self.tokens = operands.insert(0, opcode)

    def parse(self):
        opcode = self.tokens[0]
        operands = self.tokens[1:]
    
        global labelDict,macroDict

        outputOperands = []

        for operand in operands:
            if opcode[0] == '.':
                linetype = 'label'
                labelEntry = (opcode, self.originalLineNum)
                labelDict.append(labelEntry)
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
                    print(f'Error on line {self.originalLineNum}: "{f"{opcode} {operand}"}": Unrecognized instruction "{opcode}"')
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

                regex = re.fullmatch(r'0[xX][0-9]+', operand)               # check for hex immediate    
                if type(regex) == re.match:
                    outputOperands.append( (operand,'hex immediate') )
                    continue

                regex = re.fullmatch(r'0[bB][01]+', operand)                # check for binary immediate
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
                        labelDict[operand]
                        outputOperands.append(operand, '')
                        continue
                    except ValueError:
                        print(f'Error: Undefined label "{operand}" referenced on line {self.originalLineNum}')
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

                print(f'Error: Unrecognized operand "{operand}" on line {self.originalLineNum}')
                return('error')
        return (linetype, outputOperands)
        

def info():
    print('Cleans URCL code')
    print('Removes comments, whitespace, and more!')
    print('Available options:')
    print('\t-o <file_path> : declare output file path (default is URCL.py/output/out.urcl)')
    print('\t-h : display this message')
    print('\t-e <command> : command to run next in chain')
    return

def clean(file, options=[]):

    outFile = './output/out.urcl'                                       # default output file
    if file == "":                                                      # if file is blank just print info and exit
        info()
        return 'success'
    
    # argument handling loop
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
        if v.lower() == '-e':
            try:
                endCommand = options[c+1]
            except IndexError:
                print('Error parsing command: -e flag used but no command provided')
                return 'error'
    
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
    
    codeList = codeString.split("\n")

    lines = []
    
    for i,line in enumerate(codeList):
        temp = line.split("//")
        if temp[0].strip() != '':
            lines.append(Line(temp[0].strip(),int(temp[1])))
    for line in lines:
        # lexing time :)
        line.lex()

    codeString = "\n".join([str(line)for line in lines]) # some cool one line shit i learned a couple years ago

    with open(outFile, 'w') as f:                                       # output cleaned code to file
        f.write(codeString)
    return outFile                                                      # return output file for other functions to reference