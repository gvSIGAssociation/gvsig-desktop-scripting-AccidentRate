# encoding: utf-8

import gvsig


from addons.AccidentRate import actions 
from addons.Arena2Importer import Arena2ImportLocator 

def main(*args):
  script.registerDataFolder("CEGESEV")
  Arena2ImportLocator.selfRegister()
  actions.selfRegister()
  
