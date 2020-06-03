from colorama import Fore, Style
from datetime import datetime
import colorama
colorama.init()


class Logger:
    to_store_in_file = []

    LOG_CONNECTS = True
    LOG_DISCONNECTS = True
    LOG_INFO = True
    LOG_DEBUG = False
    LOG_VOTES = True
    LOG_DATABASE = True
    LOG_CACHE = True
    LOG_RSS = True

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
                Fore.WHITE + msg)
        if cls.LOG_INFO or error:
            print(text)

    @classmethod
    def log_database(cls, msg, error=False):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.MAGENTA + "[ Database ] " +
                Fore.WHITE + msg)
        if cls.LOG_DATABASE or error:
            print(text)

    @classmethod
    def log_cache(cls, msg, error=False):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTBLUE_EX + "[ Cache ] " +
                Fore.WHITE + msg)
        if cls.LOG_CACHE or error:
            print(text)

    @classmethod
    def log_rss(cls, msg, error=False):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.YELLOW + "[ RSS ] " +
                Fore.WHITE + msg)
        if cls.LOG_CACHE or error:
            print(text)
