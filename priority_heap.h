#ifndef PRIORITY_HEAP_H
#define PRIORITY_HEAP_H

#include "field_bst.h"

constexpr int HEAP_CAPACITY = 1024;

// Binary max-heap ordered by dryness
class Heap {
public:
    Heap();
    int insert(const FieldItem &item);        // 0 = ok, -1 = full
    int extract_max(FieldItem &out_item);     // 0 = ok, -1 = empty
    void build_from_array(FieldItem *arr, int n);

private:
    FieldItem data[HEAP_CAPACITY];
    int size;
    void sift_down(int i);
};

#endif
