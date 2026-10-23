"""Exact ternary matrix norms and their compact display programs (offline)."""
from flint import fmpq_poly as Poly


def matrix_norm_coefficients(matrices):
    degree = matrices[0].nrows()
    values = [(matrices[0]+c*matrices[1]).charpoly() for c in range(degree+1)]
    result = {}
    for i in range(degree+1):
        differences, row = [], [f[i] for f in values]
        while row:
            differences.append(row[0])
            row = [row[j+1]-row[j] for j in range(len(row)-1)]
        polynomial, term = Poly([0]), Poly([1])
        for j in range(degree+1-i):
            polynomial += term*differences[j]
            term = term*Poly([-j, 1])/(j+1)
        for j, value in enumerate(polynomial):
            if value:
                result[i, degree-i-j, j] = value
    return result


class NormProgram:
    def __init__(self):
        self.nodes, self.cache = [], {}
        self.zero, self.one = self.rational(0), self.rational(1)

    def node(self, *instruction):
        if instruction not in self.cache:
            self.cache[instruction] = len(self.nodes)
            self.nodes.append(list(instruction))
        return self.cache[instruction]

    def rational(self, value):
        return self.node('rational', str(value))

    def multiply(self, a, b):
        if a == self.zero or b == self.zero:
            return self.zero
        return b if a == self.one else a if b == self.one else self.node('mul', a, b)

    def add(self, a, b):
        return b if a == self.zero else a if b == self.zero else self.node('add', a, b)

    def power(self, a, n):
        return self.one if n == 0 else a if n == 1 else self.node('pow', a, n)

    def evaluate(self, coefficients, S, B, C):
        degree = max(sum(exponents) for exponents in coefficients)
        scale = max(abs(value) for value in coefficients.values())
        result = self.zero
        for i in range(degree, -1, -1):
            row, n = self.zero, degree-i
            for j in range(n, -1, -1):
                k = n-j
                row = self.add(self.multiply(row, B), self.multiply(
                    self.rational(coefficients.get((i, j, k), 0)/scale), self.power(C, k)))
            result = self.add(self.multiply(result, S), row)
        return result
