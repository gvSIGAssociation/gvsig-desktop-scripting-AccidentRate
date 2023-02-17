# encoding: utf-8

import gvsig


from addons.AccidentRate import actions 
from addons.AccidentRate import accidentrateutils
from addons.Arena2Importer import Arena2ImportLocator 
from addons.AccidentRate import importrules
from addons.AccidentRate import postprocess


def main(*args):
  script.registerDataFolder("CEGESEV")
  Arena2ImportLocator.selfRegister()
  actions.selfRegister()
  importrules.selfRegister()
  accidentrateutils.addArena2Workspace()
  postprocess.selfRegister()
  
