#!/usr/bin/env python3.7
import os
import sys


CurrentDir = os.path.dirname(os.path.realpath(__file__))
TestScript = os.path.join(CurrentDir, "test.hs")


def Run(filepath):
    os.system(f"runhaskell {filepath}")


def main():
    print("Python main()")
    print(f"Python argv: {sys.argv}")
    #Run(TestScript)


if __name__ == "__main__":
    main()