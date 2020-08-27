# encoding: utf-8

import gvsig

from collections import OrderedDict

from java.lang import String, Integer

from addons.AccidentRate.roadcatalog import findOwnership, checkRequirements

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer
from org.gvsig.expressionevaluator import ExpressionUtils

CODERR_VEHICULOS_NO_COINCIDEN = 450

class UpdateCountVehicles(RuleFixer):
  def __init__(self, **args):
    RuleFixer.__init__(self, "UpdateCountVehicles", "Corregir vehiculos", True)

  def fix(self,feature, issue):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    peatones = issue.get("TOTAL_PEATONES")
    feature["TOTAL_PEATONES"] = peatones

class CountVehiclesRule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    
  def execute(self, report, feature):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    titularidad_accidente = feature.get("TITULARIDAD_VIA")
    storePeatones = feature.getStore().getStoresRepository().getStore("ARENA2_PEATONES")
    accidente = feature.get("ID_ACCIDENTE")

    if accidente !=None:
      builder = ExpressionUtils.createExpressionBuilder()
      expression = builder.eq(builder.variable("ID_ACCIDENTE"), builder.constant(accidente)).toString()
      fset = storePeatones.getFeatureSet(expression)
      totalPeatones = fset.size()
      peatonesFromFeature = feature.get("TOTAL_PEATONES")
      if totalPeatones!=peatonesFromFeature:
        report.add(
                  feature.get("ID_ACCIDENTE"),
                  CODERR_VEHICULOS_NO_COINCIDEN,
                  "Peatones no coinciden, entidad: %s , tablas peatones: %s'." % (
                    str(peatonesFromFeature), 
                    str(totalPeatones)
                  ),
                  fixerId = "AssignPeatonesFromTableFixer", 
                  selected=False,
                  TOTAL_PEATONES=totalPeatones
                )
    
class CountVehiclesRuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,"[GVA] Numero de vehiculos")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo  es posible realizar las comprobaciones de numero de vehiculos.\n"+s
    return None

  def create(self, **args):
    return CountVehiclesRule(self, **args)

def selfRegister():
  manager = getArena2ImportManager()
  manager.addRuleFactory(CountVehiclesRuleFactory())
  manager.addRuleFixer(UpdateCountVehicles())
  manager.addRuleErrorCode(
    CODERR_VEHICULOS_NO_COINCIDEN,
    "%s - Numero vehiculos no coinciden" % CODERR_VEHICULOS_NO_COINCIDEN
  )

  manager.addReportAttribute("TOTAL_PEATONES",Integer, size=10, label="Total Peatones", isEditable=True)

  


    
def main(*args):
  #test()
  #selfRegister()
  pass
