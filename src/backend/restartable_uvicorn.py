import os
import signal
import threading
import time
from typing import Any, List, Dict

from uvicorn.workers import UvicornWorker

"""
    Thanks to this solution to make gonicurn reload after the changes.
    gunicorn has issues to reload with UvicornWorker class.
    Here you can read more about the issue and solution
    https://github.com/benoitc/gunicorn/issues/2339#issuecomment-867481389
"""


class ReloaderThread(threading.Thread):

    def __init__(self, worker: UvicornWorker, sleep_interval: float = 1.0):
        super().__init__()
        self.setDaemon(True)
        self._worker = worker
        self._interval = sleep_interval

    def run(self) -> None:
        while True:
            if not self._worker.alive:
                os.kill(os.getpid(), signal.SIGINT)
            time.sleep(self._interval)


class RestartableUvicornWorker(UvicornWorker):

    CONFIG_KWARGS = {"loop": "uvloop", "http": "httptools"}

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]):
        super().__init__(*args, **kwargs)
        self._reloader_thread = ReloaderThread(self)

    def run(self) -> None:
        if self.cfg.reload:
            self._reloader_thread.start()
        super().run()
