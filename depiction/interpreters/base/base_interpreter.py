"""Core utilities for handling interpreters."""
from enum import Enum
from abc import ABC, abstractmethod

from ...core import Task, DataType
from ...models.base.base_model import BaseModel, TrainableModel


class TransparencyType(Enum):
    """Enum denoting black-box or white-box."""
    BLACK_BOX = 1
    WHITE_BOX = 2


class ExplanationType(Enum):
    """Enum denoting type of the explanation."""
    LOCAL = 1
    GLOBAL = 2


class BaseInterpreter(ABC):
    @abstractmethod
    def interpret(self, *argv, **kwarg):
        """
        Interface to interpret a model.
        """
        raise NotImplementedError


class AnteHocInterpreter(BaseInterpreter, TrainableModel):
    class UsageMode(Enum):
        """Enum indicating use modality since antehoc method could be used in a posthoc fashion."""
        ANTE_HOC = 1
        POST_HOC = 2

    def __init__(self, usage_mode, model = None, task_type = None, data_type = None):
        """Constructor. Checks consistency among arguments."""
        BaseInterpreter.__init__(self)

        self.usage_mode = usage_mode
        if self.usage_mode == self.UsageMode.ANTE_HOC:
            if task_type is None or data_type is None:
                raise ValueError("If using this model in ante-hoc mode, please provide task and data types!")
            TrainableModel.__init__(self, task_type, data_type)
        else:
            if model is None:
                raise ValueError("Please provide a model to post-hoc interpret!")
            else:
                if not isinstance(model, BaseModel):
                    raise TypeError("For safe use of this library, please wrap this model into a BaseModel!")

            self._to_interpret = model
            TrainableModel.__init__(self, model.task, model.data_type)

    def fit(self, *argv, **kwargs): 
        """Training routine. Implements the antehoc vs posthoc logic."""
        if self.usage_mode == self.UsageMode.ANTE_HOC:
            self._fit_antehoc(*argv, **kwargs)
        else:
            self._fit_posthoc(*argv, **kwargs)

    @abstractmethod
    def _fit_antehoc(self, *argv, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _fit_posthoc(self, *argv, **kwargs):
        raise NotImplementedError
