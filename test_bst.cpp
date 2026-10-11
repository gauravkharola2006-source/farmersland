// Part 1 test: BST (field_bst). Build and run with: make test
#include <cassert>
#include <cstdio>
#include <iostream>
#include <sstream>
#include <vector>
#include "../field_bst.h"

using namespace std;

static string captureList(Field *root) {
    ostringstream buf;
    streambuf *old = cout.rdbuf(buf.rdbuf());
    listFields(root);
    cout.rdbuf(old);
    return buf.str();
}

int main() {
    Field *root = nullptr;
    assert(searchField(root, 1) == nullptr);
    assert(captureList(root).empty());

    root = insertField(root, 50, 30, "wheat");
    root = insertField(root, 30, 45, "maize");
    root = insertField(root, 70, 20, "rice");
    root = insertField(root, 20, 70, "soybean");
    root = insertField(root, 40, 25, "barley");
    root = insertField(root, 60, 55, "cotton");
    root = insertField(root, 80, 10, "sugarcane");
    assert(searchField(root, 40) && searchField(root, 40)->crop == "barley");
    assert(searchField(root, 99) == nullptr);

    // in-order output must be sorted by ID
    string out = captureList(root);
    assert(out.find("ID: 20") < out.find("ID: 30"));
    assert(out.find("ID: 30") < out.find("ID: 40"));
    assert(out.find("ID: 70") < out.find("ID: 80"));
    assert(out.find("Dryness: 70") != string::npos);     // field 50: 100 - 30

    // update instead of duplicate
    root = insertField(root, 50, 90, "WHEAT2");
    assert(searchField(root, 50)->moisture == 90 && searchField(root, 50)->crop == "WHEAT2");

    // collect_fields_into_array: count + in-order fill + dryness
    int n = collect_fields_into_array(root, nullptr);
    assert(n == 7);
    vector<FieldItem> arr(n);
    assert(collect_fields_into_array(root, arr.data()) == 7);
    for (int i = 1; i < n; i++) assert(arr[i - 1].id < arr[i].id);
    assert(arr[0].id == 20 && arr[0].dryness == 30);

    // save and load round trip
    const string tmp = "/tmp/_bst_roundtrip.txt";
    assert(save_fields(root, tmp) == 0);
    Field *loaded = load_fields(tmp);
    assert(collect_fields_into_array(loaded, nullptr) == 7);
    assert(searchField(loaded, 50)->moisture == 90);
    assert(searchField(loaded, 20)->crop == "soybean");
    bst_free(loaded);
    remove(tmp.c_str());
    assert(load_fields("/tmp/definitely_missing_file.txt") == nullptr);
    assert(save_fields(root, "/nonexistent_dir/x.txt") == -1);

    // delete: leaf, one child, two children, root, missing id
    root = removeField(root, 20);   assert(searchField(root, 20) == nullptr);
    root = removeField(root, 80);
    root = removeField(root, 70);   assert(searchField(root, 70) == nullptr && searchField(root, 60));
    root = insertField(root, 20, 10, "oats");
    root = removeField(root, 30);   assert(searchField(root, 20) && searchField(root, 40));
    root = removeField(root, 50);   assert(searchField(root, 50) == nullptr);
    root = removeField(root, 12345);

    // long crop names are cut
    root = insertField(root, 5, 50, string(200, 'x'));
    assert(searchField(root, 5)->crop.size() == (size_t)(MAX_CROP_LEN - 1));

    bst_free(root);
    cout << "Part 1 (BST): all tests passed\n";
    return 0;
}
