import importlib


class Base(object):
    def __init__(self, data):
        pass

    def evaluate(self):
        raise Exception("Cannot evaluate on base class")


class Logic(Base):
    def __init__(self, data):
        super().__init__(data)

        self._operands = []

        for item in data:
            self._operands.append(logic(item))


def factory(op, data):
    try:
        import_obj = importlib.import_module("logic.{0}".format(op))
        logic_class = getattr(import_obj, "Logic", None)
        if logic_class is not None:
            return logic_class(data)
    except Exception as e:
        raise Exception("[ERROR] Logic class {0} not found: {1}".format(op, e))

    return None


def logic(json_obj):
    if len(json_obj) != 1:
        raise Exception("[ERROR] Json object does not have only one key: '{0}'".format(json_obj))

    op = list(json_obj.keys())[0]
    data = json_obj[op]

    return factory(op, data)
