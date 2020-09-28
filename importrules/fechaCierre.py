# encoding: utf-8

import gvsig

from collections import OrderedDict

from java.lang import String, Integer
from java.util import Date

from addons.AccidentRate.roadcatalog import findOwnership, checkRequirements

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer
from org.gvsig.expressionevaluator import ExpressionUtils

CODERR_VALUES_FECHA_CIERRE = 571

class DateLockRule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    
  def execute(self, report, feature):
    ftype = feature.getStore().getDefaultFeatureType()
    for attr in ftype:
      if attr.hasAvailableValues()==True:
        value = feature.get(attr.getName())
        if value==None: 
            continue
        if not attr.isInAvailableValues(value):
            report.add(
                      feature.get("ID_ACCIDENTE"),
                      CODERR_VALUES_FECHA_CIERRE,
                      "Valor no disponible en este fecha: %s  del campo: %s " % (
                        str(value),
                        str(attr.getName())
                      ),
                      fixerId = None, 
                      selected=False,
                      FIELD_NO_AVAILABLE=attr.getName()
                    )

class DateLockRuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,"[GVA] Fecha cierre")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo  es posible realizar las comprobaciones de fecha cierre.\n"+s
    return None

  def create(self, **args):
    return DateLockRule(self, **args)

def selfRegister():
  manager = getArena2ImportManager()
  manager.addRuleFactory(DateLockRuleFactory())
  #manager.addRuleFixer()
  manager.addRuleErrorCode(
    CODERR_VALUES_FECHA_CIERRE,
    "%s - está fuera de la fecha de cierre" % CODERR_VALUES_NO_DISPONIBLES
  )

  manager.addReportAttribute("DATE_LOCK_CONSTRAINT",Date, size=40, label="Valor anterior a la fecha de cierre", isEditable=True)
  


    
def main(*args):
  #test()
  #selfRegister()
  pass

