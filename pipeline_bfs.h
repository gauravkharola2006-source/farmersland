#ifndef PIPELINE_BFS_H
#define PIPELINE_BFS_H

#include <string>
#include <vector>

// Undirected graph stored as adjacency lists. Returns 0 on success, -1 if file can't be opened.
int load_pipeline_network(const std::string &filename, int &out_node_count,
                          std::vector<std::vector<int>> &out_adj);

// Shortest number of pipes between src and dest, or -1 if unreachable / invalid.
int bfs_shortest_distance(int node_count, const std::vector<std::vector<int>> &adj, int src, int dest);

#endif
