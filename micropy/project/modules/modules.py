# -*- coding: utf-8 -*-

import abc

"""Project Packages Module Abstract Implementation"""


class ProjectModule(metaclass=abc.ABCMeta):

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @abc.abstractproperty
    def config(self):
        pass

    @abc.abstractmethod
    def load(self):
        pass

    @abc.abstractmethod
    def create(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    def add(self, component):
        pass

    def remove(self, component):
        pass
