class Company:
    def __init__(self, name: str, info: dict):
        self.name = name
        self.info = info

    def __eq__(self, other):
        return self.name == other.name and self.info == other.info

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, info: dict):
        if all(key in info for key in ["role", "link"]):
            self._info = [info]
        else:
            raise ValueError("Invalid info. Check Code")

    def add_info(self, info):
        if all(key in info for key in ["role", "link"]):
            self._info.append(info)
        else:
            raise ValueError("Invalid info. Check Code")
