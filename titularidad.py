# encoding: utf-8

import gvsig

from addons.AccidentRate.roadcatalog import findOwnership

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleAction

class FixOwnershipRuleAction(RuleAction):
  def __init__(self, factory):
    RuleAction.__init__(self, factory, "Corregir titularidad")

  def check(self, report, row, accidentId):
    pass
    
  def fix(self,feature, args):
    titularidad = args
    feature["TITULARIDAD_VIA"] = titularidad

class OwnershipRule(Rule):
  def __init__(self, factory):
    Rule.__init__(self, factory)
    
  def execute(self, report, feature):
    titularidad = findOwnership(
      feature.get("FECHA_ACCIDENTE"), 
      feature.get("CARRETERA"), 
      feature.get("KM")
    )
    if titularidad == None:
      report.add(
        feature.get("ID_ACCIDENTE"), 
        self.getName(), 
        "Carretera '%s/%s/%s' no encontrada." % (
          feature.get("CARRETERA"), 
          feature.get("KM"),
          feature.get("FECHA_ACCIDENTE")
        )
      )
    titularidad = titularidad / 10
    if titularidad == 6:
      titularidad = 5
    if titularidad == feature.get("TITULARIDAD_VIA"):
      return
    row = report.add(
      feature.get("ID_ACCIDENTE"), 
      self.getName(), 
      "Titularidad incorrecta %s '%s/%s/%s'." % (
        titularidad,
        feature.get("CARRETERA"), 
        feature.get("KM"),
        feature.get("FECHA_ACCIDENTE")
      )
    )
    report.setFix(row, FixOwnershipRuleAction(self.getFactory()), titularidad)
    
class OwnershipRuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,"Titularidad")

  def create(self, *args):
    return OwnershipRule(self)

def selfRegister():
  manager = getArena2ImportManager()
  manager.addRuleFactory(OwnershipRuleFactory())
  
def main(*args):
  #test()
  selfRegister()
