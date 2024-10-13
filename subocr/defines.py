from abc import ABC, abstractmethod
import threading
from typing import Callable

'''
格式化时间
返回格式: hh:mm:ss,ms  其中:
hh: 小时, 长度无限制, 若<1则省略。
mm: 分钟, 长度为2, 不足2位补0。
ss: 秒, 长度为2, 不足2位补0。
ms: 毫秒, 长度为3, 不足3位补0。
'''
def us2mmss(us:int, need_ms:bool=True, must_h=False)->str:
    ms = us // 1000
    s = ms // 1000
    m = s // 60
    h = int(m // 60)
    ms = int(ms % 1000)
    s = int(s % 60)
    m = int(m % 60)
    if h > 0:
        res = "{:d}:{:02d}:{:02d}".format(h, m, s)
    else:
        res = "{:02d}:{:02d}".format(m, s)
    if need_ms:
        res += ",{:03d}".format(ms)
    return res

class AtomicValue:
    def __init__(self, value):
        self._value = value
        self.lock = threading.Lock()
    def get(self):
        with self.lock:
            return self._value
    def set(self, value):
        with self.lock:
            self._value = value

class DataProducer(ABC):
    @abstractmethod
    def produce(self):
        pass

class AsyncDataProducer(DataProducer):
    def __init__(self, producer:DataProducer, buffer_size:int):
        self.producer = producer

        self.lock_buffer = threading.Lock()
        self.buffer = []

        self.is_running = AtomicValue(False)
        self.lock_control = threading.Lock()

        self.sem_buffer_full = threading.Semaphore(0)
        self.sem_buffer_empty = threading.Semaphore(buffer_size)

    def start(self):
        with self.lock_control:
            if self.is_running.get():
                return
            self.is_running.set(True)
            self.thread = threading.Thread(target=self._run)
            self.thread.start()

    def stop(self, process_buffered_data:Callable):
        with self.lock_control:
            if not self.is_running.get():
                return
            self.is_running.set(False)
            self.thread.join()
            for data in self.buffer:
                self.sem_buffer_full.acquire()
                process_buffered_data(data)
                self.sem_buffer_empty.release()
            self.buffer = []


    def produce(self):
        if not self.is_running.get():
            print("Fatal error: producer is not running")
            exit(1)
        self.sem_buffer_full.acquire()
        with self.lock_buffer:
            data = self.buffer.pop(0)
        self.sem_buffer_empty.release()
        return data


    def _run(self):
        try:
            while self.is_running.get():
                if not self.sem_buffer_empty.acquire(timeout=0.001):
                    continue
                data = self.producer.produce()
                with self.lock_buffer:
                    self.buffer.append(data)
                self.sem_buffer_full.release()
        except Exception as e:
            print("Error in producer thread:", e)
            exit(1)
