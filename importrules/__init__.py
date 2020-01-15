# encoding: utf-8

import gvsig

from addons.AccidentRate.importrules import geocode
from addons.AccidentRate.importrules import titularidad
from addons.AccidentRate.importrules import conflicto


def selfRegister():
  geocode.selfRegister()
  titularidad.selfRegister()
  conflicto.selfRegister()
