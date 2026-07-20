# encoding: utf-8

import gvsig

#from addons.AccidentRate.importrules import geocode
from addons.AccidentRate.importrules import titularidad
from addons.AccidentRate.importrules import conflicto
from addons.AccidentRate.importrules import peatones
from addons.AccidentRate.importrules import conteoVehiculos
from addons.AccidentRate.importrules import valoresDisponibles
from addons.AccidentRate.importrules import fechaCierre
from addons.AccidentRate.importrules import geocode
from addons.AccidentRate.importrules.codigoINE import codigoINE
from addons.AccidentRate.importrules import asignarMedidasAforos
from addons.AccidentRate.importrules import asignarTipoDiaCit
from addons.AccidentRate.importrules import asignarEdad
from addons.AccidentRate.importrules import victimas

def selfRegister():
  geocode.selfRegister()
  titularidad.selfRegister()
  conflicto.selfRegister()
  peatones.selfRegister()
  conteoVehiculos.selfRegister()
  valoresDisponibles.selfRegister()
  fechaCierre.selfRegister()
  codigoINE.selfRegister()
  asignarMedidasAforos.selfRegister()
  asignarTipoDiaCit.selfRegister()
  asignarEdad.selfRegister()
  victimas.selfRegister()

def main(*args):
  selfRegister()