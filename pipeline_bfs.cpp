#include <fstream>
#include <vector>
#include "pipeline_bfs.h"

int load_pipeline_network(const std::string &filename, int &out_node_count,
                          std::vector<std::vector<int>> &out_adj) {
    std::ifstream in(filename);
    if (!in) return -1;

    std::vector<std::pair<int, int>> edges;
    int u, v, maxid = -1;
    while (in >> u >> v) {
        if (u < 0 || v < 0) continue;            // ignore invalid node ids
        if (u > maxid) maxid = u;
        if (v > maxid) maxid = v;
        edges.push_back({u, v});
    }

    if (edges.empty()) {
        out_node_count = 0;
        out_adj.clear();
        return 0;
    }

    int n = maxid + 1;
    out_adj.assign(n, std::vector<int>());
    for (const auto &e : edges) {
        out_adj[e.first].push_back(e.second);
        out_adj[e.second].push_back(e.first);
    }
    out_node_count = n;
    return 0;
}

int bfs_shortest_distance(int node_count, const std::vector<std::vector<int>> &adj, int src, int dest) {
    if (node_count == 0) return -1;
    if (src < 0 || src >= node_count || dest < 0 || dest >= node_count) return -1;

    std::vector<int> q(node_count);
    std::vector<int> vis(node_count, 0);
    std::vector<int> dist(node_count, 0);
    int head = 0, tail = 0;
    q[tail++] = src; vis[src] = 1; dist[src] = 0;

    while (head < tail) {
        int u = q[head++];
        if (u == dest) return dist[u];
        for (int v : adj[u]) {
            if (!vis[v]) { vis[v] = 1; dist[v] = dist[u] + 1; q[tail++] = v; }
        }
    }
    return -1;
}
