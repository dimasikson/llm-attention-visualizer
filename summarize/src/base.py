import abc


class LLMRequestProcessor(object):
    def __init__(self, config):
        self.config = config

    @abc.abstractmethod
    def process(self, body):
        pass
