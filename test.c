#include <stdio.h>
#include <stddef.h>
#include "lib/stringutils.h"

int main() {
  char* base = "Hello, World!";
  char* replacement = "scape";
  char* new = replaceString(base, replacement, 4UL, 6UL);

  printf("replaced section in base string \"%s\", got \"%s\"\n", base, new);

  new = replaceString(base, "\n", 7UL, 11UL);
  printf("replaced section in base string \"%s\", got \"%s\"\n", base, new);

  return 0;
}