@startuml
actor Client

WebServer -> WebServer : Listen on :80
RuntimeEnvServer -> RuntimeEnvServer : Listen on :1337

||50||

Client -> WebServer : GET root:80
activate WebServer
WebServer -> Client: index.html
deactivate WebServer
activate Client

||50||


Client-->WebServer : json/body (id, language, code)
activate WebServer

loop HelathResult is OK
    WebServer -> RuntimeEnvServer : Health
    activate RuntimeEnvServer
    RuntimeEnvServer -> WebServer: HelathResult
    deactivate RuntimeEnvServer
end

WebServer-->RuntimeEnvServer : json/RPC (id, language, code, array<test inputs>)
deactivate WebServer
activate RuntimeEnvServer

RuntimeEnvServer -> RuntimeEnvServer : Compile
alt Compilation succeded

    RuntimeEnvServer -> Worker : Create worker and start all tests
    activate Worker
        Worker -> Worker : Run test 0
        Worker -> Worker : Run test 1
        Worker -> Worker : Run test X
        Worker -> RuntimeEnvServer : End
    deactivate Worker
    RuntimeEnvServer -> RuntimeEnvServer : Parse results
else Compilation failed
    RuntimeEnvServer -> RuntimeEnvServer : Prepare compilation error msg
end

RuntimeEnvServer --> WebServer: json/RPC (id, status, array<(test num, duration, output)>)

deactivate RuntimeEnvServer 
activate WebServer
WebServer -> WebServer: Check tests
WebServer --> Client: json/html result
deactivate WebServer

Client-->Client : Update page content
deactivate Client
@enduml