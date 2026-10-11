CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2

all: smart_farming_milestone

smart_farming_milestone: main.cpp field_bst.cpp pipeline_bfs.cpp priority_heap.cpp irrigation_queue.cpp
	$(CXX) $(CXXFLAGS) -o $@ $^

test:
	$(CXX) $(CXXFLAGS) -o test_bst tests/test_bst.cpp field_bst.cpp
	$(CXX) $(CXXFLAGS) -o test_bfs tests/test_bfs.cpp pipeline_bfs.cpp
	$(CXX) $(CXXFLAGS) -o test_heap_queue tests/test_heap_queue.cpp priority_heap.cpp irrigation_queue.cpp
	./test_bst
	./test_bfs
	./test_heap_queue

clean:
	rm -f smart_farming_milestone test_bst test_bfs test_heap_queue

.PHONY: all test clean
