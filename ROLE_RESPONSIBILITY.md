# Gaurav Kharola — Core + Integration

Assigned files:
- `main.cpp` — main CLI and integration (shared-work item assigned here because the main program is the integration point)
- `field_bst.h/.cpp` — field record BST, CRUD/search/list and save/load helpers
- `pipeline_bfs.h/.cpp` — irrigation pipeline BFS
- `tests/test_bst.cpp`, `tests/test_bfs.cpp` — related tests
- `fields_sample.txt`, `pipeline_network.txt` — sample data
- `Makefile`, `README.md` — build/test entry point and project instructions

Important: `main.cpp` includes `priority_heap.h` and `irrigation_queue.h`, owned by Tanvi. The final build requires both role folders to be merged into one project directory before running `make`/`make test`.
