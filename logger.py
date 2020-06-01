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

    @classmethod
    def log_shard_connect(cls, shard_id):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTCYAN_EX + "[ Shard Connected ] " +
                Fore.CYAN + f" Shard {shard_id}  | " +
                Fore.WHITE + "CONNECTED!")
        if cls.LOG_CONNECTS:
            print(text)

    @classmethod
    def log_shard_disconnect(cls):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTRED_EX + "[ Shard Disconnected ] " +
                Fore.CYAN + f" Shard UNKOWN  | " +
                Fore.WHITE + "LOST CONNECTION!")
        if cls.LOG_DISCONNECTS:
            print(text)

    @classmethod
    def log_info(cls, msg):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTGREEN_EX + "[ Info ] " +
                Fore.WHITE + msg)
        if cls.LOG_INFO:
            print(text)

    @classmethod
    def log_database(cls, msg):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.MAGENTA + "[ Database ] " +
                Fore.WHITE + msg)
        if cls.LOG_DATABASE:
            print(text)

    @classmethod
    def log_cache(cls, msg):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTBLUE_EX + "[ Cache ] " +
                Fore.WHITE + msg)
        if cls.LOG_CACHE:
            print(text)