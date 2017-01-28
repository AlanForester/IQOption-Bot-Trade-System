from threading import Thread


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, verbose)
        self._return = None

    def run(self):
        try:
            if self._Thread__target:
                self._return = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._Thread__target, self._Thread__args, self._Thread__kwargs

    def get_result(self, timeout=None):
        Thread.join(self, timeout)
        return self._return
