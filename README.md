# Piff

Simple File Diff Tool in Python. It's very slow (not only because it's written in Python, but also because it uses O(N²) algorithm) and implemented for educational purposes. Don't use it for anything real.

## Quick Start

```console
$ ./piff.py diff file1.txt file2.txt > file.patch
$ ./piff.py patch file1.txt file.patch
$ diff -u file1.txt file2.txt  # verify that file1.txt was actually turned into file2.txt
```

## Patch Format

Piff uses custom patch format. Here is its [ABNF](https://en.wikipedia.org/wiki/Augmented_Backus%E2%80%93Naur_form):

```c
patch  = *(action SP row SP line LF)
action = 'A' / 'R'
row    = 1*DIGIT
line   = *OCTET
```

- `action` `'A'` means add the `line` after index `row`
- `action` `'R'` means remove the `line` after index `row`

Here is an example of how it usually looks like:

```
A 4 Duis aute irure in dolor reprehenderit in voluptate velit
R 4 Duis aute irure dolor in reprehenderit in voluptate velit
A 7 asjdklaskldja
R 7 mollit anim id est laborum.
```

## References

- https://en.wikipedia.org/wiki/Levenshtein\_distance
- https://www.nathaniel.ai/myers-diff/
