# encoding: utf-8

import gvsig

from collections import OrderedDict

from java.lang import String, Integer

from addons.AccidentRate.roadcatalog import findOwnership, checkRequirements

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer
from org.gvsig.expressionevaluator import ExpressionUtils

CODERR_VALUES_NO_DISPONIBLES = 470

class AvailableValuesRule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    
  def execute(self, report, feature):
    for attr in feature.getStore().getDefaultFeatureType():
      if attr.hasConstantAvailableValues():
        value = feature.get(attr)
        if not attr.isInAvailableValues(value):
          report.add(
                    feature.get("ID_ACCIDENTE"),
                    CODERR_VALUES_NO_DISPONIBLES,
                    "Valor no disponible en este attributo: %s ." % (
                      str(value)
                    ),
                    fixerId = None, 
                    selected=False,
                    FIELD_NO_AVAILABLE=attr.getName()
                  )
      
class AvailableValuesRuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,"[GVA] Valores disponibles")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo  es posible realizar las comprobaciones de valores disponibles.\n"+s
    return None

  def create(self, **args):
    return AvailableValuesRule(self, **args)

def selfRegister():
  manager = getArena2ImportManager()
  manager.addRuleFactory(AvailableValuesRuleFactory())
  #manager.addRuleFixer()
  manager.addRuleErrorCode(
    CODERR_VALUES_NO_DISPONIBLES,
    "%s - Valor no es un valor disponible del campo" % CODERR_VALUES_NO_DISPONIBLES
  )

  manager.addReportAttribute("FIELD_NO_AVAILABLE",String, size=120, label="Campo con valor no disponible", isEditable=True)

  


    
def main(*args):
  #test()
  #selfRegister()
  pass

