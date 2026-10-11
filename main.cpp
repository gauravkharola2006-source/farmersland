#include <iostream>
#include <vector>
#include <string>
#include "field_bst.h"
#include "irrigation_queue.h"
#include "priority_heap.h"
#include "pipeline_bfs.h"

int main() {
    Field *root = nullptr;
    Queue queue;
    Heap heap;
    int choice = -1;
    while (true) {
        std::cout << "\n=== Smart Farming System (Phase-II 40-50% Milestone) ===\n"
                  << "1. Add/update field\n2. Remove field\n3. List fields\n"
                  << "4. Enqueue irrigation request\n5. Dequeue request\n"
                  << "6. Build dryness heap\n7. Extract driest field\n"
                  << "8. Find pipeline shortest distance\n0. Exit\nChoice: ";
        if (!(std::cin >> choice)) break;
        if (choice == 0) break;
        if (choice == 1) {
            int id, moisture; std::string crop;
            std::cout << "Field ID, moisture (0-100), crop: ";
            if (std::cin >> id >> moisture >> crop && moisture >= 0 && moisture <= 100) {
                root = insertField(root, id, moisture, crop);
                std::cout << "Field added/updated.\n";
            } else std::cout << "Invalid input.\n";
        } else if (choice == 2) {
            int id; std::cout << "Field ID: ";
            if (std::cin >> id) root = removeField(root, id);
            std::cout << "Remove request processed.\n";
        } else if (choice == 3) {
            listFields(root);
        } else if (choice == 4) {
            int id; std::cout << "Field ID: "; std::cin >> id;
            if (searchField(root, id) && queue.enqueue(id) == 0) std::cout << "Queued.\n";
            else std::cout << "Field missing or queue full.\n";
        } else if (choice == 5) {
            int id;
            if (queue.dequeue(id) == 0) std::cout << "Next field: " << id << "\n";
            else std::cout << "Queue empty.\n";
        } else if (choice == 6) {
            int n = collect_fields_into_array(root, nullptr);
            if (!n) { std::cout << "No fields available.\n"; continue; }
            std::vector<FieldItem> items(n);
            collect_fields_into_array(root, items.data());
            heap.build_from_array(items.data(), n);
            std::cout << "Heap built. Note: verify the field moisture/dryness mapping during integration.\n";
        } else if (choice == 7) {
            FieldItem item;
            if (heap.extract_max(item) == 0)
                std::cout << "Priority field ID " << item.id << ", priority " << item.dryness << "\n";
            else std::cout << "Heap empty.\n";
        } else if (choice == 8) {
            std::string filename; int src, dst, nodes;
            std::cout << "Pipeline file (e.g. pipeline_network.txt), source, destination: ";
            if (!(std::cin >> filename >> src >> dst)) break;
            std::vector<std::vector<int>> adj;
            if (load_pipeline_network(filename, nodes, adj) == 0)
                std::cout << "Shortest distance: " << bfs_shortest_distance(nodes, adj, src, dst) << "\n";
            else std::cout << "Could not load pipeline file.\n";
        } else std::cout << "Unknown choice.\n";
    }
    bst_free(root);
    return 0;
}
