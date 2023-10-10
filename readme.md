Command line syntax:

```
./URCL.py [command] [file] [options]
./URCL.py [command] : returns info about command
./URCL.py : returns info about toolkit
```

Commands List:
  clean: cleans out whitespace, comments, and strings
    options:
      -h : display options list and info about command
      -o <path> : delclare output file (default is ./out.urcl)
      -n : preserve original line number (used for debugging)
      -a : only allow ascii characters in strings
