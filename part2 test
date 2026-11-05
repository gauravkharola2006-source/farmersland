// Part 2 test: Max-Heap + circular Queue, and the heap -> queue scheduling sequence. Run: make test
#include <cassert>
#include <iostream>
#include <vector>
#include "../priority_heap.h"
#include "../irrigation_queue.h"

using namespace std;

static FieldItem item(int id, int dryness) { FieldItem f; f.id = id; f.dryness = dryness; f.crop = "c"; return f; }

int main() {
    // ---- Heap ----
    Heap h;
    FieldItem out;
    assert(h.extract_max(out) == -1);                         // empty

    // build_from_array (bottom-up heapify): must come out in descending dryness
    FieldItem arr[5] = { item(1, 10), item(2, 80), item(3, 60), item(4, 90), item(5, 40) };
    h.build_from_array(arr, 5);
    int expect_ids[5] = {4, 2, 3, 5, 1};
    int expect_dry[5] = {90, 80, 60, 40, 10};
    for (int i = 0; i < 5; i++) {
        assert(h.extract_max(out) == 0);
        assert(out.id == expect_ids[i] && out.dryness == expect_dry[i]);
    }
    assert(h.extract_max(out) == -1);

    // insert one by one gives the same result
    Heap h2;
    for (int i = 0; i < 5; i++) assert(h2.insert(arr[i]) == 0);
    for (int i = 0; i < 5; i++) { assert(h2.extract_max(out) == 0); assert(out.dryness == expect_dry[i]); }

    // capacity: 1024 inserts fit, the 1025th is refused
    Heap h3;
    for (int i = 0; i < HEAP_CAPACITY; i++) assert(h3.insert(item(i, i % 100)) == 0);
    assert(h3.insert(item(9999, 5)) == -1);
    int last = 1000;
    for (int i = 0; i < HEAP_CAPACITY; i++) { assert(h3.extract_max(out) == 0); assert(out.dryness <= last); last = out.dryness; }

    // ---- Queue ----
    Queue q;
    int x = -1;
    assert(q.dequeue(x) == -1 && q.peek(x) == -1);
    q.enqueue(10); q.enqueue(20); q.enqueue(30);
    assert(q.peek(x) == 0 && x == 10);
    assert(q.dequeue(x) == 0 && x == 10);
    assert(q.dequeue(x) == 0 && x == 20);
    assert(q.dequeue(x) == 0 && x == 30);
    assert(q.dequeue(x) == -1);

    Queue q2;                                                 // full + wrap-around
    for (int i = 0; i < QUEUE_CAPACITY; i++) assert(q2.enqueue(i) == 0);
    assert(q2.enqueue(999) == -1);
    for (int i = 0; i < 100; i++) { assert(q2.dequeue(x) == 0); assert(x == i); }
    for (int i = 0; i < 100; i++) assert(q2.enqueue(1000 + i) == 0);
    for (int i = 100; i < QUEUE_CAPACITY; i++) { assert(q2.dequeue(x) == 0); assert(x == i); }
    for (int i = 0; i < 100; i++) { assert(q2.dequeue(x) == 0); assert(x == 1000 + i); }
    assert(q2.dequeue(x) == -1);

    // ---- Heap feeds Queue: driest field is irrigated first ----
    Heap h4; Queue sched;
    h4.build_from_array(arr, 5);
    while (h4.extract_max(out) == 0) assert(sched.enqueue(out.id) == 0);
    for (int i = 0; i < 5; i++) { assert(sched.dequeue(x) == 0); assert(x == expect_ids[i]); }

    cout << "Part 2 (Heap + Queue): all tests passed\n";
    return 0;
}
