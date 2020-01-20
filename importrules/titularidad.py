# encoding: utf-8

import gvsig

from collections import OrderedDict

from java.lang import String, Integer

from addons.AccidentRate.roadcatalog import findOwnership

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer

class SetOwnershipRuleFixer(RuleFixer):
  def __init__(self, **args):
    RuleFixer.__init__(self, "SetOwnership", "Asignar titularidad", True)

  def fix(self,feature, issue):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    titularidad = issue.get("TITULARIDAD")
    feature["TITULARIDAD_VIA"] = titularidad

class OwnershipRule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    self.__titularidadGVA2DGT = {
      0: 0,
      1: 1,
      2: 2,
      3: 3, # En la GVA han separado esta en dos
      4: 3,
      5: 4,
      6: 5
    }
    self.__titularidadCod2Name = {
      0: "Desconocida [0]",
      1: "Estatal [1]",
      2: "Autonomica [2]",
      3: "Provincial, Cabildo/Consell [3]",
      4: "Municipal [4]",
      5: "Otra [5]"
      
    }
    
  def execute(self, report, feature):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    if feature.get("CARRETERA") == None:
      return
    titularidad_accidente = feature.get("TITULARIDAD_VIA")
    titularidad_tramo = findOwnership(
      feature.get("FECHA_ACCIDENTE"), 
      feature.get("CARRETERA"), 
      feature.get("KM")
    )
    if titularidad_tramo == None:
      if titularidad_accidente==2: 
        # Tramo no encontrado y titularidad en el acidente a Autonomica
        report.add(
          feature.get("ID_ACCIDENTE"), 
          101,
          "Carretera no encontrada (%s) '%s/%s/%s'." % (
            self.__titularidadCod2Name.get(titularidad_accidente,0),
            feature.get("CARRETERA"), 
            feature.get("KM"),
            feature.get("FECHA_ACCIDENTE")
          ),
          fixerId = "SetOwnership", 
          selected=False,
          CARRETERA=feature.get("CARRETERA"),
          PK=feature.get("KM"),
          TITULARIDAD=titularidad_accidente,
          TITULARIDAD_ACCIDENTE=titularidad_accidente,
          TITULARIDAD_TRAMO=titularidad_tramo,
          FECHA=feature.get("FECHA_ACCIDENTE"),
          PROVINCIA=feature.get("COD_PROVINCIA")
        )
      else:
        pass
        #report.add(
        #  feature.get("ID_ACCIDENTE"), 
        #  100,
        #  "Carretera no encontrada (%s) '%s/%s/%s'." % (
        #    self.__titularidadCod2Name.get(titularidad_accidente,0),
        #    feature.get("CARRETERA"), 
        #    feature.get("KM"),
        #    feature.get("FECHA_ACCIDENTE")
        #  ),
        #  fixerId = "SetOwnership", 
        #  selected=False,
        #  CARRETERA=feature.get("CARRETERA"),
        #  PK=feature.get("KM"),
        #  TITULARIDAD_DGT=titularidad_accidente,
        #  TITULARIDAD=titularidad_tramo,
        #  FECHA=feature.get("FECHA_ACCIDENTE"),
        #  PROVINCIA=feature.get("COD_PROVINCIA")
        #)
      return 
    # Convertimos la titularidad obtenida de la BBDD 
    # de la GVA a la de la DGT
    titularidad_tramo = self.__titularidadGVA2DGT.get(titularidad_tramo,5)

    if titularidad_tramo == titularidad_accidente:
      return
    row = report.add(
      feature.get("ID_ACCIDENTE"), 
      102,
      "Titularidad incorrecta (accidente %r, tramo %r) '%s/%s/%s'." % (
        self.__titularidadCod2Name.get(titularidad_accidente,0),
        self.__titularidadCod2Name.get(titularidad_tramo,0),
        feature.get("CARRETERA"), 
        feature.get("KM"),
        feature.get("FECHA_ACCIDENTE")
      ),
      fixerId = "SetOwnership", 
      selected=True,
      CARRETERA=feature.get("CARRETERA"),
      PK=feature.get("KM"),
      TITULARIDAD=titularidad_tramo,
      TITULARIDAD_ACCIDENTE=titularidad_accidente,
      TITULARIDAD_TRAMO=titularidad_tramo,
      FECHA=feature.get("FECHA_ACCIDENTE"),
      PROVINCIA=feature.get("COD_PROVINCIA")
    )
    
class OwnershipRuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,"[GVA] Titularidad")

  def create(self, **args):
    return OwnershipRule(self, **args)

def selfRegister():
  valoresTitularidad = OrderedDict()
  valoresTitularidad[0] = "0 - Desconocida"
  valoresTitularidad[1] = "1 - Estatal"
  valoresTitularidad[2] = "2 - Autonomica"
  valoresTitularidad[3] = "3 - Provincial, Cabildo/Consell"
  valoresTitularidad[4] = "4 - Municipal"
  valoresTitularidad[5] = "5 - Otra"

  manager = getArena2ImportManager()
  manager.addRuleFactory(OwnershipRuleFactory())
  manager.addRuleFixer(SetOwnershipRuleFixer())
  manager.addRuleErrorCode(100,"100 - Carretera/km no encontrada")
  manager.addRuleErrorCode(101,"101 - Titularidad autonomica y carretera/km no encontrada")
  manager.addRuleErrorCode(102,"102 - Titularidad incorrecta")
  manager.addReportAttribute("CARRETERA",String, size=45, label="Carretera")
  manager.addReportAttribute("PK",Integer, label="PK")
  manager.addReportAttribute("TITULARIDAD",Integer, size=10, label="Titularidad", isEditable=True, availableValues=valoresTitularidad)
  manager.addReportAttribute("TITULARIDAD_ACCIDENTE",Integer, size=10, label="Titularidad acc.", availableValues=valoresTitularidad)
  manager.addReportAttribute("TITULARIDAD_TRAMO",Integer, size=10, label="Titularidad tramo", availableValues=valoresTitularidad)
  manager.addReportAttribute("FECHA",String, size=45, label="Fecha")
  manager.addReportAttribute("PROVINCIA",String, size=45, label="Provincia")
  
    
def main(*args):
  #test()
  #selfRegister()
  pass
