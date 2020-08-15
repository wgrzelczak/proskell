import os
import docker # Needed: pip install docker
import time


WORKER_HASKELL_IMAGE_NAME = "worker_haskell_img:proskell"
WORKER_HASKELL_NAME = "worker_haskell"

client = docker.from_env()

def clean_worker_container():
    try:
        worker = client.containers.get(WORKER_HASKELL_NAME)
        worker.remove(force = True)
    except:
        pass

def create_worker(cmd):
    clean_worker_container()

    worker = client.containers.run(
        image = WORKER_HASKELL_IMAGE_NAME,
        name = WORKER_HASKELL_NAME,
        entrypoint = cmd,
        detach = True
    )
    return worker


def main():
    print("Creating worker...")

    cmd = f"bash -c 'time (echo hello world; echo 2; sleep 1; echo 3)'"
    #cmd = f"bash -c time echo"

    worker = create_worker(cmd)

    #while worker.status is not "exit":
    #    print(worker.status)
    print("Sleeping...")
    time.sleep(3)

    print("Results:")
    print(worker.logs().decode())

    print("Removing container...")
    worker.remove(force = True)


if __name__ == "__main__":
    startTime = time.time()
    main()
    endTime = time.time()
    print(f"main() time: {endTime-startTime}")