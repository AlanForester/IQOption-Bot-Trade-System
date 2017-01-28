# -*- coding: utf-8 -*-


class FibonacciHelper(object):
    @staticmethod
    def get_uniq_unsigned_array(dimension):
        """Возвращяет массив фибоначи с уникальными значениями"""
        output = [0]

        unsigned = dimension
        fib1 = 0
        fib2 = 1
        while unsigned > 0:
            fib_sum = fib2 + fib1
            output.append(-fib_sum)
            fib1 = fib2
            fib2 = fib_sum
            unsigned -= 1
        output.reverse()

        signed = dimension
        fib1 = 0
        fib2 = 1
        while signed > 0:
            fib_sum = fib2 + fib1
            output.append(fib_sum)
            fib1 = fib2
            fib2 = fib_sum
            signed -= 1
        return output
