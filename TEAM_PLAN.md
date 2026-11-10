# Team Plan - Smart Farming System (C++)

Two people, two parts. The three work items from the team report are divided like this:

| | Part 1 - Core Program | Part 2 - Tanvi Tripathi |
|---|---|---|
| Work items | Core Program (main logic, CLI menu, integration, sample-input testing) | Scheduling & Queue Module, and Prediction & Documentation |
| Files owned | `main.cpp`, `field_bst.*`, `pipeline_bfs.*`, `Makefile`, `server.py`, `ui/`, `tests/` (BST, BFS, smoke test), sample data | `priority_heap.*`, `irrigation_queue.*`, `scheduler.*`, `prediction.*`, `planner.*`, `README.md` |
| DSA | Binary Search Tree, Graph + BFS | Max-Heap, Circular Queue, Greedy planner |
| Menu options | 1, 2, 3, 10, 11, 12 and the whole menu loop | 4, 5, 6, 7, 8, 9, 13 |

Why the BST, BFS and UI are in Part 1: the core program is what connects everything, and these three are not listed in the report under the other work items.

## The agreement between the two parts (do not change names or signatures without telling each other)

**Part 1 provides** (`field_bst.h`):
```cpp
struct Field     { int fieldID; int moisture; std::string crop; Field *left, *right; };
struct FieldItem { int id; int dryness; std::string crop; };
int collect_fields_into_array(Field *root, FieldItem *out_array);   // nullptr = only count
```

**Part 2 provides** (called from `main.cpp`):
```cpp
// irrigation_queue.h
class Queue { int enqueue(int fieldID); int dequeue(int &out); int peek(int &out) const; };
// priority_heap.h
class Heap  { int insert(const FieldItem &item); int extract_max(FieldItem &out); void build_from_array(FieldItem *arr, int n); };
// prediction.h
double predict_yield(int moisture_percent);
// planner.h
int plan_irrigation(Field *root, int days, int per_day_limit, std::vector<std::vector<int>> &out_schedule);
```
Part 2's heap and planner use Part 1's `Field`, `FieldItem` and `collect_fields_into_array`.

## Presentation split (suggestion)

- Part 1: system overview and menu demo, BST (insert, delete, in-order), BFS on the pipeline network, how main.cpp connects the modules, the web UI.
- Part 2: heap and why dryness is the priority, circular queue, yield formula, the irrigation planner (greedy, and what DP would add), complexity table.
- Both: the full demo flow - load sample fields, list, build heap, extract driest, enqueue and dequeue, predict, plan 3 days, pipeline query.
