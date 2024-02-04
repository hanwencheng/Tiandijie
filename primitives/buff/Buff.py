from primitives.buff import BuffTemp


class Buff:
    def __init__(self, buff_temp: BuffTemp, duration: int, caster_id: str, level: int = 1, stack: int = 1, content: int = 0):
        # Copying attributes from BuffTemp
        self.__dict__.update(buff_temp.__dict__)
        # Setting duration
        self.duration: int = duration
        self.temp = BuffTemp
        self.caster_id = caster_id
        self.level = level
        self.stack = stack
        self.content = content


def cast_buff(buff_temp: BuffTemp, duration: int, caster_id: str, level: int = 1, stack: int = 1):
    return Buff(buff_temp, duration, caster_id, level, stack, 0)
