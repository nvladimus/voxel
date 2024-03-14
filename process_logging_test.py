import logging
import multiprocessing
from multiprocessing import Queue

class QueueHandler(logging.Handler):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def emit(self, record):
        self.queue.put_nowait(record)

def worker_process(queue):
    # Initialize logging in the worker process
    logger = logging.getLogger()
    handler = QueueHandler(queue)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Log messages
    logger.info('Worker process started')
    # Simulate some work
    logger.info('Worker process finished')

if __name__ == '__main__':
    log_queue = Queue()

    # Set up logging in the main process
    logger = multiprocessing.get_logger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    processes = []
    for _ in range(3):
        p = multiprocessing.Process(target=worker_process, args=(log_queue,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    while not log_queue.empty():
        record = log_queue.get()
        logger.handle(record)