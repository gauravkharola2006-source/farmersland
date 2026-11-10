#include <algorithm>
#include <vector>
#include "planner.h"

static bool compare_desc(const FieldItem &a, const FieldItem &b) {
    return a.dryness > b.dryness;
}

int plan_irrigation(Field *root, int days, int per_day_limit, std::vector<std::vector<int>> &out_schedule) {
    if (!root || days <= 0 || per_day_limit <= 0) return 0;
    int n = collect_fields_into_array(root, nullptr);
    if (n == 0) return 0;

    std::vector<FieldItem> arr(n);
    collect_fields_into_array(root, arr.data());
    std::stable_sort(arr.begin(), arr.end(), compare_desc);

    out_schedule.assign(days, std::vector<int>(per_day_limit, -1));

    std::vector<int> prev_watered(n, 0);
    int maxid = 0;
    for (int i = 0; i < n; i++) if (arr[i].id > maxid) maxid = arr[i].id;
    int map_size = maxid + 1;
    std::vector<int> id_to_idx(map_size, -1);
    for (int i = 0; i < n; i++) if (arr[i].id >= 0) id_to_idx[arr[i].id] = i;

    for (int d = 0; d < days; ++d) {
        int picked = 0;
        for (int i = 0; i < n && picked < per_day_limit; ++i) {
            if (prev_watered[i]) continue;
            out_schedule[d][picked] = arr[i].id;
            picked++;
        }
        std::vector<int> next_prev(n, 0);
        for (int p = 0; p < picked; p++) {
            int fid = out_schedule[d][p];
            if (fid >= 0 && fid < map_size && id_to_idx[fid] != -1) next_prev[id_to_idx[fid]] = 1;
        }
        prev_watered = next_prev;
        for (int s = picked; s < per_day_limit; ++s) out_schedule[d][s] = -1;
    }
    return days;
}
