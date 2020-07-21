import asyncio
import discord

from discord.ext import commands
from datetime import datetime, timedelta


class TimeOut:
    def __int__(self):
        pass


class CooldownError(Exception):
    """ Raised when cooldown """


class TimeoutManager:
    def __init__(self):
        self.time_out = TimeOut()
        self._loop = asyncio.get_event_loop()

    def add_timeout(self, time_out):
        setattr(self.time_out, str(time_out), time_out)

    def remove_timeout(self, time_out):
        delattr(self.time_out, str(time_out))

    async def on_timeout(self, time_out, **kwargs):
        if hasattr(self.time_out, str(time_out)):
            timeout = getattr(self.time_out, str(time_out))
            return await timeout.is_on_timeout(**kwargs)
        else:
            raise AttributeError('No timeout called {}'.format(time_out))


class NewTimeout:
    def __init__(self, name, **kwargs):
        self.name = name  # name of object / timeout
        self.time_outs = {}  # Used for mapping members timeouts
        self.severity = kwargs.get('severity', 2)  # Changes how sharply the time increases
        self.max_time = kwargs.get('max_time', (0, 0, 0, 5, 0))  # Max time (tuple) (D, H, M, S, MS)
        self.start_timeout = kwargs.get('base_timeout', (0, 0, 0, 0, 500))  # timeout starts with (D, H, M, S, MS) time
        self.alert_enabled = kwargs.get('alert_on_spam', False)  # Bool, triggers an alert event if spam detected
        self.max_offences = kwargs.get('max_offences', 5)  # Amount of limits they get before event
        self.call_func = kwargs.get('alert_func', None)

    async def is_on_timeout(self, **kwargs):
        id_ = kwargs.get('id', None)
        if id_ is not None:  # we check a specific user / thing's timeout
            if id_ in self.time_outs:
                selected_timeout = self.time_outs[id_]
                if selected_timeout['time_stamp'] > datetime.now():
                    time_stamp = selected_timeout['time_stamp'] - datetime.now()
                    new_time = time_stamp * (1 + self.severity)
                    max_time = timedelta(
                        days=self.max_time[0],
                        hours=self.max_time[1],
                        minutes=self.max_time[2],
                        seconds=self.max_time[3],
                        milliseconds=self.max_time[4]
                    )

                    if new_time >= max_time:
                        new_time = max_time

                    selected_timeout['time_stamp'] += new_time
                    selected_timeout['repeated_offence_no'] += 1
                    if self.alert_enabled:
                        if selected_timeout['repeated_offence_no'] > self.max_offences:
                            if self.call_func is None:
                                raise RuntimeError(
                                    'Alert on spam is enabled, but you want passed a function to be called.')
                            else:
                                if asyncio.iscoroutinefunction(self.call_func):
                                    await self.call_func(id_)
                                else:
                                    self.call_func(id_)
                    self.time_outs[id_] = selected_timeout
                    return True, selected_timeout['time_stamp']

                else:  # they're not on a timeout lets reset that timestamp and return false
                    self.time_outs[id_]['time_stamp'] = datetime.now() + timedelta(days=self.start_timeout[0],
                                                                                   hours=self.start_timeout[1],
                                                                                   minutes=self.start_timeout[2],
                                                                                   seconds=self.start_timeout[3],
                                                                                   milliseconds=self.start_timeout[4])
                    self.time_outs[id_]['repeated_offence_no'] = 0
                    return False, selected_timeout['time_stamp']
            else:  # User is not in the existing timeout list, return false after adding them to it
                delta = timedelta(days=self.start_timeout[0],
                                  hours=self.start_timeout[1],
                                  minutes=self.start_timeout[2],
                                  seconds=self.start_timeout[3],
                                  milliseconds=self.start_timeout[4])

                self.time_outs[id_] = {
                    'time_stamp': datetime.now() + delta,
                    'repeated_offence_no': 0,
                }

                return False, self.time_outs[id_]['time_stamp']
        else:  # now we go through all timeouts
            active_timeouts = []
            for key, timeout in self.time_outs.items():
                if timeout['time_stamp'] <= datetime.now():
                    del self.time_outs[key]
                else:
                    active_timeouts.append((key, timeout))
            return active_timeouts

    def __repr__(self):
        return self.name



if __name__ == "__main__":  # Use this for testing
    pass
