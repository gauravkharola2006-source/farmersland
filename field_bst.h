#ifndef FIELD_BST_H
#define FIELD_BST_H

#include <string>

constexpr int MAX_CROP_LEN = 64;

struct Field {
    int fieldID;
    int moisture;
    std::string crop;
    Field *left, *right;
};

Field* insertField(Field *root, int id, int moisture, const std::string &crop);
Field* removeField(Field *root, int id);
Field* searchField(Field *root, int id);
void listFields(Field *root);
void bst_free(Field *root);

int save_fields(Field *root, const std::string &filename);
Field* load_fields(const std::string &filename);

struct FieldItem {
    int id;
    int dryness;
    std::string crop;
};

// Pass nullptr to only count the fields; otherwise fills out_array in-order.
int collect_fields_into_array(Field *root, FieldItem *out_array);

#endif
