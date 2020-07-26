# Requirements
Docker

# Setup
* docker-compose build
* docker-compose up -d

# Bash attach
docker exec -it proskell /bin/bash


# Haskell
Run interpreter: ghci
Run without compilation: runhaskell test.hs
Compile to exe: ghc --make test.hs
Run: ./test

# Python integration
/etc/proskell/haskell# echo test | ./compile_and_run.py