import tornado
import time
import sys
import logging
from concurrent import futures

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.concurrent import run_on_executor

from odin.adapters.parameter_tree import ParameterTree, ParameterTreeError
from odin._version import get_versions as get_odin_versions

from workshop._version import __version__ as workshop_version

class WorkshopError(Exception):
    """Simple exception class to wrap lower-level exceptions."""

    pass


class WorkshopController():
    """WorkshopController - class that extracts and stores information about system-level parameters."""

    # Thread executor used for background tasks
    executor = futures.ThreadPoolExecutor(max_workers=1)

    def __init__(self, background_task_enable, background_task_interval):
        """Initialise the WorkshopController object.

        This constructor initlialises the WorkshopController object, building a parameter tree and
        launching a background task if enabled
        """
        # Save arguments
        self.background_task_enable = background_task_enable
        self.background_task_interval = background_task_interval

        # Store initialisation time
        self.init_time = time.time()

        # Get package version information
        odin_versions = get_odin_versions()

        # Set the background task counters to zero
        self.background_ioloop_counter = 0
        self.background_thread_counter = 0

        # Build a parameter tree for the background task
        bg_task = ParameterTree({
            'ioloop_count': (lambda: self.background_ioloop_counter, None),
            'thread_count': (lambda: self.background_thread_counter, None),
            'enable': (lambda: self.background_task_enable, self.set_task_enable),
            'interval': (lambda: self.background_task_interval, self.set_task_interval),
        })

        # Store all information in a parameter tree
        self.param_tree = ParameterTree({
            'odin_version': odin_versions["version"],
            'workshop_version': workshop_version,
            'tornado_version': tornado.version,
            'server_uptime': (self.get_server_uptime, None),
            'background_task': bg_task 
        })

        # Launch the background task if enabled in options
        if self.background_task_enable:
            self.start_background_tasks()

    def get_server_uptime(self):
        """Get the uptime for the ODIN server.

        This method returns the current uptime for the ODIN server.
        """
        return time.time() - self.init_time

    def get(self, path):
        """Get the parameter tree.

        This method returns the parameter tree for use by clients via the Workshop adapter.

        :param path: path to retrieve from tree
        """
        return self.param_tree.get(path)

    def set(self, path, data):
        """Set parameters in the parameter tree.

        This method simply wraps underlying ParameterTree method so that an exceptions can be
        re-raised with an appropriate WorkshopError.

        :param path: path of parameter tree to set values for
        :param data: dictionary of new data values to set in the parameter tree
        """
        try:
            self.param_tree.set(path, data)
        except ParameterTreeError as e:
            raise WorkshopError(e)

    def cleanup(self):
        """Clean up the WorkshopController instance.

        This method stops the background tasks, allowing the adapter state to be cleaned up
        correctly.
        """
        self.stop_background_tasks()

    def set_task_interval(self, interval):
        """Set the background task interval."""
        logging.debug("Setting background task interval to %f", interval)
        self.background_task_interval = float(interval)
        
    def set_task_enable(self, enable):
        """Set the background task enable."""
        enable = bool(enable)

        if enable != self.background_task_enable:
            if enable:
                self.start_background_tasks()
            else:
                self.stop_background_tasks()

    def start_background_tasks(self):
        """Start the background tasks."""
        logging.debug(
            "Launching background tasks with interval %.2f secs", self.background_task_interval
        )

        self.background_task_enable = True

        # Register a periodic callback for the ioloop task and start it
        self.background_ioloop_task = PeriodicCallback(
            self.background_ioloop_callback, self.background_task_interval * 1000
        )
        self.background_ioloop_task.start()

        # Run the background thread task in the thread execution pool
        self.background_thread_task()

    def stop_background_tasks(self):
        """Stop the background tasks."""
        self.background_task_enable = False
        self.background_ioloop_task.stop()

    def background_ioloop_callback(self):
        """Run the adapter background IOLoop callback.

        This simply increments the background counter before returning. It is called repeatedly
        by the periodic callback on the IOLoop.
        """

        if self.background_ioloop_counter < 10 or self.background_ioloop_counter % 20 == 0:
            logging.debug(
                "Background IOLoop task running, count = %d", self.background_ioloop_counter
            )

        self.background_ioloop_counter += 1

    @run_on_executor
    def background_thread_task(self):
        """The the adapter background thread task.

        This method runs in the thread executor pool, sleeping for the specified interval and 
        incrementing its counter once per loop, until the background task enable is set to false.
        """

        sleep_interval = self.background_task_interval

        while self.background_task_enable:
            time.sleep(sleep_interval)
            if self.background_thread_counter < 10 or self.background_thread_counter % 20 == 0:
                logging.debug(
                    "Background thread task running, count = %d", self.background_thread_counter
                )
            self.background_thread_counter += 1

        logging.debug("Background thread task stopping")