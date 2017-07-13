
class InsulinValue:
    def __init__(self, start_date, value):
        self.start_date = start_date
        self.value = value

    def __repr__(self):
        return "InsulinValue(%s %s units)" % (self.start_date, self.value)

    def as_dict(self):
        return dict(
            start_date=self.start_date.isoformat(),
            value=self.value,
            )
