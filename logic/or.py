import logic


class Logic(logic.Logic):
    def __init__(self, data):
        super().__init__(data)

    def evaluate(self):
        for operand in self._operands:
            if operand.evaluate() is True:
                return True

        return False
