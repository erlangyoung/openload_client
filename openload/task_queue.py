import threading
import queue
import logging

class TaskQueue(object):
    def __init__(self, thread_number=1):
        self._threads = []
        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)
        self._task_queue = queue.Queue()
        
        count = 0
        while count < thread_number:
            t = threading.Thread(target=self.run)
            self._threads.append(t)
            count += 1

    def start(self):
        with self._lock:
            self._running = True
            for t in self._threads:
                t.start()

    def stop(self):
        with self._lock:
            self._running = False

    def queue(self, task):
        with self._cv:
            self._task_queue.put(task)
            self._cv.notify()

    def run(self):
        task=None
        while self._running:
            with self._cv:
                while self._task_queue.empty():
                    self._cv.wait()
                #self._cv.wait_for((lambda x: x.empty() == False)(self._task_queue), timeout=100)
                task = self._task_queue.get()
            try:         
                task()
            except Exception as e:
                logging.error(e)
                print(e)
            
