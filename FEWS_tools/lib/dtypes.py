class isString:
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f'_{name}'

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        if not isinstance(value, str):
            if not (isinstance(value, tuple) and all(isinstance(v, str) for v in value)):
                raise TypeError(f'{self.public_name} takes string arguments only')

        setattr(obj, self.private_name, value)


class GroupSet:
    group_key = isString()
    sort_keys = isString()

    def __init__(self, group_key: str, *sort_keys: tuple[str]):
        self.group_key = group_key
        self.sort_keys = sort_keys or (group_key,)

    def __repr__(self):
        return (f'''{self.__class__.__name__}'''
                f'''({self.group_key}, {', '.join(self.sort_keys)})''')

    def __lt__(self, other):
        return self.__hash__() < other.__hash__()

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(tuple(i.lower() for i in self.sort_keys))

    @staticmethod
    def grouper(instance):
        return instance.group_key.lower()
