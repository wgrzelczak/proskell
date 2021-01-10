from flask import (Flask, request, Response, json)
import os
import docker  # Needed: pip install docker
import time
import json
import platform


WORKER_HASKELL_IMAGE_NAME = "haskell"
WORKER_HASKELL_NAME = "worker_haskell"
WORKER_PROLOG_IMAGE_NAME = "prolog"
WORKER_PROLOG_NAME = "worker_prolog"
WORKER_DATA_DIR = "/var/proskell"
SERVER_DATA_DIR = "mnt_data"

JSON_HASKELL_ID = "haskell"
JSON_PROLOG_ID = "prolog"

def GetServerMainDirectory():
    return os.path.dirname(os.path.realpath(__file__))


def GetWorkerRequestDir(request):
    return f"{WORKER_DATA_DIR}/{request['userid']}/{request['timestamp']}"


def GetServerRequestDir(request):
    return f"{SERVER_DATA_DIR}/{request['userid']}/{request['timestamp']}"


def GetServerDir():
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        return "/var/proskell"
    else:
        return os.getcwd()

def GetFiletypeByLanguage(lang):
    if lang == JSON_HASKELL_ID:
        return "hs"
    if lang == JSON_PROLOG_ID:
        return "pl"
    return ""

client = docker.from_env()


def process_all_tests(request):
    tests = request["tests"]
    lang = request['language']

    executable = f"{lang}_out"

    # Compile
    cmd = ""

    if lang == JSON_HASKELL_ID:
        cmd = f"ghc -o {executable} -O2 code.{GetFiletypeByLanguage(lang)}"
    if lang == JSON_PROLOG_ID:
        cmd = f"swipl -g main -o {executable} -c code.{GetFiletypeByLanguage(lang)}"

    if cmd == "":
        print(f"Execution command is empty!")
        return

    stdout = create_and_run_worker(cmd, request, 0)

    # Run Tests
    for i in range(len(tests)):
        print(f"Processing test {i}...")
        cmd = f"bash -c 'cat test{i} | ./{executable}'"
        stdout = create_and_run_worker(cmd, request, request["timeoutMs"])
        tests[i]["result"] = f"{stdout}"


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


def create_and_run_worker(cmd, request, timeout):
    clean_worker_container()
    imageName = ""
    containerName = ""

    if request['language'] == JSON_HASKELL_ID:
        imageName = WORKER_HASKELL_IMAGE_NAME
        containerName = WORKER_HASKELL_NAME
    elif request['language'] == JSON_PROLOG_ID:
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
           f"{GetServerMainDirectory()}/{SERVER_DATA_DIR}": {'bind': WORKER_DATA_DIR, 'mode': 'rw'}
        },
        working_dir=GetWorkerRequestDir(request)
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
    with open(f"{GetServerRequestDir(request)}/code.{GetFiletypeByLanguage(request['language'])}", "w+") as file:
        file.write(request["code"])


def process_request(json):
    request = json

    try:
        validate_request(request)
        save_files_on_volume(request)
        process_all_tests(request)
    except ValueError as err:
        print(f"ValueError: {err}")

    return request


def process_tests():
    def run_test(jsonPath):
        filepath = os.path.join(GetServerMainDirectory(), jsonPath)
        with open(filepath) as file:
            request = json.loads(file.read())
            response = process_request(request)
            print(response)

    run_test("input_test_haskell.json")
    run_test("input_test_prolog.json")

#process_tests()

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'tester.sqlite'),
    )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/', methods=['GET', 'POST'])
    def main_function():
        if request.method == 'GET':
            return 'ALA MA KOTA'
        if request.method == 'POST':
            print('POST')
            print(request)
            print(request.json)
            startTime = time.time()
            # main()
            response = process_request(request.json)
            endTime = time.time()
            return response
            # return Response(response, mimetype='application/json')

    return app
