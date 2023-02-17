# encoding: utf-8
import gvsig

from addons.AccidentRate.postprocess import deletederegisteredaccidents

def selfRegister():
  deletederegisteredaccidents.selfRegister()
