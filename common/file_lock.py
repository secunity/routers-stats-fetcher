import time
class FileLock:

    def __init__(self, filename: str, retries: int = 3, sleep: int = 1.0, mode: str = 'r'):
        """
        Perform file lock. Performs several attempts to lock the file
        """
        self._filename = filename
        self._retries = retries
        self._sleep = sleep
        self._mode = mode
        self._handle = None

    def __enter__(self):

        for attempt in range(self._retries):

            try:

                self._handle = open(self._filename, self._mode)

                return self._handle

            except Exception as ex:

                if attempt < self._retries:

                    time.sleep(self._sleep)

                else:

                    raise ex

    def __exit__(self, exc_type, exc_val, exc_tb):

        if self._handle and not self._handle.closed:
            self._handle.close()