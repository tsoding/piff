# Piff

Simple File Diff Tool in Python. It's very slow (cause it's uses O(N²) algorithm) and implemented for educational purposes. Don't use it for anything real.

## Quick Start

```console
$ ./piff.py diff file1.txt file2.txt > file.patch
$ ./piff.py patch file1.txt file.patch
$ diff -u file1.txt file2.txt  # verify that file1.txt was actually turned into file2.txt
```
