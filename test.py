import threading
import uvicorn

def run():
    uvicorn.run("fa:app")

def _exit():
    import time
    import gc

    from uvicorn.supervisors import Multiprocess, ChangeReload
    from uvicorn.server import Server
    time.sleep(5)
    for obj in gc.get_objects():
        if isinstance(obj, (ChangeReload, Multiprocess, Server)):
            print(obj)
            print(callable(obj))
            if isinstance(obj, Server):
                obj.should_exit = True
            else:
                obj.should_exit.set()

threading.Thread(target=run).start()

_exit()