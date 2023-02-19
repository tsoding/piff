#!/usr/bin/env python3

import sys
import re

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

def edit_distance(s1, s2):
    m1 = len(s1)
    m2 = len(s2)

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
            if s1[n1-1] == s2[n2-1]:
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
            patch.append((ADD, n2, s2[n2]))
        elif action == REMOVE:
            n1 -= 1
            patch.append((REMOVE, n1, s1[n1]))
        elif action == IGNORE:
            n1 -= 1
            n2 -= 1
        else:
            assert False, "unreachable"
    patch.reverse()
    return patch

def diff_subcommand(program, args):
    if len(args) < 2:
        print(f"Usage: {program} diff <file1> <file2>")
        print(f"ERROR: not enough files were provided to generate a diff")
        exit(1)

    file_path1, *args = args
    file_path2, *args = args
    lines1 = read_entire_file(file_path1).splitlines()
    lines2 = read_entire_file(file_path2).splitlines()

    patch = edit_distance(lines1, lines2)

    for (action, n, line) in patch:
        print(f"{action} {n} {line}")

PATCH_LINE_REGEXP = re.compile("([AR]) (\d+) (.*)")

def line_as_patch_action(line):
    return PATCH_LINE_REGEXP.match(line)

def patch_subcommand(program, args):
    if len(args) < 2:
        print(f"Usage: {program} patch <file> <file.patch>")
        print(f"ERROR: not enough arguments were provided to patch a file")
    file_path, *args = args
    patch_path, *args = args

    lines = read_entire_file(file_path).splitlines()
    patch = []
    ok = True
    for (row, line) in enumerate(read_entire_file(patch_path).splitlines()):
        if len(line) == 0:
            continue
        m = PATCH_LINE_REGEXP.match(line)
        if m is None:
            print(f"{patch_path}:{row + 1}: Invalid patch action: {line}")
            ok = False
            continue
        patch.append((m.group(1), int(m.group(2)), m.group(3)))
    if not ok:
        exit(1)

    for (action, row, line) in reversed(patch):
        if action == ADD:
            lines.insert(row, line)
        elif action == REMOVE:
            lines.pop(row)
        else:
            assert False, "unreachable"

    with open(file_path, 'w') as f:
        for line in lines:
            f.write(line)
            f.write('\n')

def help_subcommand(program, args):
    if len(args) == 0:
        usage(program)
        return

    subcommand, *args = args
    if subcommand not in SUBCOMMANDS:
        usage(program)
        print(f"ERROR: unknown subcommand {subcommand}")
        exit(1)

    print(f"Usage: {subcommand} {SUBCOMMANDS[subcommand].signature}")
    print(f"    {SUBCOMMANDS[subcommand].description}")

class Subcommand:
    def __init__(self, run, signature, description):
        self.run = run
        self.signature = signature
        self.description = description

SUBCOMMANDS = {
    "diff": Subcommand(
        run = diff_subcommand,
        signature = "<file1> <file2>",
        description = "print the difference between the files to stdout",
    ),
    "patch": Subcommand(
        run = patch_subcommand,
        signature = "<file> <file.patch>",
        description = "patch the file with the given patch",
    ),
    "help": Subcommand(
        run = help_subcommand,
        signature = "[subcommand]",
        description = "print this help",
    )
}

def usage(program):
    print(f"Usage: {program} <SUBCOMMAND> [OPTIONS]")
    print(f"Subcommands:")
    width = max([len(f'{name} {subcmd.signature}')
                 for (name, subcmd) in SUBCOMMANDS.items()])
    for (name, subcmd) in SUBCOMMANDS.items():
        command = f'{name} {subcmd.signature}'.ljust(width)
        print(f'    {command}    {subcmd.description}')

def main():
    assert len(sys.argv) > 0
    program, *args = sys.argv

    if len(args) == 0:
        usage(program)
        print(f"ERROR: no subcommand is provided")
        exit(1)

    subcommand, *args = args

    if subcommand not in SUBCOMMANDS:
        usage(program)
        print(f"ERROR: unknown subcommand {subcommand}")
        candidates = [(name, len(edit_distance(subcommand, name)))
                      for (name, definition) in SUBCOMMANDS.items()
                      if len(edit_distance(subcommand, name)) < 3]
        candidates.sort(key=lambda x: x[1])
        if len(candidates) > 0:
            print("Maybe you meant:")
            for (name, _) in candidates:
                print(f"    {name}")
        exit(1)

    SUBCOMMANDS[subcommand].run(program, args)

if __name__ == '__main__':
    main()
