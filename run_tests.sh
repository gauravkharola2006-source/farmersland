#!/bin/bash
# Integration smoke test of the console menu. Fails (non-zero exit) if any check fails.
cd "$(dirname "$0")/.."
[ -x ./smart_farming_system ] || make || exit 1
fail=0
check() { # check "<description>" "<output>" "<expected text>"
    if grep -qF -- "$3" <<<"$2"; then echo "  ok   - $1"; else echo "  FAIL - $1 (expected: $3)"; fail=1; fi
}

echo "Menu smoke test: load file, list, heap, schedule, predict, plan, BFS"
out=$(./smart_farming_system <<'IN'
11
fields_sample.txt
3
6
7
13
3
5
8
3
9
3
2
12
pipeline_network.txt
0
4
0
IN
)
check "load sample file"            "$out" "Loaded."
check "list shows field 4 soybean"  "$out" "ID: 4 | Moisture: 70 | Dryness: 30 | Crop: soybean"
check "heap built"                  "$out" "Heap built from current fields."
check "driest field extracted"      "$out" "Highest priority field: ID 3 Dryness 80"
check "heap -> queue scheduling"    "$out" "3 field(s) moved from heap to irrigation queue"
check "queue gives driest first"    "$out" "Dequeued field ID 3"
check "yield prediction"            "$out" "Predicted yield (relative): 0.64"
check "multi-day plan"              "$out" "Planned for 3 days:"
check "BFS shortest distance"       "$out" "Shortest path length: 3"

echo "Input validation: moisture out of range and non-numeric input are rejected"
out=$(./smart_farming_system <<'IN'
1
7
150
abc
60
rice
0
IN
)
check "moisture 150 rejected"       "$out" "Invalid value. Enter a number from 0 to 100."
check "letters rejected"            "$out" "Invalid input. Enter a number."

[ $fail -eq 0 ] && echo "Smoke test passed" || { echo "Smoke test FAILED"; exit 1; }
