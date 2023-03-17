class Printable:
    def __repr__(self) -> str:
        return str(self.__dict__)