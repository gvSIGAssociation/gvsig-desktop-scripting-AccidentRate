# encoding: utf-8

import gvsig

from collections import OrderedDict

from java.lang import String, Integer
from java.util import Date

from addons.AccidentRate.roadcatalog import findOwnership, checkRequirements

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer
from org.gvsig.expressionevaluator import ExpressionUtils
from java.sql import Date
from java.text import SimpleDateFormat
from org.apache.commons.lang3 import StringUtils
CODERR_VALUES_FECHA_CIERRE = 571

class DateLockRule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    self.workspace = args.get("workspace",None)
    fechaDeCierreString = self.workspace.get('CEGESEV.accidentes.fecha_de_cierre')
    if fechaDeCierreString == None or StringUtils.isEmpty(fechaDeCierreString):
      self.fechaDeCierre = None
    else:
      self.fechaDeCierre = SimpleDateFormat("dd/MM/yyyy").parse(fechaDeCierreString)
    
  def execute(self, report, feature):
    if self.fechaDeCierre == None:
        return
    ftype = feature.getStore().getDefaultFeatureType()
    if ftype.get("FECHA_ACCIDENTE")==None:
        return
    fecha = feature.get("FECHA_ACCIDENTE")
    if fecha <= self.fechaDeCierre:
      report.add(
              feature.get("ID_ACCIDENTE"),
              CODERR_VALUES_FECHA_CIERRE,
              "Fecha de cierre fuera: %s, establecida: %s" % (
                str(fecha),
                str(self.fechaDeCierre)),
              fixerId = None, 
              selected=False
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
    u"%s - está fuera de la fecha de cierre" % CODERR_VALUES_FECHA_CIERRE
  )

  manager.addReportAttribute("DATE_LOCK_CONSTRAINT",Date, size=40, label="Valor anterior a la fecha de cierre", isEditable=True)
  


    
def main(*args):
  #test()
  selfRegister()
  pass

