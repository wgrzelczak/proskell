import os
import docker # Needed: pip install docker
import time
import asyncio
import json

WORKER_HASKELL_IMAGE_NAME = "worker_haskell_img:proskell"
WORKER_HASKELL_NAME = "worker_haskell"
WORKER_DATA_DIR = "/var/proskell"
SERVER_DATA_DIR = "mnt_data"

def GetWorkerRequestDir(request):
    return f"{WORKER_DATA_DIR}/{request['userid']}/{request['timestamp']}"

def GetServerRequestDir(request):
    return f"{SERVER_DATA_DIR}/{request['userid']}/{request['timestamp']}"

def GetServerDir():
    return os.getcwd()

client = docker.from_env()

async def process_all_tests(request):
    tests = request["tests"]
    for i in range(len(tests)):
        print(f"Processing test {i}...")
        cmd = f"bash -c 'cat {GetWorkerRequestDir(request)}/test{i} | runhaskell {GetWorkerRequestDir(request)}/code'"
        stdout = await process_test(cmd, request["timeoutMs"])
        tests[i]["result"] = f"{stdout}"


async def process_test(cmd, timeout):
    print("Creating worker...")
    try:
        # TODO: timeout does not work now
        out = await asyncio.wait_for(
            asyncio.gather(create_and_run_worker(cmd)),
            timeout = timeout
        )
        print(f"Worker stdout: {out}")
        return out
    except asyncio.TimeoutError:
        print('Worker timeout!')
        return "Timeout"


def clean_worker_container():
    try:
        worker = client.containers.get(WORKER_HASKELL_NAME)
        worker.remove(force = True)
    except:
        pass

async def create_and_run_worker(cmd):
    clean_worker_container()

    out = client.containers.run(
        image = WORKER_HASKELL_IMAGE_NAME,
        name = WORKER_HASKELL_NAME,
        entrypoint = cmd,
        remove = True,
        volumes = {
            f"{GetServerDir()}/{SERVER_DATA_DIR}":{ 'bind': WORKER_DATA_DIR, 'mode': 'rw' }
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
    if request["language"] not in ["haskell"]:
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
    with open(f"{GetServerRequestDir(request)}/code", "w+") as file:
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
    with open("test_input.json") as file:
        request = file.read()
        process_request(request)
    
if __name__ == "__main__":
    startTime = time.time()
    main()
    endTime = time.time()
    print(f"main() time: {endTime-startTime}")