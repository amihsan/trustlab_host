import importlib
import importlib.util
import sys
from serializer import Interface
from abc import ABC, abstractmethod
from os import listdir
from os.path import isfile
from pathlib import Path


class UpdatableInterface(Interface):
    def serialize(self):
        for key in self.kwargs.keys():
            value = getattr(self, key)
            self.kwargs[key] = value if type(value) is not type else value.__name__
        return super().serialize()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Observation(UpdatableInterface):
    observation_id = int
    before = list
    sender = str
    receiver = str
    author = str
    topic = str
    message = str

    def __init__(self, observation_id, before, sender, receiver, author, topic, message):
        self.observation_id = observation_id
        self.before = before
        self.sender = sender
        self.receiver = receiver
        self.author = author
        self.topic = topic
        self.message = message
        super().__init__(observation_id=observation_id, before=before, sender=sender, receiver=receiver, author=author,
                         topic=topic, message=message)

    def __eq__(self, other):
        return self.observation_id == other.observation_id and self.before == other.before and \
               self.sender == other.sender and self.receiver == other.receiver and self.author == other.author \
               and self.topic == other.topic and self.message == other.message


class Scale(ABC):
    def __init__(self):
        if hasattr(self, 'maximum') and hasattr(self, 'minimum'):
            if type(self.maximum) is float and type(self.minimum) is float:
                self.number_type = float
            elif type(self.maximum) is int and type(self.minimum) is int:
                self.number_type = int
            else:
                raise TypeError("Scale is defined with mixed minimum and maximum variable types. "
                                "Requires to be int and int, or float and float.")
        else:
            raise AttributeError("Scale requires minimum and maximum variable.")


class Scenario(UpdatableInterface):
    name = str
    agents = list
    observations = list
    description = str
    history = dict
    scales_per_agent = dict
    metrics_per_agent = dict

    def agent_uses_metric(self, agent, metric_name):
        return metric_name in self.metrics_per_agent[agent].keys()

    def any_agents_use_metric(self, metric_name):
        return any(metric_name in metrics.keys() for agent, metrics in self.metrics_per_agent.items())

    def agents_with_metric(self, metric_name):
        agent_dict = {}
        if metric_name == 'content_trust.topic' or metric_name == 'content_trust.authority':
            agent_dict = {agent: metrics[metric_name] for agent, metrics in self.metrics_per_agent.items()
                          if metric_name in metrics.keys()}
        return agent_dict

    @staticmethod
    def check_consistency(name, agents, observations, scales_per_agent):
        if len(name) == 0:
            raise ValueError("Scenario names must be not empty.")
        if len(agents) <= 1:
            raise ValueError("Scenario agents must describe at least 2 agents.")
        if len(observations) == 0:
            raise ValueError("Scenario schedule must be not empty.")
        for observation in observations:
            if type(observation) != dict:
                raise ValueError("Each Observation requires to be dict.")
            Observation(**observation)  # check if observation is instantiable, else TypeError will be raised.
        # TODO: check for correct scales_per_agent setup
        for scale_dict in scales_per_agent.values():
            init_scale_object(scale_dict)
        # TODO: check for correct metrics_per_agent setup

    def __init__(self, name, agents, observations, history, scales_per_agent, metrics_per_agent,
                 description="No one described this scenario so far."):
        if history is None or len(history.keys()) == 0:
            # TODO history should be able to be None at default and then set to 0 for all agents
            #  -> maybe even not completely set and filled up with 0
            pass
        self.check_consistency(name, agents, observations, scales_per_agent)
        self.name = name
        self.agents = agents
        self.observations = observations
        self.history = history
        self.scales_per_agent = scales_per_agent
        self.metrics_per_agent = metrics_per_agent
        self.description = description
        super().__init__(name=name, agents=agents, observations=observations, history=history,
                         scales_per_agent=scales_per_agent, metrics_per_agent=metrics_per_agent,
                         description=description)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return '%s' % self.name

    def __eq__(self, other):
        return self.name == other.name and self.agents == other.agents and self.observations == other.observations and \
               self.description == other.description


def init_scale_object(scale_dict):
    scales_path = Path(Path(__file__).parent.absolute()) / "scales"
    module_name = vars(sys.modules[__name__])['__package__']
    scale_object = None
    scale_file_names = [file for file in listdir(scales_path) if isfile(scales_path / file)
                        and file.endswith("_scale.py")]
    for file_name in scale_file_names:
        file_package = file_name.split(".")[0]
        # python package path
        import_package = f".scales.{file_package}"
        # ensure package is accessible
        implementation_spec = importlib.util.find_spec(import_package, module_name)
        if file_package == scale_dict['package'] and implementation_spec is not None:
            # check if module was imported during runtime to decide if reload is required
            scale_spec = importlib.util.find_spec(import_package, module_name)
            # import scenario config to variable
            scale_module = importlib.import_module(import_package, module_name)
            # only reload module after importing if spec was found before
            if scale_spec is not None:
                scale_module = importlib.reload(scale_module)
            # class name requires to be file name in CamelCase
            class_name = ''.join([name_part.capitalize() for name_part in file_package.split("_")])
            if hasattr(scale_module, class_name):
                cls = getattr(scale_module, class_name)
                if issubclass(cls, Scale) and issubclass(cls, UpdatableInterface):
                    scale_kwargs = {key: value for key, value in scale_dict.items() if key != 'package'}
                    scale_object = cls(**scale_kwargs)
                else:
                    raise SyntaxError("Scale Implementation is not subclass of Scale and UpdatableInterface.")
    if scale_object is None:
        raise ModuleNotFoundError(f"Scale with package '{scale_dict['package']}' was not found.")
    return scale_object
