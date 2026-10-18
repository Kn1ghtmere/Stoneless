import time 


class Reminder:

    def __init__(self, interval, snooze, clock=time.time):
        self.interval = interval
        self.snooze_for = snooze
        self.clock = clock
        self.due_at = clock() + interval

    def reset(self):
        self.due_at = self.clock() + self.interval


    def snooze(self):
        self.due_at = self.clock() + self.snooze_for


    def remaining(self):
        return max(0, self.due_at - self.clock())

    def is_due(self):
        return self.clock() >= self.due_at