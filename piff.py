#!/usr/bin/env python3

import sys

def read_entire_file(file_path):
    with open(file_path) as f:
        return f.read()

IGNORE  = 'I'
ADD     = 'A'
REMOVE  = 'R'

def trace_tables(cache, actions):
    for row in range(len(cache)):
        for col in range(len(cache[row])):
            item = cache[row][col]
            action = actions[row][col]
            print(f"{item} ({action})".ljust(6), end=' ')
        print()
    print()

if __name__ == '__main__':
    program = sys.argv[0]
    if len(sys.argv) < 3:
        print(f"Usage: {program} <file1> <file2>")
        print(f"ERROR: not enough files to compare were provided")
        exit(1)
    lines1 = read_entire_file(sys.argv[1]).splitlines()
    lines2 = read_entire_file(sys.argv[2]).splitlines()
    m1 = len(lines1)
    m2 = len(lines2)

    distances = []
    actions = []
    for _ in range(m1 + 1):
        distances.append([0]*(m2 + 1))
        actions.append(['-']*(m2 + 1))

    distances[0][0] = 0
    actions[0][0] = IGNORE

    for n2 in range(1, m2 + 1):
        n1 = 0
        distances[n1][n2] = n2
        actions[n1][n2] = ADD

    for n1 in range(1, m1 + 1):
        n2 = 0
        distances[n1][n2] = n1
        actions[n1][n2] = REMOVE

    for n1 in range(1, m1 + 1):
        for n2 in range(1, m2 + 1):
            if lines1[n1-1] == lines2[n2-1]:
                distances[n1][n2] = distances[n1-1][n2-1]
                actions[n1][n2] = IGNORE
                continue      # ignore

            remove = distances[n1-1][n2]
            add = distances[n1][n2-1]

            distances[n1][n2] = remove
            actions[n1][n2] = REMOVE

            if distances[n1][n2] > add:
                distances[n1][n2] = add
                actions[n1][n2] = ADD

            distances[n1][n2] += 1

    patch = []
    n1 = m1
    n2 = m2
    while n1 > 0 or n2 > 0:
        action = actions[n1][n2]
        if action == ADD:
            n2 -= 1
            patch.append((ADD, n2, lines2[n2]))
        elif action == REMOVE:
            n1 -= 1
            patch.append((REMOVE, n1, lines1[n1]))
        elif action == IGNORE:
            n1 -= 1
            n2 -= 1
        else:
            assert False, "unreachable"
    patch.reverse()
    for (action, n, line) in patch:
        print(f"{action} {n} {line}")
