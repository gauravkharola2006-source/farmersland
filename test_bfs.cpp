// Part 1 test: pipeline BFS. Build and run with: make test
#include <cassert>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <vector>
#include "../pipeline_bfs.h"

using namespace std;

int main() {
    const string tmp = "/tmp/_pipeline_test.txt";
    { ofstream o(tmp); o << "0 1\n1 2\n2 3\n0 3\n4 5\n"; }

    int n = 0; vector<vector<int>> adj;
    assert(load_pipeline_network(tmp, n, adj) == 0);
    assert(n == 6);

    assert(bfs_shortest_distance(n, adj, 0, 0) == 0);     // same node
    assert(bfs_shortest_distance(n, adj, 0, 3) == 1);     // direct pipe 0-3
    assert(bfs_shortest_distance(n, adj, 1, 3) == 2);     // 1-0-3 or 1-2-3
    assert(bfs_shortest_distance(n, adj, 3, 1) == 2);     // undirected
    assert(bfs_shortest_distance(n, adj, 0, 5) == -1);    // different component
    assert(bfs_shortest_distance(n, adj, 0, 99) == -1);   // invalid node
    assert(bfs_shortest_distance(n, adj, -1, 2) == -1);

    assert(load_pipeline_network("/tmp/no_such_network.txt", n, adj) == -1);   // missing file
    { ofstream o(tmp); }                                                         // empty file
    assert(load_pipeline_network(tmp, n, adj) == 0 && n == 0);
    assert(bfs_shortest_distance(n, adj, 0, 0) == -1);

    remove(tmp.c_str());
    cout << "Part 1 (BFS): all tests passed\n";
    return 0;
}
