# -*- coding: UTF-8 -*-

'''工作线程
'''

import time
import threading
from queue import Queue


class Task(object):
    '''任务
    '''

    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def run(self):
        return self._func(*self._args, **self._kwargs)


class WorkThread(object):
    '''
    '''

    def __init__(self):
        self._thread = threading.Thread(target=self._work_thread)
        self._thread.setDaemon(True)
        self._run = True
        self._task_queue = Queue()
        self._thread.start()

    def _work_thread(self):
        '''
        '''
        while self._run:
            if self._task_queue.empty():
                time.sleep(0.1)
                continue
            task = self._task_queue.get()
            try:
                task.run()
            except:
                import traceback
                traceback.print_exc()

    def post_task(self, func, *args, **kwargs):
        '''发送任务
        '''
        task = Task(func, *args, **kwargs)
        self._task_queue.put(task)