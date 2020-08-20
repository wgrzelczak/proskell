import os
import docker # Needed: pip install docker
import time
import asyncio

WORKER_HASKELL_IMAGE_NAME = "worker_haskell_img:proskell"
WORKER_HASKELL_NAME = "worker_haskell"

client = docker.from_env()

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
        remove = True
    )
    return out


async def main():
    print("Creating worker...")

    cmd = f"bash -c 'time (echo hello world; echo 2; sleep 20; echo 3)'"
    #cmd = f"bash -c time echo"


    try:
        out = await asyncio.wait_for(
            asyncio.gather(create_and_run_worker(cmd)),
            timeout=1.0
        )
        print("Results:")
        print(f"Out: {out}")
    except asyncio.TimeoutError:
        print('timeout!')
    


if __name__ == "__main__":
    startTime = time.time()
    asyncio.run(main())
    endTime = time.time()
    print(f"main() time: {endTime-startTime}")