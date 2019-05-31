import logic


class Logic(logic.Base):
    def __init__(self, data):
        super().__init__(data)

        self._val = data["val"]
        self._rop = data["rop"]

    def evaluate(self):
        return self._val > self._rop
