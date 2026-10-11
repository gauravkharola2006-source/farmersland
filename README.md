# Smart Farming System — Phase-II 40–50% Milestone (C++17)

This package is a deliberately partial milestone based on the supplied C++ project. It includes the field BST, pipeline BFS, Max-Heap, circular FIFO queue, a small integrated CLI, sample data, and module tests.

## Included and testable
- BST: add/update, remove, search, sorted listing, save/load functions
- BFS pipeline shortest-distance module
- Max-Heap and circular FIFO queue
- Basic CLI integration for these modules
- Unit tests for BST, BFS, and heap/queue

## Not included in this milestone
- Crop-yield prediction module
- Multi-day irrigation planner (the full project version currently uses a greedy planner)
- Web UI/backend
- Complete end-to-end irrigation lifecycle and final integration

This is a milestone snapshot, not a claim that the full project is complete. The percentage is a project-progress estimate based on selected modules, not a measured line-count percentage.

## Build and test
```bash
make
make test
./smart_farming_milestone
```
Requires g++ with C++17 support.

## Test status
The included module tests should be run locally with `make test`. A passing unit test verifies the tested module behavior only; it does not prove all end-to-end workflows.
