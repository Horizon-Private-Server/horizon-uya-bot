

class CircularList:
    def __init__(self, items, circular=False, casttype=tuple):

        assert len(items) > 1

        self.circular = circular
        self.direction = 'forward'
        self.size = len(items)
        self.casttype = casttype
        if self.size == 2:
            self.circular = True
        self.circular_list = [None] * self.size
        self.current_index = 0  # Pointer to the current position
        for item in items:
            self.append(self.casttype(item))

    def append(self, item):
        """Append an item to the circular list."""
        self.circular_list[self.current_index] = item
        self.current_index = (self.current_index + 1) % self.size

    def pop(self):
        if self.circular:
            """Pop an item from the circular list."""
            if self.current_index == 0:
                self.current_index = self.size - 1
            else:
                self.current_index = self.current_index - 1
        else:
            if self.current_index == 0:
                self.direction = 'forward'
                self.current_index = 1
            elif self.current_index == self.size - 1:
                self.direction = 'backward'
                self.current_index -= 1
            elif self.direction == 'forward':
                self.current_index += 1
            elif self.direction == 'backward':
                self.current_index -= 1

        item = self.circular_list[self.current_index]
        if self.casttype is tuple:
            return list(item)
        return self.casttype(item)

    def peek(self):
        return self.circular_list[self.current_index]

    def __eq__(self, other):
        if not isinstance(other, list):
            return False
        if len(other) != self.size:
            return False
        queue_set = set(self.circular_list)
        return queue_set == set([self.casttype(a) for a in other])