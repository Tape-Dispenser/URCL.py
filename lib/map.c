/*
 * map.c: Map library written for passphrase generator
 * Copyright (C) 2025, Ada Gramiak, <adadispenser@gmail.com>
 *   Special thanks to: Stella
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
#include <stdio.h>
#include <string.h>

typedef struct CharMap {
  char* keys;
  char* values;
} CharMap;

// create a new map with empty lists (map constructor)
struct CharMap empty_map() {
  struct CharMap map;
  map.keys = malloc(sizeof(char));
  map.keys[0] = 0;
  map.values = malloc(sizeof(char));
  map.values[0] = 0;
  return map;
}

// create a new map from two input strings (map constructor)
struct CharMap full_map(char* keys, char* values) {
  struct CharMap map;
  if (strlen(keys) != strlen(values)) {
    map.keys = 0;
    map.values = 0;
    return map;
  }

  map.keys = malloc((strlen(keys) + 1) * sizeof(char));
  map.values = malloc((strlen(values) + 1) * sizeof(char));

  size_t len = strlen(keys);

  size_t index = 0;
  while (index < len) {
    map.keys[index] = keys[index];
    map.values[index] = values[index];
    index++;
  }
  // null terminator will be copied over in the loop
  return map;
}

// get value (input key)
int map_get(struct CharMap* map, char key, char* output) {
  // returns 0 on success
  // returns -1 if key-value pair does not exist in map
  int index = 0;
  while (index < strlen(map->keys)) {
    if (map->keys[index] == key) {
      *output = map->values[index];
      return 0;
    }
    index++;
  }
  return -1;
}

// add key-value pair (input new key and new value)
int map_add(struct CharMap* map, char key, char value) {
  // returns 0 on success
  // returns -1 if key-value pair already exists in map
  char temp;
  if (map_get(map, key, &temp) == 0) {
    return -1;
  }
  int map_len = strlen(map->keys);
  map->keys = realloc(map->keys, (map_len + 2) * sizeof(char)); // map_len + 2 accounts for null terminator and the character to be added
  if (map->keys == 0) {
    printf("Error while reallocating memory for keys string!\n");
    return -1;
  }
  map->keys[map_len] = key; // add key to keys
  map->keys[map_len + 1] = 0; // add null terminator to keys
  map->values = realloc(map->values, (map_len + 2) * sizeof(char));
  if (map->keys == 0) {
    printf("Error while reallocating memory for values string!\n");
    return -1;
  }
  map->values[map_len] = value;
  map->values[map_len + 1] = 0;
  return 0;
}

// edit value in pair (input key and new value)
int map_update(struct CharMap* map, char key, char value) {
  // returns 0 on success
  // returns -1 if key-value pair does not exist in map
  int index = 0;
  while (index < strlen(map->keys)) {
    if (map->keys[index] == key) {
      map->values[index] = value;
      return 0;
    }
    index++;
  }
  return -1;
}

// remove key-value pair (input key to remove)
int map_delete(struct CharMap* map, char key) {
  // returns 0 on success
  // returns -1 if key-value pair does not exist in map
  int index = 0;
  while (index < strlen(map->keys)) {
    if (!map->keys[index] == key) {
      index++;
      continue;
    }
    // get index of last entry (strlen)
    int last_entry = strlen(map->keys);
    // overwrite the entry at index with the last entry in the map
    map->keys[index] = map->keys[last_entry];
    map->values[index] = map->values[last_entry];
    // overwrite the duplicate entry at the end of the map with a null terminator
    map->keys[last_entry] = 0;
    map->values[last_entry] = 0;
    // shrink allocated memory size for string
    // original strlen will point to the last character of the original string, which is where the new null terminator will go,
    // therefore no pointer math is needed for malloc
    map->keys = realloc(map->keys, last_entry * sizeof(char));
    if (map->keys == 0) {
      printf("Error while reallocating memory for keys string!\n");
      return -1;
    }
    map->values = realloc(map->values, last_entry * sizeof(char));
    if (map->keys == 0) {
      printf("Error while reallocating memory for values string!\n");
      return -1;
    }
    return 0;
  }
  return -1;
}
