#!/usr/bin/env python3.7
import os

CurrentDir = os.path.dirname(os.path.realpath(__file__))
TestScript = os.path.join(CurrentDir, "test.hs")


def Run(filepath):
    os.system(f"runhaskell {filepath}")


def main():
    print("Python main()")
    Run(TestScript)


if __name__ == "__main__":
    main()