#ifndef MAP_H
#define MAP_H

typedef struct CharMap {
    char* keys;
    char* values;
} CharMap;

struct CharMap empty_map();

struct CharMap full_map(char* keys, char* values);

int map_add(struct CharMap* map, char key, char value);

int map_get(struct CharMap* map, char key, char* output);

int map_update(struct CharMap* map, char key, char value);

int map_delete(struct CharMap* map, char key);

#endif
