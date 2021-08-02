import time
from datetime import datetime

import colorama
from colorama import Fore, Style

colorama.init()


class Logger:
    to_store_in_file = []

    LOG_CONNECTS = True
    LOG_DISCONNECTS = True
    LOG_INFO = True
    LOG_DEBUG = False
    LOG_DBL = True
    LOG_DATABASE = True
    LOG_CACHE = True
    LOG_RSS = True
    LOG_BROADCASTS = True

    @classmethod
    def log_shard_connect(cls, shard_id, error=False):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTCYAN_EX + "[ Shard Connected ] " +
                Fore.CYAN + f" Shard {shard_id}  | " +
                Fore.WHITE + "CONNECTED!")
        if cls.LOG_CONNECTS or error:
            print(text)

    @classmethod
    def log_shard_disconnect(cls, error=False):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTRED_EX + "[ Shard Disconnected ] " +
                Fore.CYAN + f" Shard UNKNOWN  | " +
                Fore.WHITE + "LOST CONNECTION!")
        if cls.LOG_DISCONNECTS or error:
            print(text)

    @classmethod
    def log_info(cls, msg, error=False):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTGREEN_EX + "[ Info ] " +
                Fore.WHITE + msg + Fore.WHITE)
        if cls.LOG_INFO or error:
            print(text)

    @classmethod
    def log_database(cls, msg, error=False):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.MAGENTA + "[ Database ] " +
                Fore.WHITE + msg + Fore.WHITE)
        if cls.LOG_DATABASE or error:
            print(text)

    @classmethod
    def log_cache(cls, msg, error=False):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTBLUE_EX + "[ Cache ] " +
                Fore.WHITE + msg + Fore.WHITE)
        if cls.LOG_CACHE or error:
            print(text)

    @classmethod
    def log_rss(cls, msg, error=False):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.YELLOW + "[ RSS ] " +
                Fore.WHITE + msg + Fore.WHITE)
        if cls.LOG_RSS or error:
            print(text)

    @classmethod
    def log_broadcast(cls, msg, error=False):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.YELLOW + "[ BROADCASTS ] " +
                Fore.WHITE + msg + Fore.WHITE)
        if cls.LOG_BROADCASTS or error:
            print(text)

    @classmethod
    def log_dbl(cls, msg, error=False):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTMAGENTA_EX + "[ TOP.GG ] " +
                Fore.WHITE + msg + Fore.WHITE)
        if cls.LOG_BROADCASTS or error:
            print(text)


class Timer:
    timings = {}

    @classmethod
    def fetch_timings(cls):
        return cls.timings

    @classmethod
    def reset_timings(cls):
        cls.timings = {}

    @classmethod
    def timeit(cls, func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            output = func(*args, **kwargs)
            end_time = time.time()
            cls.timings[str(func.__qualname__)] = end_time - start_time
            return output

        return wrapper
