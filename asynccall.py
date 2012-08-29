#coding:utf8
#TooNTonG 2012-08-13

import threading
import traceback
import logging

class Callable():
    def __init__(self, function, args, resultHandler = None, exceptHandler = None):
        self._func = function
        self._args = args
        self._resultHandler = resultHandler
        self._exceptHandler = exceptHandler

    def __call__(self):
        try:
            if self._args:
                res = self._func(*self._args)
            else:
                res = self._func()

            if self._resultHandler:
                self._resultHandler(res)
        except Exception, e:
            try:
                if self._exceptHandler:
                    self._exceptHandler(e)
            except Exception, err:
                logging.error('on async call error handler raise [%s]' % err.__str__())

class AsyncCall(object):
    def __init__(self, logger, threads = 2):
        self._lock = threading.Condition()
        self._threads = []
        self._workQueue = []
        self._stop = False
        self.logger = logger
        for i in range(threads):
            self._threads.append(self._startNewThread('aynsc-%d' % i, self._worker))

    def shutdown(self, waitForFinish):
        self._lock.acquire()
        self._stop = True
        self._workQueue = []
        threads, self._threads = self._threads, []
        self._lock.notifyAll()
        self._lock.release()

        if waitForFinish:
            for work in threads:
                work.join()

    def add(self, callable):
        self._lock.acquire()
        self._workQueue.append(callable)
        self._lock.notify_all()
        self._lock.release()

    def _startNewThread(self, threadName, target):
        t = threading.Thread(target = target)
        self._threads.append(t)
        t.setName(threadName)
        t.setDaemon(True)
        t.start()
        return t

    def _worker(self):
        self._lock.acquire()
        try:
            while True:
                while not self._workQueue and not self._stop:
                    self._lock.wait()

                if self._stop:
                    return

                if not self._workQueue:
                    continue

                task = self._workQueue.pop(0)
                self._lock.release()

                try:
                    task()
                except Exception, e:
                    self.logger.error(traceback.format_exc())

                self._lock.acquire()
        except:
            self.logger.error(traceback.format_exc())
        finally:
            self._lock.release()

if __name__ == '__main__':
    import time, logging
    def f():
        print 'no args'
    def f2(a, b):
        print 'args', a, b
        return 'xxoo'
    def h(r):
        print 'result handler', r

    a = AsyncCall(logging, 1)
    time.sleep(0.2)
    c = Callable(f, None)
    c2 = Callable(f2, ('123', '234'), h)
    a.add(c)
    a.add(c2)
    time.sleep(2)
