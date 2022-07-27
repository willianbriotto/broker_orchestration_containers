from src.monitor.monitor_thread_base import MonitorThreadBase


class MonitorThread(MonitorThreadBase):

    def __init__(self, routine, routine_args, interval, on_completed_callback):
        super(MonitorThread, self).__init__(
            routine=routine,
            routine_args=routine_args,
            interval=interval
        )

        self._on_completed_callback = on_completed_callback

    def before_start(self):

        return True

    def on_completed(self, thread_event):

        if self._on_completed_callback:
            self._on_completed_callback(thread_event)
