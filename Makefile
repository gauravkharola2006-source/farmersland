CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2

SRCS = main.cpp field_bst.cpp pipeline_bfs.cpp priority_heap.cpp irrigation_queue.cpp \
       prediction.cpp planner.cpp scheduler.cpp
TARGET = smart_farming_system

all: $(TARGET)

$(TARGET): $(SRCS) $(wildcard *.h)
	$(CXX) $(CXXFLAGS) -I. -o $@ $(SRCS)

# Unit tests (BST, BFS, heap/queue, prediction/planner, heap->queue scheduler),
# the integration smoke test of the console menu, and the web API end-to-end test (needs python3).
test: $(TARGET)
	$(CXX) $(CXXFLAGS) -I. -o test_bst tests/test_bst.cpp field_bst.cpp
	$(CXX) $(CXXFLAGS) -I. -o test_bfs tests/test_bfs.cpp pipeline_bfs.cpp
	$(CXX) $(CXXFLAGS) -I. -o test_heap_queue tests/test_heap_queue.cpp field_bst.cpp priority_heap.cpp irrigation_queue.cpp
	$(CXX) $(CXXFLAGS) -I. -o test_prediction_planner tests/test_prediction_planner.cpp field_bst.cpp prediction.cpp planner.cpp
	$(CXX) $(CXXFLAGS) -I. -o test_scheduler tests/test_scheduler.cpp field_bst.cpp priority_heap.cpp irrigation_queue.cpp scheduler.cpp
	./test_bst
	./test_bfs
	./test_heap_queue
	./test_prediction_planner
	./test_scheduler
	bash tests/run_tests.sh
	@if command -v python3 >/dev/null 2>&1; then python3 tests/test_api.py; else echo "python3 not found - skipping web API test"; fi

clean:
	rm -f $(TARGET) test_bst test_bfs test_heap_queue test_prediction_planner test_scheduler

.PHONY: all test clean
