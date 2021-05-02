class Money:
    def __init__(self, value):
        self._value = float(value)

    def __add__(self, rhs):
        if isinstance(rhs, Money):
            rhs = rhs._value
        return Money(self._value + rhs)

    def __sub__(self, rhs):
        if isinstance(rhs, Money):
            rhs = rhs._value
        return Money(self._value - rhs)

    def __mul__(self, rhs):
        if isinstance(rhs, Money):
            rhs = rhs._value
        return Money(self._value * rhs)

    def __truediv__(self, rhs):
        if isinstance(rhs, Money):
            rhs = rhs._value
        return Money(self._value / rhs)

    def __floordiv__(self, rhs):
        if isinstance(rhs, Money):
            rhs = rhs._value
        return Money(self._value // rhs)

    def __radd__(self, lhs):
        return self.__add__(lhs)

    def __rmul__(self, lhs):
        return self.__mul__(lhs)

    def __rsub__(self, lhs):
        if isinstance(lhs, Money):
            lhs = lhs._value
        return Money(lhs - self._value)

    def __rtruediv__(self, lhs):
        if isinstance(lhs, Money):
            lhs = lhs._value
        return Money(lhs / self._value)

    def __rfloordiv__(self, lhs):
        if isinstance(lhs, Money):
            lhs = lhs._value
        return Money(lhs // self._value)

    def __pow__(self, rhs):
        if isinstance(rhs, Money):
            rhs = rhs._value
        return Money(self._value ** rhs)

    def __lt__(self, rhs):
        if isinstance(rhs, Money):
            rhs = rhs._value
        return self._value < rhs

    def __lte__(self, rhs):
        if isinstance(rhs, Money):
            rhs = rhs._value
        return self._value <= rhs

    def __gt__(self, rhs):
        if isinstance(rhs, Money):
            rhs = rhs._value
        return self._value > rhs

    def __gte__(self, rhs):
        if isinstance(rhs, Money):
            rhs = rhs._value
        return self._value >= rhs

    def __abs__(self):
        return Money(abs(self._value))

    def __divmod__(self, rhs):
        if isinstance(rhs, Money):
            rhs = rhs._value
        return self._value // rhs, self._value % rhs

    def __float__(self):
        return self._value

    def __int__(self):
        return int(self._value)

    def __str__(self):
        if self._value < 0:
            string = "-$"
        else:
            string = "$"

        string += str(abs(round(self._value, 2)))
        if string[-2] == ".":
            string += "0"
        return string

    def __repr__(self):
        return "'" + self.__str__() + "'"
