#include <iostream>
#include <fstream>
#include "field_bst.h"

static Field* create_field_node(int id, int moisture, const std::string &crop) {
    Field *f = new Field;
    f->fieldID = id;
    f->moisture = moisture;
    f->crop = crop.substr(0, MAX_CROP_LEN - 1);
    f->left = f->right = nullptr;
    return f;
}

Field* insertField(Field *root, int id, int moisture, const std::string &crop) {
    if (!root) return create_field_node(id, moisture, crop);
    if (id < root->fieldID) root->left = insertField(root->left, id, moisture, crop);
    else if (id > root->fieldID) root->right = insertField(root->right, id, moisture, crop);
    else {
        root->moisture = moisture;
        root->crop = crop.substr(0, MAX_CROP_LEN - 1);
    }
    return root;
}

Field* searchField(Field *root, int id) {
    if (!root) return nullptr;
    if (id == root->fieldID) return root;
    if (id < root->fieldID) return searchField(root->left, id);
    return searchField(root->right, id);
}

static Field* find_min(Field *r) {
    while (r && r->left) r = r->left;
    return r;
}

Field* removeField(Field *root, int id) {
    if (!root) return nullptr;
    if (id < root->fieldID) root->left = removeField(root->left, id);
    else if (id > root->fieldID) root->right = removeField(root->right, id);
    else {
        if (!root->left) { Field *t = root->right; delete root; return t; }
        if (!root->right) { Field *t = root->left; delete root; return t; }
        Field *minr = find_min(root->right);
        root->fieldID = minr->fieldID;
        root->moisture = minr->moisture;
        root->crop = minr->crop;
        root->right = removeField(root->right, minr->fieldID);
    }
    return root;
}

void listFields(Field *root) {
    if (!root) return;
    listFields(root->left);
    std::cout << "ID: " << root->fieldID
              << " | Moisture: " << root->moisture
              << " | Dryness: " << 100 - root->moisture
              << " | Crop: " << root->crop << "\n";
    listFields(root->right);
}

void bst_free(Field *root) {
    if (!root) return;
    bst_free(root->left);
    bst_free(root->right);
    delete root;
}

// In-order helper (replaces the GCC-only nested function used in the C version)
static void save_rec(Field *r, std::ofstream &out) {
    if (!r) return;
    save_rec(r->left, out);
    out << r->fieldID << ' ' << r->moisture << ' ' << r->crop << '\n';
    save_rec(r->right, out);
}

int save_fields(Field *root, const std::string &filename) {
    std::ofstream out(filename);
    if (!out) return -1;
    save_rec(root, out);
    return 0;
}

Field* load_fields(const std::string &filename) {
    std::ifstream in(filename);
    if (!in) return nullptr;
    Field *root = nullptr;
    int id, moisture;
    std::string crop;
    while (in >> id >> moisture >> crop) {
        root = insertField(root, id, moisture, crop);
    }
    return root;
}

static void collect_rec(Field *r, FieldItem *out_array, int &idx) {
    if (!r) return;
    collect_rec(r->left, out_array, idx);
    if (out_array) {
        out_array[idx].id = r->fieldID;
        out_array[idx].dryness = 100 - r->moisture;
        out_array[idx].crop = r->crop;
    }
    idx++;
    collect_rec(r->right, out_array, idx);
}

int collect_fields_into_array(Field *root, FieldItem *out_array) {
    int idx = 0;
    collect_rec(root, out_array, idx);
    return idx;
}
