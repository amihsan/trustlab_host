from ..models import Scale, UpdatableInterface


class MarshBriggsScale(Scale, UpdatableInterface):
    name = str
    maximum = float
    minimum = float
    default = float
    cooperation = float
    forgivability = float

    def minimum_to_trust_others(self):
        return self.minimum

    def default_value(self):
        return self.default

    def __init__(self, minimum, maximum, default=0.0, cooperation=0.5, forgivability=-0.5,
                 name="Trust Scale by Marsh and Briggs (2009)"):
        self.name = name
        self.maximum = maximum
        self.minimum = minimum
        self.default = default
        self.cooperation = cooperation
        self.forgivability = forgivability
        Scale.__init__(self)
        UpdatableInterface.__init__(self, maximum=maximum, minimum=minimum, default=default, name=name,
                                    forgivability=forgivability, cooperation=cooperation)
