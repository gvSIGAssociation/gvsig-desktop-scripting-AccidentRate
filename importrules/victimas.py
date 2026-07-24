# encoding: utf-8

import gvsig

from collections import OrderedDict

from java.lang import String, Integer

from addons.AccidentRate.roadcatalog import findOwnership, checkRequirements

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer
from org.gvsig.expressionevaluator import ExpressionUtils
from org.gvsig.tools.dispose import DisposeUtils
CODERR_VICTIMAS_NO_COINCIDEN = 300

class TotalVictimsRuleFixer(RuleFixer):
  def __init__(self, **args):
    RuleFixer.__init__(self, "TotalVictimsRuleFixer", "Corregir Víctimas", True)

  def fix(self,feature, issue):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    victimas = issue.get("TOTAL_VICTIMAS")
    feature["TOTAL_VICTIMAS"] = victimas

class TotalVictimsRule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    
  def execute(self, report, feature):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    suma = feature.getInt("TOTAL_MUERTOS")+feature.getInt("TOTAL_GRAVES")+feature.getInt("TOTAL_LEVES")
    totalVictimas = feature.getInt("TOTAL_VICTIMAS")
    if suma != totalVictimas:
      report.add(
        feature.get("ID_ACCIDENTE"),
        CODERR_VICTIMAS_NO_COINCIDEN,
        u"Víctimas no coinciden, entidad: %s , suma: %s'." % (
          str(totalVictimas),
          str(suma)
        ),
        fixerId = "TotalVictimsRuleFixer", 
        selected=True,
        TOTAL_VICTIMAS=suma
      )

class TotalVictimsRuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,u"[GVA] Víctimas")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+u".\nNo  es posible realizar las comprobaciones de víctimas.\n"+s
    return None

  def create(self, **args):
    return TotalVictimsRule(self, **args)

def selfRegister():
  manager = getArena2ImportManager()
  manager.addRuleFactory(TotalVictimsRuleFactory())
  manager.addRuleFixer(TotalVictimsRuleFixer())
  manager.addRuleErrorCode(
    CODERR_VICTIMAS_NO_COINCIDEN,
    "%s - Victimas no coinciden" % CODERR_VICTIMAS_NO_COINCIDEN
  )

  manager.addReportAttribute("TOTAL_VICTIMAS",Integer, size=10, label=u"Total Víctimas", isEditable=True, group=u"Víctimas")

  


    
def main(*args):
  #test()
  #selfRegister()
  manager = getArena2ImportManager()
  print dir(manager)
  print manager.getFixer("TotalVictimsRuleFixer")
  pass
