import concurrent.futures
import random
import time
import threading

class Ticker:
    def __init__(self, rps):
        self._lock = threading.Lock()
        self._last = 0
        self._wait = 1.0 / rps

    def tick(self):
        self._lock.acquire()
        now = time.time()
        wait = max(this._wait - (now - self._last), 0)
        time.sleep(wait)
        self._last = now + wait
        self._lock.release()

def exectasks(rps, tasks, consumer):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        ticker = Ticker(rps)
        def exec_task(task):
            ticker.tick()
            consumer(task)
        futures = {executor.submit(consumer, task): task for task in tasks}
        result = [future.result() for future in concurrent.futures.as_completed(futures)]

    return result

