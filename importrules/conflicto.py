# encoding: utf-8

import gvsig

from collections import OrderedDict

from java.lang import String, Integer

from addons.AccidentRate.roadcatalog import findOwnership, checkRequirements

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer

class ConflictRule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    self.workspace = args.get("workspace",None)
    self.repo = self.workspace.getStoresRepository()
    
  def execute(self, report, feature):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return

    # 
    # CARRETERA
    # TIPO_VIA
    # KM
    # TITULARIDAD_VIA
    store = self.repo.getStore("ARENA2_ACCIDENTES")
    oldf = store.findFirst("LID_ACCIDENTE = '%s'" % feature.get("LID_ACCIDENTE"))
    store.dispose()
    if oldf == None:
      # Es un accidente nuevo, asi que no hay conflictos
      return
    conflictos = list()
    for fieldName in ("CARRETERA", "TIPO_VIA", "KM", "TITULARIDAD_VIA"):
      if oldf.get(fieldName) != oldf.get(fieldName+"_DGT"):
        # Hemos modificado el campo
        if feature.get(fieldName) != oldf.get(fieldName):
          # No coincide con el nuevo
          conflictos.append(fieldName)
    if len(conflictos)<1 :
      return
    report.add(
      feature.get("ID_ACCIDENTE"), 
      200,
      "Conflicto en %s." % str(conflictos),
      selected=False,
      CARRETERA=feature.get("CARRETERA"),
      PK=feature.get("KM"),
      TITULARIDAD=None,
      TITULARIDAD_ACCIDENTE=feature.get("TITULARIDAD_VIA"),
      TITULARIDAD_TRAMO=None,
      FECHA=feature.get("FECHA_ACCIDENTE"),
      PROVINCIA=feature.get("COD_PROVINCIA")
    )
    
class ConflictRuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,"[GVA] Conflicto en CARRETERA/TIPO_VIA/KM/TITULARIDAD_VIA")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo  es posible realizar las comprobaciones de CARRETERA/TIPO_VIA/KM/TITULARIDAD_VIA.\n"+s
    return None

  def create(self, **args):
    return ConflictRule(self, **args)

def selfRegister():
  manager = getArena2ImportManager()
  manager.addRuleFactory(ConflictRuleFactory())
  manager.addRuleErrorCode(200,"200 - Conflicto en CARRETERA/TIPO_VIA/KM/TITULARIDAD_VIA")
    
def main(*args):
  pass
