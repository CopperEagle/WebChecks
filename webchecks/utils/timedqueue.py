"""Provides the TimedQueue class."""

from typing import Union, Any

class TimedQueue:
    """
    Multi queue that allows to specify delays between the different elements of one queue.
    The user can specify the queue using the key. Each element of that queue has a delay
    specifying 'when' after the previous element this one can be accessed.

    Note that the notion of time is arbitrary: The user passes the current time in each call.
    Thus, this may not be literal time but may be some counter.

    """

    def __init__(self):
        self.queue = {}
        self.timestamp = 0
        self.value = 1

    def enqueue(self, key, value : Any, delay : Union[int, float],
            current_time : Union[int, float]):
        """
        Add an element to the queue. Note that if the specified queue is empty, 
        that new element will be delayed by the specified amount too. Return is void.

        Parameters:
        -------------
        key: Hashable Object
            Specifies the queue. Can be any hashable object.
        value: Object
            The element to be added.
        delay: int or float
            Delay of that element
        current_time: int or float
            The current timestamp. This may e.g. be Nanoseconds after program start.

        Note that the notion of time is arbitrary: The user passes the current time in each call.
        Thus, this may not be literal time but may be some counter.
        """
        try:
            if len(self.queue[key]) > 0:
                self.queue[key].append((delay, value))
            else:
                self.queue[key].append((current_time + delay, value))
        except KeyError:
            self.queue[key] = [(current_time + delay, value)]

    def dequeue(self, current_time: Union[str, int]) -> Any:
        """
        Pop an element who has been long enough in the queue and has passed its delay requirement.

        Parameters:
        -------------
        current_time: int or float
            The current timestamp. This may e.g. be Nanoseconds after program start.
        """
        for key in self.queue:
            if len(self.queue[key]) == 0:
                continue

            ## first entry is ready to go
            if self.queue[key][0][self.timestamp] <= current_time:
                ret = self.queue[key][0] # the first element
                self.queue[key] = self.queue[key][1:] # all other elements remain
                if len(self.queue[key]) > 0: # make sure first element has nonrelative timestamp
                    self.queue[key][0] = (self.queue[key][0][0] + current_time,
                        self.queue[key][0][1])
                return ret[1]
        return None

    def isempty(self):
        """
        Returns boolean, signaling whether the queue is empty.
        """
        for (_, domain_queue) in self.queue.items():
            if len(domain_queue) > 0:
                return False
        return True
