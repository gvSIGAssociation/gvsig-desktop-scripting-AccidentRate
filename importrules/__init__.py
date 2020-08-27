# encoding: utf-8

import gvsig

from addons.AccidentRate.importrules import geocode
from addons.AccidentRate.importrules import titularidad
from addons.AccidentRate.importrules import conflicto
from addons.AccidentRate.importrules import peatones
from addons.AccidentRate.importrules import conteoVehiculos
from addons.AccidentRate.importrules import valoresDisponibles

def selfRegister():
  geocode.selfRegister()
  titularidad.selfRegister()
  conflicto.selfRegister()
  peatones.selfRegister()
  conteoVehiculos.selfRegister()
  valoresDisponibles.selfRegister()