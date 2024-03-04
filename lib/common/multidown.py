# !/usr/bin/env python
# coding: utf-8
from threading import Thread


class DownloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            param, execution = self.queue.get()
            try:
                execution(param)
            finally:
                self.queue.task_done()
