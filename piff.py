#!/usr/bin/env python3

import sys
import re
from typing import TypeVar, List, Sequence, Tuple, Union
from typing_extensions import Literal

def read_entire_file(file_path: str) -> str:
    with open(file_path) as f:
        return f.read()

Action = Literal['I', 'A', 'R']

# TODO: can we get rid of IGNORE? It's not used in the final patches anyway...
IGNORE: Action  = 'I'
ADD: Action     = 'A'
REMOVE: Action  = 'R'

T = TypeVar("T")

# TODO: can we make T comparable?
def edit_distance(s1: Sequence[T], s2: Sequence[T]) -> List[Tuple[Action, int, T]]:
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

PATCH_LINE_REGEXP: re.Pattern = re.compile("([AR]) (\d+) (.*)")

class Subcommand:
    name: str
    signatures: str
    description: str

    def __init__(self, name: str, signature: str, description: str):
        self.name = name
        self.signature = signature
        self.description = description

    def run(self, program: str, args: List[str]) -> int:
        assert False, "not implemented"
        return 0

class DiffSubcommand(Subcommand):
    def __init__(self):
        super().__init__("diff", "<file1> <file2>", "print the difference between the files to stdout")

    def run(self, program: str, args: List[str]) -> int:
        if len(args) < 2:
            print(f"Usage: {program} {self.name} {self.signature}")
            print(f"ERROR: not enough files were provided to {self.name}")
            return 1

        file_path1, *args = args
        file_path2, *args = args
        lines1 = read_entire_file(file_path1).splitlines()
        lines2 = read_entire_file(file_path2).splitlines()

        patch = edit_distance(lines1, lines2)

        for (action, n, line) in patch:
            print(f"{action} {n} {line}")
        return 0

class PatchSubcommand(Subcommand):
    def __init__(self):
        super().__init__("patch", "<file> <file.patch>", "patch the file with the given patch")

    def run(self, program: str, args: List[str]) -> int:
        if len(args) < 2:
            print(f"Usage: {program} {self.name} {self.signature}")
            print(f"ERROR: not enough arguments were provided to {self.name} a file")
            return 1

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
            return 1

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
        return 0

class HelpSubcommand(Subcommand):
    def __init__(self):
        super().__init__("help", "[subcommand]", "print this help message")

    def run(self, program: str, args: List[str]) -> int:
        if len(args) == 0:
            usage(program)
            return 0

        subcmd_name, *args = args

        subcmd = find_subcommand(subcmd_name)
        if isinstance(subcmd, Subcommand):
            print(f"Usage: {subcmd.name} {subcmd.signature}")
            print(f"    {subcmd.description}")
            return 0

        candidates: List[str] = subcmd
        usage(program)
        print(f"ERROR: unknown subcommand {subcmd_name}")
        if len(candidates) > 0:
            print("Maybe you meant:")
            for name in candidates:
                print(f"    {name}")
        return 1

SUBCOMMANDS: List[Subcommand] = [
    DiffSubcommand(),
    PatchSubcommand(),
    HelpSubcommand(),
]

def usage(program: str) -> None:
    print(f"Usage: {program} <SUBCOMMAND> [OPTIONS]")
    print(f"Subcommands:")
    width = max([len(f'{subcmd.name} {subcmd.signature}')
                 for subcmd in SUBCOMMANDS])
    for subcmd in SUBCOMMANDS:
        command = f'{subcmd.name} {subcmd.signature}'.ljust(width)
        print(f'    {command}    {subcmd.description}')

def find_subcommand(subcmd_name: str) -> Union[Subcommand, List[str]]:
    for subcmd in SUBCOMMANDS:
        if subcmd.name == subcmd_name:
            return subcmd

    return [subcmd.name
            for subcmd in SUBCOMMANDS
            if len(edit_distance(subcmd_name, subcmd.name)) < 3]

def main() -> int:
    assert len(sys.argv) > 0
    program, *args = sys.argv

    if len(args) == 0:
        usage(program)
        print(f"ERROR: no subcommand is provided")
        return 1

    subcmd_name, *args = args

    subcmd = find_subcommand(subcmd_name)
    if isinstance(subcmd, Subcommand):
        return subcmd.run(program, args)

    candidates: List[str] = subcmd
    usage(program)
    print(f"ERROR: unknown subcommand {subcmd_name}")
    if len(candidates) > 0:
        print("Maybe you meant:")
        for name in candidates:
            print(f"    {name}")
    return 1

# TODO: some sort of automatic testing

if __name__ == '__main__':
    exit(main())
