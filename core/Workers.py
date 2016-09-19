"""
    Class Name : Workers

    Description:
        Class that will spawn threads to do work seperate to the main logic

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import threading
import time
import logging
import traceback

try:
    import queue
except ImportError:
    import Queue as queue

class Workers():
    def __init__(self, queue_size, threads):
        self.logger = logging.getLogger(__name__)

        # Init worker list and queue
        self._threads = []
        self.tasks = queue.Queue(queue_size)

        self.logger.info("Spawning " + str(threads) + " worker threads.")

        # Create worker threads
        self.threads = threads

    def queue(self, callable, *args, **kwargs):
        """
            Summary:
                Puts task on the task queue for workers to pull from.
                If task queue is full; will block until space opens up

            Args:
                callable (func): Function object to be invoked by a Worker
                *args (list): Positional arguments passed to callable
                **kwargs (dict): Keyword arguments passed to callable

            Returns:
                None
        """
        if(self.tasks.full()):
            self.logger.warning("Task queue is full. Consider raising the task queue size.")

        task = (callable, args, kwargs)
        self.tasks.put(task, block=True)

    def dequeue(self):
        """
            Summary:
                Removes a task from the queue. Will block for half a second, and raise Queue.Empty exception when nothing is in queue

            Args:
                None

            Returns:
                None
        """
        return self.tasks.get(block=True, timeout=0.1)

    @property
    def threads(self):
        return len(self._threads)

    @threads.setter
    def threads(self, number):
        while len(self._threads) < number:
            new_worker = Worker(self, len(self._threads) + 1)
            self._threads.append(new_worker)
            new_worker.start()

        while len(self._threads) > number:
            worker = self._threads.pop()
            worker.stop()
            worker.join()

class Worker(threading.Thread):
    def __init__(self, tasks, num):

        # Call super constructor for thread to name it
        super(Worker, self).__init__(name="WorkerThread" + str(num))
        self.name = "WorkerThread" + str(num)
        self.logger = logging.getLogger(self.name)

        # Sentinal value used to kill our thread
        self.running = True

        # Reference to parent object to get tasks from
        self.tasks = tasks

    def stop(self):
        """
            Summary:
                Tells the thread that it should stop running

            Args:
                None

            Returns:
                None
        """
        self.running = False

    def run(self):
        """
            Summary:
                Part of the Thread superclass; this method is where the logic for our thread resides.
                Loops continously while trying to pull a task from the task queue and execute that task

            Args:
                None

            Returns:
                None
        """
        while(self.running):
            # Dequeue task will block and thread will wait for a task
            try:
                task = self.tasks.dequeue()
            except queue.Empty as e:
                continue

            # Get task data
            callable = task[0]
            args = task[1]
            kwargs = task[2]

            # Invoke task
            try:
                callable(*args, **kwargs)
            except BaseException as e:
                self.logger.warning("Exception occured in {}:\n {}".format(self.name, traceback.format_exc()))
                continue
