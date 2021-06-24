# encoding: utf-8

import gvsig

from addons.AccidentRate.importrules import geocode 
from addons.AccidentRate.importrules.codigoINE import transformCodigoINE

def main(*args):
    transformCodigoINE.updateWorkspace()
    geocode.updateWorkspace()
    
    pass
