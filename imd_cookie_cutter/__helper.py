#!/usr/bin/python3
#
#
#

# Progress bar
class ProgressBar():
    def __init__(self, length=20, endval = 100, chars=("[","#","]")):
        self.__length = length
        self.__current = 0
        self.__endval = endval
        self.__chars = chars

    def increase(self):
        self.__current += 1
        percent = self.__current/self.__endval
        nchars = int(percent*self.__length)

        out = "\r" + self.__chars[0]
        out += self.__chars[1]*nchars
        out += " "*(self.__length - nchars)
        out += self.__chars[2] + " {:.2f}%".format(percent*100)

        print(out, end="")


# Statements as returnable values
class Statement():
    pass
class Continue(Statement):
    pass
class Break(Statement):
    pass
class Success(Statement):
    pass


# Macros
def order_dict(d, keys):
    if isinstance(keys, list):
        for key in keys:
            yield d[key]
