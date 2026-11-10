#include <iostream>
#include <limits>
#include <string>
#include <vector>
#include "field_bst.h"
#include "irrigation_queue.h"
#include "priority_heap.h"
#include "prediction.h"
#include "planner.h"
#include "pipeline_bfs.h"
#include "scheduler.h"

using namespace std;

void print_menu() {
    cout << "\n=== Smart Farming System ===\n"
         << "1. Add / Update Field\n"
         << "2. Remove Field\n"
         << "3. List all Fields\n"
         << "4. Enqueue field for irrigation\n"
         << "5. Dequeue next irrigation\n"
         << "6. Build priority heap from fields (by dryness)\n"
         << "7. Extract highest priority field\n"
         << "8. Predict yield for field\n"
         << "9. Plan multi-day irrigation (greedy planner)\n"
         << "10. Save fields to file\n"
         << "11. Load fields from file\n"
         << "12. Pipeline BFS test (load edges and query shortest)\n"
         << "13. Schedule irrigation from heap (move driest fields to queue)\n"
         << "0. Exit" << endl;
}

// Reads an integer in [lo, hi]. Re-asks on bad input (letters, out of range).
// Returns false only if the input stream is closed.
static bool read_int(const char *prompt, int lo, int hi, int &out) {
    while (true) {
        cout << prompt;
        if (cin >> out) {
            if (out >= lo && out <= hi) return true;
            cout << "Invalid value. Enter a number from " << lo << " to " << hi << "." << endl;
        } else {
            if (cin.eof()) return false;
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            cout << "Invalid input. Enter a number." << endl;
        }
    }
}

// Reads a non-empty line of text (e.g. a crop name or a filename). Re-asks if it is empty.
// Returns false only if the input stream is closed.
static bool read_text(const char *prompt, string &out) {
    while (true) {
        cout << prompt;
        cin >> ws;
        if (!getline(cin, out)) return false;
        while (!out.empty() && (out.back() == '\r' || out.back() == ' ')) out.pop_back();
        if (!out.empty()) return true;
        cout << "Input cannot be empty." << endl;
    }
}

int main() {
    Field *root = nullptr;
    Queue q;
    Heap h;

    int choice;
    while (true) {
        print_menu();
        cout << "Enter choice: ";
        if (!(cin >> choice)) {
            if (cin.eof()) break;                 // input closed -> exit cleanly
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            continue;
        }
        if (choice == 0) break;

        if (choice == 1) {
            int id, moisture; string crop;
            if (!read_int("Field ID: ", 0, 1000000, id)) break;
            if (!read_int("Moisture (0-100): ", 0, 100, moisture)) break;
            if (!read_text("Crop name: ", crop)) break;
            root = insertField(root, id, moisture, crop);
            cout << "Field added/updated." << endl;
        }
        else if (choice == 2) {
            int id;
            if (!read_int("Field ID to remove: ", 0, 1000000, id)) break;
            root = removeField(root, id);
            cout << "If existed, field removed." << endl;
        }
        else if (choice == 3) {
            cout << "\nListing fields (in-order):" << endl;
            listFields(root);
        }
        else if (choice == 4) {
            int id;
            if (!read_int("Field ID to enqueue: ", 0, 1000000, id)) break;
            Field *f = searchField(root, id);
            if (!f) cout << "Field not found." << endl;
            else if (q.enqueue(id) == 0) cout << "Enqueued." << endl;
            else cout << "Queue full." << endl;
        }
        else if (choice == 5) {
            int id;
            if (q.dequeue(id) == 0) cout << "Dequeued field ID " << id << endl;
            else cout << "Queue empty." << endl;
        }
        else if (choice == 6) {
            int n = collect_fields_into_array(root, nullptr);
            if (n == 0) cout << "No fields to build heap." << endl;
            else {
                vector<FieldItem> arr(n);
                collect_fields_into_array(root, arr.data());
                h.build_from_array(arr.data(), n);
                cout << "Heap built from current fields." << endl;
            }
        }
        else if (choice == 7) {
            FieldItem it;
            if (h.extract_max(it) == 0)
                cout << "Highest priority field: ID " << it.id
                     << " Dryness " << it.dryness << " Crop " << it.crop << endl;
            else cout << "Heap empty." << endl;
        }
        else if (choice == 8) {
            int id;
            if (!read_int("Field ID for prediction: ", 0, 1000000, id)) break;
            Field *f = searchField(root, id);
            if (!f) cout << "Field not found." << endl;
            else {
                double yield = predict_yield(f->moisture);
                cout.setf(ios::fixed); cout.precision(2);
                cout << "Predicted yield (relative): " << yield << endl;
                cout.unsetf(ios::fixed);
            }
        }
        else if (choice == 9) {
            int days, perday;
            if (!read_int("Number of days to plan: ", 1, 365, days)) break;
            if (!read_int("Max fields to water per day: ", 1, 1000, perday)) break;
            vector<vector<int>> schedule;
            int got = plan_irrigation(root, days, perday, schedule);
            cout << "Planned for " << got << " days:" << endl;
            for (int d = 0; d < got; d++) {
                cout << "Day " << d + 1 << ": ";
                for (int k = 0; k < perday; k++) {
                    if (schedule[d][k] == -1) break;
                    cout << schedule[d][k] << " ";
                }
                cout << "\n";
            }
        }
        else if (choice == 10) {
            string fname;
            if (!read_text("Filename to save: ", fname)) break;
            if (save_fields(root, fname) == 0) cout << "Saved to " << fname << endl;
            else cout << "Save failed." << endl;
        }
        else if (choice == 11) {
            string fname;
            if (!read_text("Filename to load: ", fname)) break;
            Field *newroot = load_fields(fname);
            if (newroot) { bst_free(root); root = newroot; cout << "Loaded." << endl; }
            else cout << "Load failed or file empty." << endl;
        }
        else if (choice == 12) {
            string fname;
            if (!read_text("Edges filename: ", fname)) break;
            int node_count = 0;
            vector<vector<int>> adj;
            if (load_pipeline_network(fname, node_count, adj) != 0) {
                cout << "Failed to load network." << endl;
                continue;
            }
            int s, t;
            if (!read_int("Source node: ", 0, 1000000, s)) break;
            if (!read_int("Target node: ", 0, 1000000, t)) break;
            int dist = bfs_shortest_distance(node_count, adj, s, t);
            if (dist < 0) cout << "No path or error." << endl;
            else cout << "Shortest path length: " << dist << endl;
        }
        else if (choice == 13) {
            int count;
            if (!read_int("How many fields to schedule: ", 1, QUEUE_CAPACITY, count)) break;
            int moved = schedule_from_heap(root, h, q, count);
            if (moved == 0) cout << "No fields scheduled (no fields, or queue full)." << endl;
            else cout << moved << " field(s) moved from heap to irrigation queue (driest first)." << endl;
        }
        else {
            cout << "Invalid choice." << endl;
        }
    }

    bst_free(root);
    return 0;
}
