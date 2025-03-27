/*
 * stringutils.c: Collection of string utilities I've written over time
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

#include <stdlib.h>
#include <string.h>

char* cutString(char* input, size_t start, size_t end) {
  // cut out a section from input string between start and end indeces (start and end index are both cut out)
  
  // sanity check inputs
  if (start >= end) {
    return NULL;
  }
  size_t originalLen = strlen(input);
  if (start > originalLen - 1 || end > originalLen - 1) { // index math
    return NULL;
  }

  // calculate size of new buffer
  size_t newSize = start + (originalLen - end);
  // create new buffer
  char* outputString = malloc(sizeof(char) * newSize);
  // copy starting part to output
  size_t index = 0;
  while (index < start) {
    outputString[index] = input[index];
    index++;
  }
  // index now points to the first character to be skipped
  while (index < newSize - 1) { // convert byte size to pointer
    // prepare yourself im about to do some really funny pointer math
    outputString[index] = input[index-start+end+1]; // instead of pointing to the first character outside of start section,
    // index now points to the first character inside the end section (end pointer + 1)
    index++;
  }
  // write null terminator
  outputString[index] = 0;
  return outputString;
}

char* replaceString(char* base, char* replacement, size_t start, size_t end) {
  // replace a section in base string with replacement string, resizing base as needed
}

char* insertString(char* base, char* insert, size_t index) {
  // insert string into base string starting at index
}