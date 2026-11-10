# Smart Farming System (C++17)

**Course:** BTECH T330 (PBL) | **Team:** Avengers
**Team members:** Gaurav Kharola (Team Lead, 2510011530) and Tanvi Tripathi (2510012053)
**Repository:** https://github.com/gauravkharola2006-source/farmersland.git

A smart farming management system that stores field records, schedules irrigation, predicts crop yield, plans irrigation over several days, and analyses pipeline routes. Everything is written in C++ with **hand-written data structures** (BST, circular queue, max-heap, graph + BFS).

## Features

- **Field Management**: add, update, remove, and list fields with a Binary Search Tree (BST)
- **Irrigation Queue**: circular FIFO queue that holds the order in which fields are irrigated
- **Priority Heap**: max-heap ordered by dryness (`100 - moisture`), so the driest field comes out first
- **Heap-to-Queue Scheduling**: rebuilds the heap from the current field data and moves the driest fields into the irrigation queue (menu option 13)
- **Yield Prediction**: relative yield estimated from soil moisture (best at 50% moisture, 0 at 0% and 100%)
- **Multi-Day Planning**: sorts fields by dryness and uses a greedy approach to build a day-wise plan; a field watered the previous day is skipped
- **Pipeline Network**: BFS finds the shortest distance (number of pipes) between two pipeline nodes
- **File Operations**: save and load field data as text files
- **Input Validation**: moisture (0-100), IDs, days and counts are checked; invalid or non-numeric input is rejected and asked again
- **Web UI**: HTML/CSS/JavaScript front end with a Python API server

## Data Structures & Algorithms Used

| Module | DSA | Key operations | Complexity |
|---|---|---|---|
| `field_bst.cpp` | Binary Search Tree | insert / search / remove / in-order list | O(h) each, O(n) traversal |
| `irrigation_queue.cpp` | Circular FIFO queue (array) | enqueue / dequeue / peek | O(1) |
| `priority_heap.cpp` | Binary max-heap (by dryness) | insert / extract-max / build | O(log n) / O(log n) / O(n) |
| `scheduler.cpp` | Heap + circular queue | refresh heap from fields, extract driest k, enqueue | O(n + k log n) |
| `planner.cpp` | Sorting + greedy scheduling | plan multi-day irrigation | O(n log n + days * n) |
| `pipeline_bfs.cpp` | Graph (adjacency list) + BFS | shortest path (unweighted) | O(V + E) |
| `prediction.cpp` | Quadratic scoring function | predict yield from moisture | O(1) |

The BST, queue, heap, graph and BFS are implemented by hand (no `std::map`, `std::queue`, `std::priority_queue`). The standard library is used only for `std::string`, `std::vector`, `std::stable_sort` (in the planner) and file streams.

## Building and Running

Requires `g++` with C++17 support (MinGW on Windows).

```bash
make                       # builds ./smart_farming_system
./smart_farming_system     # starts the console menu
```

On Windows the executable is `smart_farming_system.exe`.

## Console Menu

| Option | Action |
|---|---|
| 1 | Add / update a field (ID, moisture 0-100, crop name) |
| 2 | Remove a field |
| 3 | List all fields (sorted by ID, with dryness) |
| 4 | Enqueue a field for irrigation |
| 5 | Dequeue the next field from the irrigation queue |
| 6 | Build the priority heap from the current fields |
| 7 | Extract the driest field from the heap |
| 8 | Predict yield for a field |
| 9 | Plan multi-day irrigation (days, max fields per day) |
| 10 | Save fields to a file |
| 11 | Load fields from a file |
| 12 | Pipeline BFS: load an edge file and query the shortest distance |
| 13 | Schedule irrigation from the heap (move the driest k fields into the queue) |
| 0 | Exit |

### Quick demo

1. Option `11`, file `fields_sample.txt`, then option `3` to list the fields.
2. Option `13`, count `3`: the three driest fields go into the queue. Option `5` shows them driest first.
3. Option `8`, a field ID: predicted yield.
4. Option `9`, `3` days, `2` per day: the day-wise plan.
5. Option `12`, file `pipeline_network.txt`, source `0`, target `4`: shortest distance is 3.

## Data Files

- **Field file**: one field per line, `id moisture crop` (for example `1 30 wheat`). Crop names may contain spaces. On load, malformed lines and lines with a negative ID or a moisture outside 0-100 are skipped. Crop names are cut to 63 characters.
- **Pipeline file**: one pipe per line, `u v` (two node IDs). Pipes work in both directions.
- Samples: `fields_sample.txt` and `pipeline_network.txt`.

## Testing

```bash
make test
```

Builds and runs:

- all unit tests (BST, BFS, heap/queue, prediction/planner, heap-to-queue scheduler)
- the console-menu smoke test (`tests/run_tests.sh`): loads the sample file and checks listing, heap extraction, scheduling, prediction, planning, BFS and input validation
- the web API end-to-end test (`tests/test_api.py`, needs Python 3): starts `server.py` on a free port and calls all 13 endpoints the web UI uses (add, remove, list, enqueue, dequeue, heap, heap-to-queue schedule, yield, planning through the C++ program, BFS, save, load), including error cases, and checks that every endpoint used in `ui/script.js` exists in the server

The command stops with an error if any check fails. The API test checks what the browser talks to; clicking through the page in a browser is a manual demo step.

## Web UI

### Prerequisites

- Python 3.6 or higher
- A modern web browser
- The compiled backend (`make`)

### Starting the Web UI

1. Build the C++ program: `make`
2. Start the API server: `python server.py` (runs on `http://localhost:8000`; `start_ui.sh` / `start_ui.bat` do the same after checking the build)
3. Open `ui/index.html` in the browser, or serve it:
   ```bash
   cd ui
   python -m http.server 8080
   ```
   then go to `http://localhost:8080`.

### How the web UI works

- `server.py` keeps the field data for the UI and saves it in `ui_state.txt`.
- **Multi-day planning** runs through the compiled C++ program: the server writes the fields to a temporary file and feeds the menu (options 11 and 9) to `./smart_farming_system`. If that call fails, it uses a Python fallback with the same greedy rule.
- The other UI features (field list, queue, heap, heap-to-queue scheduling, yield prediction, pipeline BFS) are handled in Python with the same logic as the C++ modules. The "Schedule Driest from Heap" button (`/api/schedule`) is the web version of console option 13. Yield uses the same 0-1 relative scale as the console program.
- The web UI needs the API server running.

## Project Structure

- `main.cpp` - entry point, menu loop, input validation, connects all modules
- `field_bst.cpp/h` - BST for field records, file save/load, `collect_fields_into_array`
- `irrigation_queue.cpp/h` - circular FIFO `Queue` class (capacity 256)
- `priority_heap.cpp/h` - max-heap `Heap` class ordered by dryness (capacity 1024)
- `scheduler.cpp/h` - moves the driest fields from the heap into the queue
- `prediction.cpp/h` - yield prediction
- `planner.cpp/h` - greedy multi-day irrigation planner
- `pipeline_bfs.cpp/h` - pipeline graph and BFS
- `tests/` - unit tests, the menu smoke test, and the web API test
- `ui/` - web UI (HTML, CSS, JavaScript)
- `server.py` - API server for the web UI
- `fields_sample.txt`, `pipeline_network.txt` - sample data

## Limitations

- The queue holds at most 256 requests and the heap at most 1024 fields.
- The heap is a snapshot: after fields change, rebuild it with option 6 (option 13 rebuilds it automatically).
- The BST is not self-balancing, so a long run of sorted IDs makes it degrade towards O(n).
- The planner is greedy (driest first, no field two days in a row). It does not look ahead to maximise total yield.
- The yield prediction is a simple moisture-based model, not trained on real crop data.

## Work Division

| Work item | Team member | Files |
|---|---|---|
| Team lead, core program and integration: menu, input validation, BST, BFS, web UI and API server, tests setup | Gaurav Kharola | `main.cpp`, `field_bst.*`, `pipeline_bfs.*`, `server.py`, `ui/`, `Makefile`, BST/BFS tests |
| Scheduling and queue: circular queue, max-heap, heap-to-queue scheduling | Tanvi Tripathi | `priority_heap.*`, `irrigation_queue.*`, `scheduler.*`, heap/queue and scheduler tests |
| Prediction and documentation: yield prediction, multi-day planner, README, complexity analysis | Tanvi Tripathi | `prediction.*`, `planner.*`, `README.md`, prediction/planner tests |

## Complexity Summary

| Operation | Time |
|---|---|
| BST insert / search / delete | O(h) (O(log n) balanced, O(n) worst) |
| BST in-order list / save / collect | O(n) |
| Queue enqueue / dequeue / peek | O(1) |
| Heap insert / extract-max | O(log n) |
| Heap build from array | O(n) |
| Heap-to-queue scheduling (k fields) | O(n + k log n) |
| Greedy planner | O(n log n) sort + O(days x n) |
| BFS shortest pipe path | O(V + E) |
| Yield prediction | O(1) |
