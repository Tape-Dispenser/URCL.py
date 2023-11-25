Command line syntax:

```
cd <directory to project root folder>

./URCL.py [command] [file] [options]
./URCL.py [command] : returns info about command
./URCL.py : returns info about toolkit
```

Commands List:
  clean: cleans out whitespace, comments, and strings
    options:
      -h : display options list and info about command
      -o <path.urcl> : delclare output file (default is ./out.urcl)
      -n : preserve original line number (used for debugging)
      -a : only allow ascii characters in strings

Supported Macros:
  `@IMPORT <path.urcl> <name>`: imports all labels in <path.urcl> as `.<name>.label` (not implemented)
  `@DEFINE <A> <B>`: defines <A> as a macro equivalent to <B>. If <B> contains spaces or newlines, it must be a string. (not implemented)
  `@DEBUG`: pauses execution when code reaches this line. (not implemented)
  `@DEBUG onwrite <A>`: pauses execution when memory address, register, or port <A> is written to. (not implemented)
  `@DEBUG onread <A>`: pauses execution when memory address, register, or port <A> is read from. (not implemented)