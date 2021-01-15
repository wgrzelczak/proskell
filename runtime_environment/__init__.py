from flask import (Flask, request, Response, json, jsonify)
import os
import docker
import time
import json
import platform
import shutil
from bson.json_util import loads, dumps
# import subprocess

from .debugger import initialize_flask_server_debugger_if_needed

initialize_flask_server_debugger_if_needed()

SUCCESS = 0
ERROR = 1

WORKER_HASKELL_IMAGE_NAME = "haskell"
WORKER_HASKELL_NAME = "worker_haskell"
WORKER_PROLOG_IMAGE_NAME = "prolog"
WORKER_PROLOG_NAME = "worker_prolog"
WORKER_DATA_DIR = "/var/proskell"
SERVER_DATA_DIR = "mnt_data"

JSON_HASKELL_ID = "haskell"
JSON_PROLOG_ID = "prolog"

def GetWorkingDir():
    return os.path.dirname(os.path.realpath(__file__))

def GetServerMountDir():
    return os.path.join(GetWorkingDir(), SERVER_DATA_DIR)

def GetServerRequestDir(request):
    return f"{GetServerMountDir()}/{request['userid']}/{request['timestamp']}"

def GetWorkerRequestDir(request):
    return f"{WORKER_DATA_DIR}/{request['userid']}/{request['timestamp']}"

def GetFiletypeByLanguage(lang):
    if lang == JSON_HASKELL_ID:
        return "hs"
    if lang == JSON_PROLOG_ID:
        return "pl"
    return ""

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

    (status, stdout) = create_and_run_worker(cmd, request, 0)
    request["result_status"] = status
    request["result_stdout"] = stdout

    if status is not SUCCESS:
        return

    # Run Tests
    for i in range(len(tests)):
        print(f"Processing test {i}...")
        cmd = f"bash -c 'cat test{i} | ./{executable}'"
        (status, stdout) = create_and_run_worker(cmd, request, request["timeoutMs"])
        tests[i]["result_status"] = status
        tests[i]["result_stdout"] = stdout


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


def create_and_run_worker(cmd, request, timeoutMs):
    clean_worker_container()

    imageName = ""
    containerName = ""

    if timeoutMs is not SUCCESS:
        cmd = f"timeout -s USR2 {timeoutMs * 0.001} {cmd}"
    # cmd = 'ls /var/haskell/151617/1598630096'

    if request['language'] == JSON_HASKELL_ID:
        imageName = WORKER_HASKELL_IMAGE_NAME
        containerName = WORKER_HASKELL_NAME
    elif request['language'] == JSON_PROLOG_ID:
        imageName = WORKER_PROLOG_IMAGE_NAME
        containerName = WORKER_PROLOG_NAME

    if (not imageName) or (not containerName):
        print("Cannot create worker! Language type is mismatched!")
        return (ERROR, "Internal error!")

    # print(f'GetServerMountDir {GetServerMountDir()}')
    # print(f'WORKER_DATA_DIR {WORKER_DATA_DIR}')
    # print(f'GetWorkerRequestDir {GetWorkerRequestDir(request)}')
    # bashCmd = ["pwd"]
    # process = subprocess.Popen(bashCmd, stdout=subprocess.PIPE)
    # output, error = process.communicate()
    # print(output)

    try:
        stdout = client.containers.run(
            image=imageName,
            name=containerName,
            entrypoint=cmd,
            # remove=True,
            volumes={
                GetServerMountDir(): {'bind': WORKER_DATA_DIR, 'mode': 'rw'}
            },
            working_dir=GetWorkerRequestDir(request)
            
        )
        print(stdout.decode("utf-8"))
        return (SUCCESS, stdout.decode("utf-8"))

    except docker.errors.ContainerError as err:
        # 124 is a SIG_USR2, which comes from timeout
        if err.exit_status == 124:
            return (ERROR, "Timeout!")
        return (ERROR, err.stderr.decode("utf-8"))
    except Exception as err:
        print(err)
        return (ERROR, "Internal error!")


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


def clean_request_dir(request):
    shutil.rmtree(GetServerRequestDir(request), ignore_errors=True)

def process_request(request):
    try:
        validate_request(request)
        save_files_on_volume(request)
        process_all_tests(request)
        clean_request_dir(request)
    except ValueError as err:
        request["result_status"] = ERROR
        request["result_stdout"] = f"Validation failed with error: {err}"

    return request


def run_debug_tests():
    def run_test(jsonPath):
        filepath = os.path.join(GetServerDir(), jsonPath)
        with open(filepath) as file:
            request = json.loads(file.read())
            response = process_request(request)
            print(response)

    run_test("input_test_haskell.json")
    run_test("input_test_prolog.json")

client = docker.from_env()
#run_debug_tests()

def parse_json(data):
    return json.loads(dumps(data))

def create_app():

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/', methods=['POST'])
    def main_function():
        if request.method == 'POST':
            response = process_request(request.json)
            # return response
            print('ok')
            return parse_json(response)

    return app
