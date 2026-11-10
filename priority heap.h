#include <utility>
#include "priority_heap.h"

Heap::Heap() : size(0) {}

int Heap::insert(const FieldItem &item) {
    if (size >= HEAP_CAPACITY) return -1;
    int i = size++;
    data[i] = item;
    while (i > 0) {
        int p = (i - 1) / 2;
        if (data[p].dryness >= data[i].dryness) break;
        std::swap(data[p], data[i]);
        i = p;
    }
    return 0;
}

void Heap::sift_down(int i) {
    while (true) {
        int l = 2 * i + 1, r = 2 * i + 2, largest = i;
        if (l < size && data[l].dryness > data[largest].dryness) largest = l;
        if (r < size && data[r].dryness > data[largest].dryness) largest = r;
        if (largest == i) break;
        std::swap(data[i], data[largest]);
        i = largest;
    }
}

int Heap::extract_max(FieldItem &out_item) {
    if (size == 0) return -1;
    out_item = data[0];
    size--;
    if (size > 0) data[0] = data[size];
    sift_down(0);
    return 0;
}

void Heap::build_from_array(FieldItem *arr, int n) {
    if (n > HEAP_CAPACITY) n = HEAP_CAPACITY;
    for (int i = 0; i < n; ++i) data[i] = arr[i];
    size = n;
    for (int i = (size / 2) - 1; i >= 0; --i) sift_down(i);   // bottom-up heapify, O(n)
}
