import time
from threading import Thread, Event


class MonitorThreadBase(Thread):

    def __init__(self, routine, routine_args, interval):
        """
        Execute a thread that will execute "routine"
        each "interval" time
        :param routine: The func that should be executed
        :param routine_args: parameters passed to routine
        :param interval: Interval between each completed execution
        """
        super(MonitorThreadBase, self).__init__()

        self._routine = routine
        self._routine_args = routine_args
        self._interval = interval

        self._event = Event()
        self._event.set()

    def before_start(self):
        """
        Some action that should be executed
        before of start event_loop
        :return:
        :exception: When the before_start not is implemented
        or when the implemented can't check some status, it
        should return an exception. This exception will call
        run.finally, executing the on_completed() notifying
        that thread execution is "completed" and can be
        closed.
        """
        raise Exception('before_start not implemented yet')

    def on_completed(self, thread_event):
        """
        When the thread isn't more executing this
        callback is called
        :param Event thread_event: The Event object
        that control status of the current thread
        :return:
        """
        pass

    def run(self):
        try:
            self.before_start()

            self.__run_until_completed(
                routine=self._routine,
                routine_args=self._routine_args,
                interval=self._interval
            )

        finally:
            self.on_completed(thread_event=self._event)

    def __run_until_completed(self, routine, routine_args, interval):

        if not routine_args:
            routine_args = {}

        while self._event.is_set():

            if self.is_alive():

                is_valid_status = routine(**routine_args)

                if not is_valid_status:
                    break

                time.sleep(interval)

            else:
                break


