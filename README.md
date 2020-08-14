# Założenia
![Sequence diagram](http://www.plantuml.com/plantuml/png/bLHXYzD05Fo-ls8-NY7L7eSeGSf1AGeA7bNHhtlPPxlUPZVilgqUzCURP3asCJbR-sbVcPatJ8Pt6rXwZhKHicBdiJ6QB0lnZUu_ap-IntADF9Jug0EJXRCetwp4BbhMDMtjCQFpVtEawvkRrqASJgzMfvCGQTtVEzvjly0xn-s6pfO-IgOC67jB2YMqLVJxnO5h8nHDILad4RA5v86No_NGmi_WxCjxfnvnfLK18-q-oZqLg9oYnPmhOPnhy9wCvCEEGZGC7V3fWm2GOVC1jJHf-D13dwGdC05WoXr6LuxMztX5p-kHLIA7sGOmHkGSTdURkHWAIE_burkcmD2sYHpMYpFfJqnSMg6DgnjjI4Z3I6_9sbc4M5MaI8ddut7-8KbuwYpyIhEq2dtv8Oq1K-0mpZ_n1D8lZMF1TbjFnEeYrFL5gEyJr6mUMwlo1vuOlZ3KE-a3mVTr2O9Ce56sFwGsfFvBq5CZFQ4Qg93tpgCE-rIugTAumkF61POSmrFJhlg4RAmBgEXx-G8kSXDvqLPF_AFjE7j91Xus1weUKYU6c7nkailksY2bDr_xV5lI0oM-Dgh3D7BVfMIPRERcwtHBLiNQ_040)


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
