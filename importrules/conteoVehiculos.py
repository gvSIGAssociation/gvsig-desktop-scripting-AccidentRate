# encoding: utf-8

import gvsig

from collections import OrderedDict

from java.lang import String, Integer

from addons.AccidentRate.roadcatalog import findOwnership, checkRequirements

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer
from org.gvsig.expressionevaluator import ExpressionUtils
from java.lang import StringBuilder
from org.gvsig.tools.dispose import DisposeUtils

CODERR_VEHICULOS_NO_COINCIDEN = 450

class UpdateCountVehicles(RuleFixer):
  def __init__(self, **args):
    RuleFixer.__init__(self, "UpdateCountVehicles", "Corregir vehiculos", True)
    self.agrupacion = {'NUM_TURISMOS' : [1,3],
         'NUM_FURGONETAS' : [2],
         'NUM_CAMIONES' : [19,20,21],
         'NUM_AUTOBUSES' : [15,16,17],
         'NUM_CICLOMOTORES' : [5],
         'NUM_MOTOCICLETAS' : [6,7],
         'NUM_BICICLETAS' : [4,30],
         'NUM_OTROS_VEHI' : [8,9,10,11,12,13,14,18,22,23,24,25,26,27,29]
         }

  def fix(self,feature, issue):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    for key in self.agrupacion.keys():
      valueToChange = issue.get(key)
      if feature.get(key)!=issue.get(key):
        feature.set(key, valueToChange)

class CountVehiclesRule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    self.agrupacion = {'NUM_TURISMOS' : [1,3],
         'NUM_FURGONETAS' : [2],
         'NUM_CAMIONES' : [19,20,21],
         'NUM_AUTOBUSES' : [15,16,17],
         'NUM_CICLOMOTORES' : [5],
         'NUM_MOTOCICLETAS' : [6,7],
         'NUM_BICICLETAS' : [4,30],
         'NUM_OTROS_VEHI' : [8,9,10,11,12,13,14,18,22,23,24,25,26,27,29]
         }
  def getKeyFromTypeVehicle(self, value):
    if value==None:
        return None
    for key in self.agrupacion.keys():
      toAssign = value in self.agrupacion[key]
      if toAssign:
        return key
      
  def execute(self, report, feature):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    titularidad_accidente = feature.get("TITULARIDAD_VIA")
    storeVehiculos= feature.getStore().getStoresRepository().getStore("ARENA2_VEHICULOS")
    accidente = feature.get("ID_ACCIDENTE")

    if accidente !=None:
      ## Rellenar por campos de la feature
      # Mantiene el none
      # no es lo mismo que llegue un None 
      # a que se confirme porque no tiene valores en la tabla
      # de vehiculos con que es 0
      conteoPorFeature = { 'NUM_TURISMOS': None,
        'NUM_FURGONETAS': None,
        'NUM_CAMIONES': None,
        'NUM_AUTOBUSES': None,
        'NUM_CICLOMOTORES': None,
        'NUM_MOTOCICLETAS': None,
        'NUM_BICICLETAS': None,
        'NUM_OTROS_VEHI': None
      }
      for key in conteoPorFeature.keys():
        value = feature.get(key)
        conteoPorFeature[key] = value

      ## Conteo por la tabla asociada de vehiculos
      builder = ExpressionUtils.createExpressionBuilder()
      expression = builder.eq(builder.variable("ID_ACCIDENTE"), builder.constant(accidente)).toString()
      #fset = storeVehiculos.getFeatureSet(expression)
      conteoPorTablas = { 'NUM_TURISMOS': 0,
        'NUM_FURGONETAS': 0,
        'NUM_CAMIONES': 0,
        'NUM_AUTOBUSES': 0,
        'NUM_CICLOMOTORES': 0,
        'NUM_MOTOCICLETAS': 0,
        'NUM_BICICLETAS': 0,
        'NUM_OTROS_VEHI': 0
        }
      fset = storeVehiculos.getFeatureSet(expression).iterable()
      for f in fset:
        tipoVehiculo = f.get("TIPO_VEHICULO")
        keyValue = self.getKeyFromTypeVehicle(tipoVehiculo)
        if keyValue!=None:
          conteoPorTablas[keyValue]+=1
      DisposeUtils.dispose(fset)
      DisposeUtils.dispose(storeVehiculos)
      toReport = False
      builder = StringBuilder()
      for key in conteoPorTablas.keys():
        if conteoPorTablas[key] != conteoPorFeature[key]:
          if toReport:
            builder.append(", ")
          toReport = True
          builder.append(key+" valor:"+str(conteoPorFeature[key])+" correccion:"+str(conteoPorTablas[key]))

      if toReport:
       report.add( feature.get("ID_ACCIDENTE"),
                  CODERR_VEHICULOS_NO_COINCIDEN,
                  "Vehiculos no coinciden: %s." % (
                    builder.toString(),
                  ),
                  fixerId = "UpdateCountVehicles", 
                  selected=True,
                  NUM_TURISMOS=conteoPorTablas['NUM_TURISMOS'],
                  NUM_FURGONETAS=conteoPorTablas['NUM_FURGONETAS'],
                  NUM_CAMIONES=conteoPorTablas['NUM_CAMIONES'],
                  NUM_AUTOBUSES=conteoPorTablas['NUM_AUTOBUSES'],
                  NUM_CICLOMOTORES=conteoPorTablas['NUM_CICLOMOTORES'],
                  NUM_MOTOCICLETAS=conteoPorTablas['NUM_MOTOCICLETAS'],
                  NUM_BICICLETAS=conteoPorTablas['NUM_BICICLETAS'],
                  NUM_OTROS_VEHI=conteoPorTablas['NUM_OTROS_VEHI']
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

  manager.addReportAttribute("NUM_TURISMOS",Integer, size=10, label="Turismos", isEditable=True)
  manager.addReportAttribute("NUM_FURGONETAS",Integer, size=10, label="Furgonetas", isEditable=True)
  manager.addReportAttribute("NUM_CAMIONES",Integer, size=10, label="Camiones", isEditable=True)
  manager.addReportAttribute("NUM_AUTOBUSES",Integer, size=10, label="Autobus", isEditable=True)
  manager.addReportAttribute("NUM_CICLOMOTORES",Integer, size=10, label="Ciclomotor", isEditable=True)
  manager.addReportAttribute("NUM_MOTOCICLETAS",Integer, size=10, label="Motocileta", isEditable=True)
  manager.addReportAttribute("NUM_BICICLETAS",Integer, size=10, label="Bicicleta", isEditable=True)
  manager.addReportAttribute("NUM_OTROS_VEHI",Integer, size=10, label="Otros Vehiculos", isEditable=True)


  


    
def main(*args):
  #test()
  #selfRegister()
  pass
