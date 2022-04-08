# encoding: utf-8

import gvsig

from collections import OrderedDict

from java.lang import String, Integer

from addons.AccidentRate.roadcatalog import findOwnership, checkRequirements

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer
import pdb

CODERR_CARRETERAKM_NO_ENCONTRADA = 100
CODERR_KM_NO_ENCONTRADO = 101
CODERR_TITULARIDADCARRETERAKM_NO_ENCONTRADA = 102
CODERR_TITULARIDAD_INCORRECTA = 103
CODERR_TITULARIDAD_AUTONOMICA_SIN_CARETERA = 104
CODERR_CARRETERA_NO_INDICADA = 105

TITULARIDAD_DESCONOCIDA = 0
TITULARIDAD_ESTATAL = 1
TITULARIDAD_AUTONOMICA = 2
TITULARIDAD_PROVINCIAL = 3
TITULARIDAD_MUNICIPAL = 4
TITULARIDAD_OTRA = 5

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
      0: TITULARIDAD_DESCONOCIDA,
      10: TITULARIDAD_ESTATAL,
      20: TITULARIDAD_AUTONOMICA,
      30: TITULARIDAD_PROVINCIAL, # En la GVA han separado esta en dos
      40: TITULARIDAD_PROVINCIAL,
      50: TITULARIDAD_MUNICIPAL,
      60: TITULARIDAD_OTRA,
      99: TITULARIDAD_DESCONOCIDA
    }
    self.__titularidadCod2Name = {
      TITULARIDAD_DESCONOCIDA: "Desconocida [%s]" % TITULARIDAD_DESCONOCIDA,
      TITULARIDAD_ESTATAL    : "Estatal [%s]" % TITULARIDAD_ESTATAL,
      TITULARIDAD_AUTONOMICA : "Autonomica [%s]" % TITULARIDAD_AUTONOMICA,
      TITULARIDAD_PROVINCIAL : "Provincial, Cabildo/Consell [%s]" % TITULARIDAD_PROVINCIAL,
      TITULARIDAD_MUNICIPAL  : "Municipal [%s]" % TITULARIDAD_MUNICIPAL,
      TITULARIDAD_OTRA       : "Otra [%s]" % TITULARIDAD_OTRA
    }
    
  def execute(self, report, feature):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    #pdb.set_trace()
    #if feature.getType().get("TITULARIDAD_VIA_DGT"):
    # print "tiene dgt:", feature.get("TITULARIDAD_VIA_DGT")
    #else:
    #  print "no tiene dgt"
    #return
    titularidad_accidente = feature.get("TITULARIDAD_VIA")
    #print "Feature:",feature.get("ID_ACCIDENTE"), feature.get("CARRETERA"), feature.get("TITULARIDAD_VIA"),feature.get("TITULARIDAD_VIA_DGT"), feature.get("KM")
    if feature.get("CARRETERA") == None:
      if titularidad_accidente==TITULARIDAD_AUTONOMICA: 
        # No se ha indicado carretera y titularidad en el acidente a Autonomica
        report.add(
          feature.get("ID_ACCIDENTE"), 
          CODERR_TITULARIDAD_AUTONOMICA_SIN_CARETERA,
          "Carretera no especificada con titularidad autonimica (%s) '%s/%s/%s'." % (
            self.__titularidadCod2Name.get(titularidad_accidente,0),
            feature.get("CARRETERA"), 
            feature.get("KM"),
            feature.get("FECHA_ACCIDENTE")
          ),
          fixerId = "SetOwnership", 
          selected=True,
          PK=feature.get("KM"),
          TITULARIDAD=TITULARIDAD_DESCONOCIDA,
          TITULARIDAD_ACCIDENTE=titularidad_accidente,
          TITULARIDAD_TRAMO=TITULARIDAD_DESCONOCIDA,
          FECHA=feature.get("FECHA_ACCIDENTE"),
          PROVINCIA=feature.get("COD_PROVINCIA")
        )
      return
    titularidad_tramo = findOwnership(
      feature.get("FECHA_ACCIDENTE"), 
      feature.get("CARRETERA"), 
      feature.get("KM")
    )
    if titularidad_tramo == None:
      if titularidad_accidente==TITULARIDAD_AUTONOMICA:
        # Tramo no encontrado y titularidad en el acidente a Autonomica
        report.add(
          feature.get("ID_ACCIDENTE"), 
          CODERR_TITULARIDADCARRETERAKM_NO_ENCONTRADA,
          "Carretera+km no encontrada (%s) '%s/%s/%s'." % (
            self.__titularidadCod2Name.get(titularidad_accidente,TITULARIDAD_DESCONOCIDA),
            feature.get("CARRETERA"), 
            feature.get("KM"),
            feature.get("FECHA_ACCIDENTE")
          ),
          fixerId = "SetOwnership", 
          selected=True,
          CARRETERA=feature.get("CARRETERA"),
          PK=feature.get("KM"),
          TITULARIDAD=TITULARIDAD_DESCONOCIDA,
          TITULARIDAD_ACCIDENTE=titularidad_accidente,
          TITULARIDAD_TRAMO=titularidad_tramo,
          FECHA=feature.get("FECHA_ACCIDENTE"),
          PROVINCIA=feature.get("COD_PROVINCIA")
        )
      return 
    # Convertimos la titularidad obtenida de la BBDD 
    # de la GVA a la de la DGT
    if titularidad_tramo not in [1,2,3,4,5]:
      titularidad_tramo = self.__titularidadGVA2DGT.get(titularidad_tramo,TITULARIDAD_DESCONOCIDA)
    else:
      print "notin: no se tiene que transformar ya es correcta", titularidad_tramo

    if titularidad_tramo == titularidad_accidente:
      return
    row = report.add(
      feature.get("ID_ACCIDENTE"), 
      CODERR_TITULARIDAD_INCORRECTA,
      "Titularidad incorrecta (accidente %r, tramo %r) '%s/%s/%s'." % (
        self.__titularidadCod2Name.get(titularidad_accidente,TITULARIDAD_DESCONOCIDA),
        self.__titularidadCod2Name.get(titularidad_tramo,TITULARIDAD_DESCONOCIDA),
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

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo  es posible realizar las comprobaciones de titularidad.\n"+s
    return None

  def create(self, **args):
    return OwnershipRule(self, **args)

def selfRegister():
  valoresTitularidad = OrderedDict()
  valoresTitularidad[TITULARIDAD_DESCONOCIDA] = "%s - Desconocida" % TITULARIDAD_DESCONOCIDA
  valoresTitularidad[TITULARIDAD_ESTATAL    ] = "%s - Estatal" % TITULARIDAD_ESTATAL
  valoresTitularidad[TITULARIDAD_AUTONOMICA ] = "%s - Autonomica" % TITULARIDAD_AUTONOMICA
  valoresTitularidad[TITULARIDAD_PROVINCIAL ] = "%s - Provincial, Cabildo/Consell" % TITULARIDAD_PROVINCIAL
  valoresTitularidad[TITULARIDAD_MUNICIPAL  ] = "%s - Municipal" % TITULARIDAD_MUNICIPAL
  valoresTitularidad[TITULARIDAD_OTRA       ] = "%s - Otra" % TITULARIDAD_OTRA

  manager = getArena2ImportManager()
  manager.addRuleFactory(OwnershipRuleFactory())
  manager.addRuleFixer(SetOwnershipRuleFixer())
  manager.addRuleErrorCode(
    CODERR_CARRETERAKM_NO_ENCONTRADA,
    "%s - Carretera/km no encontrada" % CODERR_CARRETERAKM_NO_ENCONTRADA
  )
  manager.addRuleErrorCode(
    CODERR_KM_NO_ENCONTRADO,
    "%s - km no encontrado" % CODERR_KM_NO_ENCONTRADO
  )
  manager.addRuleErrorCode(
    CODERR_CARRETERA_NO_INDICADA,
    "%s - Carretera no indicada" % CODERR_CARRETERA_NO_INDICADA
  )
  manager.addRuleErrorCode(
    CODERR_TITULARIDADCARRETERAKM_NO_ENCONTRADA,
    "%s - Titularidad autonomica y carretera/km no encontrada" % CODERR_TITULARIDADCARRETERAKM_NO_ENCONTRADA
  )
  manager.addRuleErrorCode(
    CODERR_TITULARIDAD_INCORRECTA,
    "%s - Titularidad incorrecta" % CODERR_TITULARIDAD_INCORRECTA
  )
  manager.addRuleErrorCode(
    CODERR_TITULARIDAD_AUTONOMICA_SIN_CARETERA,
    "%s - Titularidad autonomica sin especificar carretera" % CODERR_TITULARIDAD_AUTONOMICA_SIN_CARETERA
  )

  manager.addReportAttribute("CARRETERA",String, size=45, label="Carretera")
  manager.addReportAttribute("PK",Integer, label="PK")
  manager.addReportAttribute("TITULARIDAD",Integer, size=10, label="Titularidad", isEditable=True, availableValues=valoresTitularidad)
  manager.addReportAttribute("TITULARIDAD_ACCIDENTE",Integer, size=10, label="Titularidad acc.", availableValues=valoresTitularidad)
  manager.addReportAttribute("TITULARIDAD_TRAMO",Integer, size=10, label="Titularidad tramo", availableValues=valoresTitularidad)
  manager.addReportAttribute("FECHA",String, size=45, label="Fecha")
  manager.addReportAttribute("PROVINCIA",String, size=45, label="Provincia")
  


    
def main(*args):
  #test()
  selfRegister()
  pass
