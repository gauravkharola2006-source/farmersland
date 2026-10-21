#include "irrigation_queue.h"

Queue::Queue() : head(0), tail(0), size(0) {
    for (int i = 0; i < QUEUE_CAPACITY; ++i) data[i] = 0;
}

int Queue::enqueue(int fieldID) {
    if (size == QUEUE_CAPACITY) return -1;
    data[tail] = fieldID;
    tail = (tail + 1) % QUEUE_CAPACITY;
    size++;
    return 0;
}

int Queue::dequeue(int &out_fieldID) {
    if (size == 0) return -1;
    out_fieldID = data[head];
    head = (head + 1) % QUEUE_CAPACITY;
    size--;
    return 0;
}

int Queue::peek(int &out_fieldID) const {
    if (size == 0) return -1;
    out_fieldID = data[head];
    return 0;
}
