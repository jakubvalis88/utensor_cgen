from abc import ABCMeta, abstractmethod


class Morphism(object):
  __metaclass__ = ABCMeta

  from_op_type = None
  to_op_type = None

  @abstractmethod
  def transform(self, from_op, to_op):
    raise RuntimeError('abstract transform invoked')

  @abstractmethod
  def inv_transform(self, to_op, from_op):
    raise RuntimeError('abstract inv_transform invoked')
