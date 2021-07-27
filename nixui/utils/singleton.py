class Singleton:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return (
            type(other) == type(self) and
            self.name == other.name
        )

    def __repr__(self):
        return f'Singleton("{self.name}")'
