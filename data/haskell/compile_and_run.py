#!/usr/bin/env python3.7
import os
import sys
import argparse

CurrentDir = os.path.dirname(os.path.realpath(__file__))
#TestScript = os.path.join(CurrentDir, "test.hs")


def Run(code, input):
    print(f"Python: Haskell start", flush=True)
    os.system(f"cat {input} | runhaskell {code}")
    print(f"Python: Haskell end", flush=True)



def main():
    print("Python main()")

    parser = argparse.ArgumentParser(description='TBD')
    parser.add_argument('--input', nargs=1, help='data for input redirection')
    parser.add_argument('--output', nargs=1, help='data for stdout redirection')
    parser.add_argument('--code', nargs=1, help='code to process')

    args = parser.parse_args()
    print(f"Python argv: {sys.argv}")
    Run(args.code[0], args.input[0])


if __name__ == "__main__":
    main()