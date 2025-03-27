/*
 * clean.c: URCL Code cleaner, for use as the first step in a transpiler toolchain,
 *          or as a standalone program
 * Copyright (C) 2025, Ada Gramiak, <adadispenser@gmail.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <getopt.h>
#include <string.h>
#include <errno.h>
#include "lib/stringutils.h"




// ############################  OPTIONS  ############################

void help() {
  puts("clean: clean [-h] [-o path] infile");
  puts("  Clean up a urcl file by removing unnecessary comments and whitespace. Resulting code is output to stdout.");
  puts("");
  puts("  Options:");
  puts("    -h:    print this menu.");
  puts("    -n:    add original line numbers to the output code");
}

int lineNums = 0;


// #############################   CODE  #############################

char* clean(char* urclCode) {
  char* workingCopy = malloc(sizeof(char)*strlen(urclCode));
  strcpy(workingCopy, urclCode);

  // step one: add line numbers

  // step one:   replace all strings with a replacement key (ex. &1, &2, &3, etc.), remove all multiline comments
  // source string must be put into a map

  int inString = 0;
  int inComment = 0;
  int stringID = 0;
  char* currentString;
  int stringIndex;
  size_t tokenStart;
  size_t tokenEnd;

  size_t index = 0;
  char c = urclCode[index];
  while (c != 0) {
    c = urclCode[index];
    if (inString == 1) {
      currentString[stringIndex] = c;
      stringIndex++;
      currentString = realloc(currentString, (stringIndex + 1) * sizeof(char));
      if (c == '"' || c == '\'') {
        char prev = urclCode[index - 1];
        if (prev != '\\') {
          inString = 0;
          currentString[stringIndex] = 0;
          tokenEnd = index;
          printf("Found a string literal %s starting at character index %lu and ending at %lu.\n", currentString, tokenStart, tokenEnd);
          // add string to map and replace with the string id (&1, &2, &3, etc.)
        }
      }
      
      
    } else if (inComment == 1) {
      if (c == '/' && urclCode[index-1] == '*') {
        inComment = 0;
        tokenEnd = index;
        // delete comment
        urclCode = cutString(urclCode, tokenStart, tokenEnd);
        index = tokenStart;
        continue; // no need to increment index, it already points to the character immediately after the (now deleted) comment
      }


    } else {
      switch (c) {
        case '"':
        case '\'':
          inString = 1;
          currentString = malloc(2 * sizeof(char));
          stringIndex = 0;
          currentString[stringIndex] = c;
          stringIndex++;
          tokenStart = index;
          break;
        case '*':
          if (urclCode[index-1] != '/') {
            break;
          }
          inComment = 1;
          tokenStart = index - 1; // make sure / in /* gets selected too
          break;
      }

    }  





    index++;
  }

  // step two:   add line numbers (ex. ADD R1 R2 R3 &L82)

  // step three: remove all inline "multiline" comments (example: ADD /* comment */ R1 R2 R3)

  // step four:  remove all multiline comments

  // step five:  remove all single line comments

  // step six:   remove all extra whitespace

  // step seven: put all characters and strings back

  // step eight: output code
  printf("%s\n", urclCode);

}


// #########################  MAIN FUNCTION  #########################

int main(int argc, char **argv) {
  int option;
  char* urclPath;
  char* temp_arg;

  // parse arguments
  while ((option = getopt(argc, argv, ":hno")) != -1) {
    
    switch (option) {
      case 'h': {
        help();
        exit(0);
      }
      case 'n': {
        lineNums = 1;
        break;
      }
      case ':': {
        printf("Option \'%c\' missing value.\n", optopt);
        exit(-1);
      }
      case '?': {
        printf("Unknown option \'%c\'\n", optopt);
        exit(-1);
      }
    }
  }
  if (argc - optind != 1) {
    printf("expected 1 file path input, got %u\n", argc-optind);
    exit(-1);
  }

  // read input file into string
  
  urclPath = malloc( sizeof(char) * (strlen(argv[optind]) + 1) );
  FILE* urclFile = NULL;
  urclFile = fopen(argv[optind], "r");
  if (urclFile == NULL) {
    printf("error no. %d while opening file \"%s\"\n", urclPath, errno);
  }
  puts("urcl file contents:");
  char c = 0;
  size_t index = 0;
  char* code = malloc(1 * sizeof(char));
  while (c != EOF) {
    c = fgetc(urclFile);
    code = realloc(code, (index + 2) * sizeof(char)); // plus one for the null terminator, plus two for index -> size conversion
    code[index] = c;
    index++; // index now points to the next free character
  }
  // write null terminator
  code[index] = 0;

  //printf("%s\n", code);
  fclose(urclFile);
  clean(code);
  exit(0);
}