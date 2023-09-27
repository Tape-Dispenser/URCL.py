import os,re

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

    # jank
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

    matches = re.finditer(r'\/\*.*?\*\/', codeString, flags=re.DOTALL)
    for m in matches:
        text = m.group(0)
        if "\n" in text:
            codeString = codeString.replace(text, "\n")
        else:
            codeString = codeString.replace(text, "")


    codeList = codeString.split("\n")  

    lines = []
    for i,line in enumerate(codeList):
        line = line.strip()                                             # remove leading and trailing whitespace
        if line != '':                                                  # check to make sure line isn't blank
            line = line.split('//')                                     # anything after a comment is useless
            if line[0] != '':                                           # make sure there is code before the comment
                lineout = line[0].strip()                               # add original line number to output for more readable errors
                lineNum = i+1
                
                lineList = line[0].split(" ")                           # line[0] is everything before the comment
                outList = []
                for piece in lineList:
                    piece = piece.strip()
                    if piece != '':
                        outList.append(piece)
                outLine = " ".join(outList)
                lines.append(outLine) 

    codeString = "\n".join(lines)
    #print(codeString)

    # put chars and strings back
    # it may be smart to convert these to decimal immediates while i'm at it
    
    for key in strings:
        codeString = codeString.replace(key,strings[key])

    for key in chars:
        codeString = codeString.replace(key,chars[key])

    with open(outFile, 'w') as f:                                       # output cleaned code to file
        f.write(codeString)                                      
    return outFile                                                      # return output file for other functions to reference