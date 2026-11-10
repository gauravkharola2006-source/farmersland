#ifndef IRRIGATION_QUEUE_H
#define IRRIGATION_QUEUE_H

constexpr int QUEUE_CAPACITY = 256;

// Circular FIFO queue (fixed capacity)
class Queue {
public:
    Queue();
    int enqueue(int fieldID);          // 0 = ok, -1 = full
    int dequeue(int &out_fieldID);     // 0 = ok, -1 = empty
    int peek(int &out_fieldID) const;  // 0 = ok, -1 = empty

private:
    int data[QUEUE_CAPACITY];
    int head, tail, size;
};

#endif
