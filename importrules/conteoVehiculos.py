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

AGRUPACIONES = {'NUM_TURISMOS' : [1,3],
     'NUM_FURGONETAS' : [2],
     'NUM_CAMIONES' : [19,20,21],
     'NUM_AUTOBUSES' : [15,16,17],
     'NUM_CICLOMOTORES' : [5],
     'NUM_MOTOCICLETAS' : [6,7],
     'NUM_BICICLETAS' : [4,30],
     'NUM_OTROS_VEHI' : [8,9,10,11,12,13,14,18,22,23,24,25,26,27]
     }

class UpdateCountVehicles(RuleFixer):
  def __init__(self, **args):
    RuleFixer.__init__(self, "UpdateCountVehicles", "Corregir vehiculos", True)

  def fix(self,feature, issue):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    for key in AGRUPACIONES.keys():
      valueToChange = issue.get(key)
      if feature.get(key)!=issue.get(key):
        feature.set(key, valueToChange)

class CountVehiclesRule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)

  def getKeyFromTypeVehicle(self, value):
    if value==None:
        return None
    for key in AGRUPACIONES.keys():
      toAssign = value in AGRUPACIONES[key]
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
        elif tipoVehiculo > 31:
          conteoPorTablas['NUM_OTROS_VEHI']+=1
          
      DisposeUtils.dispose(fset)
      DisposeUtils.dispose(storeVehiculos)
      toReport = False
      builder = StringBuilder()
      for key in conteoPorTablas.keys():
        n = conteoPorFeature[key]
        if n == None:
          n = 0
        if conteoPorTablas[key] != n:
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


class NumVehiclesTransform(Transform):
  def __init__(self, factory, **args):
    Transform.__init__(self, factory)

  def apply(self, feature, *args):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    for key in AGRUPACIONES.keys():
      if feature.get(key) == None:
        feature.set(key, 0)

class NumVehiclesTransformFactory(TransformFactory):
  def __init__(self):
    TransformFactory.__init__(self,"[GVA] Sustituir nulos por ceros en NUM_XXX")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo  es posible realizar las transformaciones en el numero de vehiculos\n"+s
    return None
    
  def create(self,  **args):
    return NumVehiclesTransform(self, **args)


class CountVehiclesTransform(Transform):
  def __init__(self, factory, **args):
    Transform.__init__(self, factory)
    self.agrupaciones = {'NUM_VMP' : [28],
     'NUM_BICICLETASELECTRICAS' : [31],
     'NUM_DESCONOCIDO' : [29]
     }

  def apply(self, feature, *args):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    storeVehiculos= feature.getStore().getStoresRepository().getStore("ARENA2_VEHICULOS")
    accidente = feature.get("ID_ACCIDENTE")

    if accidente !=None:
      ## Rellenar por campos de la feature
      # Mantiene el none
      # no es lo mismo que llegue un None 
      # a que se confirme porque no tiene valores en la tabla
      # de vehiculos con que es 0
      conteo = { 'NUM_VMP': None,
        'NUM_BICICLETASELECTRICAS': None,
        'NUM_DESCONOCIDO': None
      }

      ## Conteo por la tabla asociada de vehiculos
      builder = ExpressionUtils.createExpressionBuilder()
      expression = builder.eq(builder.variable("ID_ACCIDENTE"), builder.constant(accidente)).toString()
      fset = storeVehiculos.getFeatureSet(expression).iterable()
      for f in fset:
        tipoVehiculo = f.get("TIPO_VEHICULO")
        keyValue = self.getKeyFromTypeVehicle(tipoVehiculo, conteo.keys())
        if keyValue!=None:
          conteoPorTablas[keyValue]+=1
        else:
          conteoPorTablas[NUM_DESCONOCIDO]+=1
          
      DisposeUtils.dispose(fset)
      DisposeUtils.dispose(storeVehiculos)

      for key in conteo.keys():
        feature.set(key, conteo[key])

      descuadre = feature.getInt('TOTAL_VEHICULOS_DGT')-(
        feature.getInt('NUM_TURISMOS') + 
        feature.getInt('NUM_FURGONETAS') + 
        feature.getInt('NUM_CAMIONES') + 
        feature.getInt('NUM_AUTOBUSES') + 
        feature.getInt('NUM_CICLOMOTORES') + 
        feature.getInt('NUM_MOTOCICLETAS') + 
        feature.getInt('NUM_BICICLETAS') + 
        feature.getInt('NUM_OTROS_VEHI') + 
        feature.getInt('NUM_VMP') + 
        feature.getInt('NUM_BICICLETASELECTRICAS') + 
        feature.getInt('NUM_DESCONOCIDO')
        )

      feature.set('TOTAL_VEHICULOS_DESCUADRE',descuadre)
  
  def getKeyFromTypeVehicle(self, value, keys):
    if value==None:
        return None
    for key in keys:
      toAssign = value in self.agrupaciones[key]
      if toAssign:
        return key
    return None

class CountVehiclesTransformFactory(TransformFactory):
  def __init__(self):
    TransformFactory.__init__(self,u"[GVA] Conteo de biciletas eléctricas, VMP y cálculo del descuadre")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+u".\nNo  es posible realizar las transformaciones en el conteo de biciletas eléctricas, VMP y cálculo del descuadre\n"+s
    return None
    
  def create(self,  **args):
    return NumVehiclesTransform(self, **args)

    
def selfRegister():
  manager = getArena2ImportManager()
  manager.addRuleFactory(CountVehiclesRuleFactory())
  manager.addRuleFixer(UpdateCountVehicles())
  manager.addTransformFactory(NumVehiclesTransformFactory())
  manager.addTransformFactory(CountVehiclesTransformFactory())
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
