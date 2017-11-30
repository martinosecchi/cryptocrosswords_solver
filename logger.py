import Queue
import threading
import datetime
import inspect
import time

def logapp(level, message, filename='lw.log'):
    logfile = open(filename, 'a+', 0)
    now = datetime.datetime.now()
    caller = inspect.currentframe().f_back
    fn, lineno, func, _1, _2 = inspect.getframeinfo(caller)
    msg = "{}.{} [{}] {}:{} {} - {}\n".format(now.strftime('%d %b %H:%M:%S'), now.microsecond, level, fn, lineno, func, message)
    logfile.write(msg)
    logfile.flush()
    logfile.close()

class logger_thread(threading.Thread):
    def __init__(self, filename='lw.log'):
        self.q = Queue.Queue()
        self._do_stop = False
        self._wait_empty = False
        self._logfile = open(filename, 'w+', 0)
        super(logger, self).__init__()
    def logapp(self, level, message):
        if self._wait_empty:
            return
        now = datetime.datetime.now()
        caller = inspect.currentframe().f_back
        fn, lineno, func, _1, _2 = inspect.getframeinfo(caller)
        msg = "{}.{} [{}] {}:{} {} - {}\n".format(now.strftime('%d %b %H:%M:%S'), now.microsecond, level, fn, lineno, func, message)
        self.q.put(msg)
    def start(self):
        super(logger, self).start()
    def stop_nowait(self):
        self._do_stop = True
    def stop_wait(self):
        self._wait_empty = True
    def run(self):
        self._logfile.write('starting logger.')
        while not self._do_stop:
            m = None
            try:
                m = self.q.get_nowait()
            except Queue.Empty:
                if self._wait_empty:
                    break
            if m:
                self._logfile.write(m)
        self._logfile.write('closing logger.')
        self._logfile.close()

# logger = logger()

# def logapp(level, msg):
#     logger.logapp(level, msg)