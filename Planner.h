#ifndef PLANNER_H
#define PLANNER_H

#include <vector>
#include "field_bst.h"

// Greedy multi-day planner: driest fields first, a field watered yesterday is skipped today.
// schedule is resized to [days][per_day_limit]; unused slots hold -1. Returns days planned.
int plan_irrigation(Field *root, int days, int per_day_limit, std::vector<std::vector<int>> &out_schedule);

#endif
