from flask import (Flask, request, Response, json)
import os
import docker  # Needed: pip install docker
import time
import asyncio
import json

WORKER_HASKELL_IMAGE_NAME = "haskell"
WORKER_HASKELL_NAME = "worker_haskell"
WORKER_PROLOG_IMAGE_NAME = "swipl"
WORKER_PROLOG_NAME = "worker_prolog"
WORKER_DATA_DIR = "/var/proskell"
SERVER_DATA_DIR = "mnt_data"

JSON_HASKELL_ID = "haskell"
JSON_PROLOG_ID = "prolog"


def GetWorkerRequestDir(request):
    return f"{WORKER_DATA_DIR}/{request['userid']}/{request['timestamp']}"


def GetServerRequestDir(request):
    return f"{SERVER_DATA_DIR}/{request['userid']}/{request['timestamp']}"


def GetServerDir():
    return os.getcwd()


def GetCompilerByLanguage(lang):
    if lang == JSON_HASKELL_ID:
        return "runhaskell"
    if lang == JSON_PROLOG_ID:
        return "swipl"
    return ""


client = docker.from_env()


async def process_all_tests(request):
    tests = request["tests"]

    compiler = GetCompilerByLanguage(request["language"])
    if compiler == "":
        print(f"Execution command is empty!")
        return

    for i in range(len(tests)):
        print(f"Processing test {i}...")
        cmd = f"bash -c 'cat {GetWorkerRequestDir(request)}/test{i} | {compiler} {GetWorkerRequestDir(request)}/code.xxx && sleep 2'"
        stdout = await process_test(cmd, request["timeoutMs"], request["language"])
        tests[i]["result"] = f"{stdout}"


async def process_test(cmd, timeout, language):
    print("Creating worker...")
    try:
        # TODO: timeout does not work now
        out = await asyncio.wait_for(
            asyncio.gather(create_and_run_worker(cmd, language)),
            timeout=timeout
        )
        print(f"Worker stdout: {out}")
        return out
    except asyncio.TimeoutError:
        print("Worker timeout!")
        return "Timeout"


def clean_worker_container():

    try:
        worker = client.containers.get(WORKER_HASKELL_NAME)
        worker.remove(force=True)
    except:
        pass
    try:
        worker = client.containers.get(WORKER_PROLOG_NAME)
        worker.remove(force=True)
    except:
        pass


async def create_and_run_worker(cmd, language):
    clean_worker_container()
    imageName = ""
    containerName = ""

    if language == JSON_HASKELL_ID:
        imageName = WORKER_HASKELL_IMAGE_NAME
        containerName = WORKER_HASKELL_NAME
    elif language == JSON_PROLOG_ID:
        imageName = WORKER_PROLOG_IMAGE_NAME
        containerName = WORKER_PROLOG_NAME

    if (not imageName) or (not containerName):
        print("Cannot create worker! Language type is mismatched!")
        return "Language mismatch"

    out = client.containers.run(
        image=imageName,
        name=containerName,
        entrypoint=cmd,
        remove=True,
        volumes={
            f"{GetServerDir()}/{SERVER_DATA_DIR}": {'bind': WORKER_DATA_DIR, 'mode': 'rw'}
        }
    )
    return out


def validate_request(request):
    if "userid" not in request:
        raise ValueError("userid is missing")
    if "timestamp" not in request:
        raise ValueError("timestamp is missing")
    if "language" not in request:
        raise ValueError("language is missing")
    if request["language"] not in [JSON_HASKELL_ID, JSON_PROLOG_ID]:
        raise ValueError("language is not supported")

    if "code" not in request:
        raise ValueError("language is missing")
    if "timeoutMs" not in request:
        raise ValueError("timeoutMs is missing")
    if "tests" not in request or not isinstance(request["tests"], list) or len(request["tests"]) == 0:
        raise ValueError("tests are missing")


def save_files_on_volume(request):
    os.makedirs(GetServerRequestDir(request), exist_ok=True)

    # Save all tests inputs
    tests = request["tests"]
    for i in range(len(tests)):
        with open(f"{GetServerRequestDir(request)}/test{i}", "w+") as file:
            file.write(tests[i]["input"])

    # Save code
    with open(f"{GetServerRequestDir(request)}/code.xxx", "w+") as file:
        file.write(request["code"])


def process_request(jsonStr):
    request = json.loads(jsonStr)

    print(json.dumps(request, indent=2))
    try:
        validate_request(request)
        save_files_on_volume(request)
        asyncio.run(process_all_tests(request))
        print(json.dumps(request, indent=2))
    except ValueError as err:
        print(f"ValueError: {err}")


def main():
    # TODO: listen for json request instead of loading json test

    print(os.getcwd())
    with open("runtime_environment\input_test_haskell.json") as file:
        request = file.read()
        process_request(request)
    # cwd = os.getcwd()
    # with open('runtime_environment\worker_prolog') as file:
    #     request = file.read()
    #     process_request(request)
# if __name__ == "__main__":
#     startTime = time.time()
#     main()
#     endTime = time.time()
#     print(f"main() time: {endTime-startTime}")


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'tester.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/', methods=['GET', 'POST'])
    def main_function():
        if request.method == 'GET':
            return 'ALA MA KOTA'
        if request.method == 'POST':
            print(request.data)
            startTime = time.time()
            # main()
            endTime = time.time()
            response = f"time: {endTime-startTime}"
            return Response(response, mimetype='application/json')

    return app
