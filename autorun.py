# encoding: utf-8

import gvsig


from addons.AccidentRate import actions 
from addons.AccidentRate import geocode
from addons.AccidentRate import accidentrateutils
from addons.Arena2Importer import Arena2ImportLocator 

def main(*args):
  script.registerDataFolder("CEGESEV")
  Arena2ImportLocator.selfRegister()
  actions.selfRegister()
  geocode.selfRegister()
  accidentrateutils.addArena2Workspace()
  
