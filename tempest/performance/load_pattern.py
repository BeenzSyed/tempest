class LoadPattern(object):
    def __init__(self, initial_load):
        self.initial_load = initial_load

    def get_steps(self):
        pass


class StepLoad(LoadPattern):
    def __init__(self, initial_load, max_load, step_duration, step_count):
        self.max_load = max_load
        self.step_duration = step_duration
        self.step_count = step_count
        super(StepLoad, self).__init__(initial_load)

    def get_steps(self):
        steps = []
        seed = self.initial_load

        while seed <= self.max_load:
            steps.append({'load': seed, 'wait_time': self.step_duration})
            seed = seed + self.step_count
        return steps


class ConstantLoad(LoadPattern):
    def __init__(self, initial_load):
        super(ConstantLoad, self).__init__(initial_load)

    def get_steps(self):
        steps = [{'load': self.initial_load, 'wait_time': 0}]
        return steps

