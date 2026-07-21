# encoding: utf-8

import gvsig

from collections import OrderedDict

from java.lang import String, Integer, Boolean

from addons.AccidentRate.roadcatalog import findOwnership, checkRequirements

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer

CODERR_TIPO_ANIMAL_NO_COINCIDE = 350

class TipoAnimalRuleFixer(RuleFixer):
  def __init__(self, **args):
    RuleFixer.__init__(self, "TipoAnimalRuleFixer", "Corregir tipo animal", True)

  def fix(self,feature, issue):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    tipoAccAnimalSugerido = issue.get("TIPO_ACC_ANIMAL")
    irrupcionAnimalSugerido = issue.get("FC_IRRUPCION_ANIMAL")
    if tipoAccAnimalSugerido != None:
      feature["TIPO_ACC_ANIMAL"] = tipoAccAnimalSugerido
    if irrupcionAnimalSugerido != None:
      feature["FC_IRRUPCION_ANIMAL"] = irrupcionAnimalSugerido

class TipoAnimalRule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    self.workspace = args.get("workspace",None)
    self.repo = self.workspace.getStoresRepository()
    
  def execute(self, report, feature):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return

    tipoAccColision = feature.get('TIPO_ACC_COLISION')
    tipoAccAnimal = feature.get('TIPO_ACC_ANIMAL')
    irrupcionAnimal = feature.get('FC_IRRUPCION_ANIMAL')

    mensaje = None
    selected = False
    tipoAccAnimalSugerido = None
    irrupcionAnimalSugerido = None
    if tipoAccColision == 8:
      if tipoAccAnimal == None:
        if irrupcionAnimal == None:
          mensaje = u""
        elif irrupcionAnimal:
          mensaje = u"Sugerencia: Tipo 'no identificado'"
          tipoAccAnimalSugerido = 0
          selected = True
        else:
          mensaje = u""
      else:
        if irrupcionAnimal == None:
          mensaje = u"Sugerencia: Con irrupción animal"
          irrupcionAnimalSugerido = True
          selected = True
        elif irrupcionAnimal == False:
          mensaje = u"Sugerencia: Con irrupción animal"
          irrupcionAnimalSugerido = True
          selected = True
    else:
      if tipoAccAnimal == None and irrupcionAnimal == True:
        mensaje = u""
      
    if mensaje != None:
      report.add(
        feature.get("ID_ACCIDENTE"), 
        CODERR_TIPO_ANIMAL_NO_COINCIDE,
        "Conflicto en tipo animal %s." % mensaje,
        selected=selected,
        TIPO_ACC_ANIMAL=tipoAccAnimalSugerido,
        FC_IRRUPCION_ANIMAL=irrupcionAnimalSugerido
      )
      
class TipoAnimalRuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,"[GVA] Conflicto en el tipo de animal")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo es posible realizar las comprobaciones de conflicto en el tipo de animal.\n"+s
    return None

  def create(self, **args):
    return TipoAnimalRule(self, **args)

def selfRegister():
  manager = getArena2ImportManager()
  manager.addRuleFactory(TipoAnimalRuleFactory())
  manager.addRuleFixer(TipoAnimalRuleFixer())
  manager.addRuleErrorCode(CODERR_TIPO_ANIMAL_NO_COINCIDE,str(CODERR_TIPO_ANIMAL_NO_COINCIDE)+" - Conflicto en el tipo de animal")
  manager.addReportAttribute("TIPO_ACC_ANIMAL",Integer, size=10, label=u"Tipo animal", isEditable=True)
  manager.addReportAttribute("FC_IRRUPCION_ANIMAL",Boolean, size=6, label=u"Irrupción animal", iósEditable=True)
    
def main(*args):
  pass
