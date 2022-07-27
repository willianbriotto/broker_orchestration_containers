from threading import Thread, Event

from src.monitor.monitor_thread import MonitorThread


class ManagerMonitors:
    """
    Manages the creation of threads that
    monitor the status of the container
    """

    def __int__(self):
        pass

    def __stop_execution(self, thread_event: Event):
        """
        Pause/stop execution of the threads
        :param thread_event:
        :return:
        """
        try:
            print('Trying to close the thread', flush=True)
            thread_event.clear()
            print('Close the thread with success', flush=True)
        except Exception as e:
            print('Error when try close the monitor thread', flush=True)
            print(e)

    def create_monitor(self, routine, routine_args, interval):
        """
        Start a new thread to check status of the container
        :param routine:
        :param routine_args:
        :param interval:
        :return:
        """
        MonitorThread(
            routine=routine,
            routine_args=routine_args,
            interval=interval,
            on_completed_callback=self.__stop_execution
        ).start()
