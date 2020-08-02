# Założenia
![Sequence diagram](http://www.plantuml.com/plantuml/png/VPFHgjim38RlzHIwR64T7MLivA8KIbbXWq6xiMil5erNHmws73R8m-nPzcHBqmIVdEFJAnDPV_ullw9T4EKbrXPKASxZtXfY0VX1Fy_aM_Ausc9wAF2B2KACZh7uk8PJP34r7RXDtQcM4xtRR3u0TDtxTTS1tEsUUtmwV4FldDmSUYpJAg7KC6CRWGiqhEdtsqfg2veoegaq2XB2oB1QRPyYd8cruGkMJjF0itTrOwmIu_X48Lh1VtzxFboey8VBPOuJh7CD7gbNLQF61Fpw6H0njUKZ6poFfAnKPr4ImvZSJJfPlP0DjwcO6M0nmndwDRt-Fc8DAUu-eZne9fo1TWe74HyC9UiCsSzm_dgVZYWlINslmt3C6aSmobtr1bb5HUKLXOA4T9qRq84rQ9epPBdd-VyAZd4HHBieRx0_oVibm8CfO7u7qb2c5JXHIQObT56QADd4qzy-gh30xus-zJJgGbWw5kAaJVko8zQnjly1)
Zadanie "Check tests" można przenieść z Workera na RuntimeEnvServer.


## Docker setup
Kontenery:
* WebServer
* RuntimeEnvServer
  * WorkerHaskell
  * WorkerProlog

## WebServer
Głównym zadaniem jest wystawianie kontentu dla użytkownika i komunikacja z serwerem zarządzającym przetwarzaniem kodu wejściowego. Serwer wystawia endpointy dla usera, a komunikacja z RuntimeEnvServer odbywa się za pomocą gRPC.

Komponenty:
* Node.js
* Opened ports 80, 1337
* gRPC client

## RuntimeEnvServer
Głównym zadaniem jest przetwarzanie kodu wejściowego i zarządzanie workerami (sprawdzenie statusu, uruchomienie, restartowanie, zabijanie po czasie lub wykorzystanych zasobach). Komunikacja z WebServerem za pomocą gRPC, komunikacja z Workerami za pomocą mapowalnych filestreamów.

Komponenty:
* python/node.js gRPC server
* Docker do stawiania i komunikacji z workerami

## Worker
Kompilacja i uruchomienie "niebezpiecznego kodu"

Komponenty:
* odpowiedni kompilator


# Testy:

## Requirements
Docker

## Setup
* docker-compose build
* docker-compose up -d

## Bash attach
docker exec -it proskell /bin/bash


## Haskell
Run interpreter: ghci
Run without compilation: runhaskell test.hs
Compile to exe: ghc --make test.hs
Run: ./test

## Python integration
/etc/proskell/haskell# echo test | ./compile_and_run.py
