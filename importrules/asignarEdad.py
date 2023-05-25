# encoding: utf-8

import gvsig

from gvsig import logger, LOGGER_WARN, LOGGER_ERROR
from addons.AccidentRate.aforos import findMedidaAforo, checkRequirements

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer

from org.gvsig.fmap.dal import DALLocator
from org.gvsig.tools.dataTypes import DataTypes, DataTypeUtils
from org.gvsig.tools.dispose import DisposeUtils
from org.gvsig.expressionevaluator import ExpressionUtils
from org.gvsig.json import Json
from java.time import DayOfWeek, Period

class AsignarEdadTransform(Transform):
  def __init__(self, factory, **args):
    Transform.__init__(self, factory)
    self.workspace = args.get("workspace",None)
    self.repo = self.workspace.getStoresRepository()

  def apply(self, feature, *args):

    tags = feature.getType().getTags()
    storeName = tags.getString("accidentrate.storename",None)

    if (feature.getType().get("FECHA_NACIMIENTO") != None) :
      accidente = feature.getForeignFeature("ID_ACCIDENTE")
      if(accidente == None):
        logger("No se ha encontrado el accidente '%s'."%feature.get("ID_ACCIDENTE"), LOGGER_WARN)
        return
      fechaAccidente = accidente.get("FECHA_ACCIDENTE")
      if(fechaAccidente == None):
        return
      fechaAccidente = DataTypeUtils.toLocalDate(fechaAccidente);
      fechaNacimiento = feature.get("FECHA_NACIMIENTO")
      if(fechaNacimiento == None):
        return
      fechaNacimiento = DataTypeUtils.toLocalDate(fechaNacimiento);

      period = Period.between(fechaNacimiento,fechaAccidente)
      edad = period.getYears()
      extra = feature.get("EXTRA")
      extra = addDataToJsonExtra(extra, edad)
      feature.set("EXTRA", extra)
      return

    '''
    if feature.getType().get("LID_CONDUCTOR") != None:
      accidente = feature.getForeignFeature("ID_ACCIDENTE")
      extra = feature.get("EXTRA")
      extra = addDataToJsonExtra(extra, accidente.get("DIA_CIT"), accidente.get("TIPO_DIA_CIT"))
      feature.set("EXTRA", extra)
      return

    if feature.getType().get("LID_PASAJERO") != None:
      accidente = feature.getForeignFeature("ID_ACCIDENTE")
      extra = feature.get("EXTRA")
      extra = addDataToJsonExtra(extra, accidente.get("DIA_CIT"), accidente.get("TIPO_DIA_CIT"))
      feature.set("EXTRA", extra)
      return

    if feature.getType().get("LID_PEATON") != None:
      accidente = feature.getForeignFeature("ID_ACCIDENTE")
      extra = feature.get("EXTRA")
      extra = addDataToJsonExtra(extra, accidente.get("DIA_CIT"), accidente.get("TIPO_DIA_CIT"))
      feature.set("EXTRA", extra)
      return
    '''

  
def addDataToJsonExtra(extra, edad):
  if extra in (None, ""):
    extraJson = Json.createObjectBuilder()
  else:
    extraJson = Json.createObjectBuilder(extra)
  extraJson.add("edad_cit",edad)
  return  extraJson.build()

class AsignarEdadTransformFactory(TransformFactory):
  def __init__(self):
    TransformFactory.__init__(self,"[GVA] Asignar Edad")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo es posible realizar la asignacion de la edad\n"+s
    return None
    
  def create(self,  **args):
    return AsignarEdadTransform(self, **args)
    
def selfRegister():
  manager = getArena2ImportManager()
  manager.addTransformFactory(AsignarEdadTransformFactory())


def test():
  from java.util import Date
  try:
    dataManager = DALLocator.getDataManager()
    workspace = dataManager.getDatabaseWorkspace("ARENA2_DB")
    store = workspace.getStoresRepository().getStore("ARENA2_ACCIDENTES")
    storeConductores = workspace.getStoresRepository().getStore("ARENA2_CONDUCTORES")
    storePasajeros = workspace.getStoresRepository().getStore("ARENA2_PASAJEROS")
    storePeatones = workspace.getStoresRepository().getStore("ARENA2_PEATONES")

    dataManager = DALLocator.getDataManager()
    trans = dataManager.createTransaction()
    trans.begin()
    trans.add(store)
    trans.add(storeConductores)
    trans.add(storePasajeros)
    trans.add(storePeatones)

    
    factory = AsignarEdadTransformFactory()
    transform = factory.create(workspace = workspace)
    f0 = store.findFirst("ID_ACCIDENTE =  '202303018000001'").getEditable() #04/01/2023
    f1 = store.findFirst("ID_ACCIDENTE =  '202303043000001'").getEditable() #05/01/2023
    f2 = store.findFirst("ID_ACCIDENTE =  '202303024000001'").getEditable() #06/01/2023
    f3 = store.findFirst("ID_ACCIDENTE =  '202312094000001'").getEditable() #07/01/2023
    f4 = store.findFirst("ID_ACCIDENTE =  '202303021000001'").getEditable() #14/01/2023
    f5 = store.findFirst("ID_ACCIDENTE =  '202303004000001'").getEditable() #15/01/2023
    f6 = store.findFirst("ID_ACCIDENTE =  '202303059000005'").getEditable() #16/01/2023
    features = [f0, f1, f2, f3, f4, f5, f6]
    store.edit()
    for feature in features:
      transform.apply(feature)
      store.update(feature)
      print u"ACCIDENTE %s -- %s" %(feature.get("ID_ACCIDENTE"), feature.get("FECHA_ACCIDENTE") )
      conductores = storeConductores.getFeatureSet(u"ID_ACCIDENTE = '"+feature.get("ID_ACCIDENTE")+u"'")

      storeConductores.edit()
      print u"CONDUCTORES"
      for conductor in conductores:
        condEd =  conductor.getEditable()
        transform.apply(condEd)
        conductores.update(condEd)
        #storeVehiculos.update(ved)
        print u"\t%s %s EDAD:%s" %(condEd.get("LID_VEHICULO"), condEd.get("FECHA_NACIMIENTO") , condEd.get("EDAD_CIT"))
      storeConductores.finishEditing()

      pasajeros = storePasajeros.getFeatureSet(u"ID_ACCIDENTE = '"+feature.get("ID_ACCIDENTE")+u"'")
      storePasajeros.edit()
      print u"PASAJEROS"
      for pasajero in pasajeros:
        pasEd =  pasajero.getEditable()
        transform.apply(pasEd)
        pasajeros.update(pasEd)
        print u"\t%s %s EDAD:%s" %(pasEd.get("ID_PASAJERO"), pasEd.get("FECHA_NACIMIENTO") , pasEd.get("EDAD_CIT"))
      storePasajeros.finishEditing()

      peatones = storePeatones.getFeatureSet(u"ID_ACCIDENTE = '"+feature.get("ID_ACCIDENTE")+u"'")
      storePeatones.edit()
      print u"PEATONES"
      for peaton in peatones:
        peaEd =  peaton.getEditable()
        transform.apply(peaEd)
        conductores.update(peaEd)
        print u"\t%s %s EDAD:%s" %(peaEd.get("ID_PEATON"), peaEd.get("FECHA_NACIMIENTO") , peaEd.get("EDAD_CIT"))
      storePeatones.finishEditing()

    store.finishEditing()
    trans.commit()    
  finally:
   store.dispose()
   trans.dispose()

def main(*args):
  selfRegister()
  #test()
  
  
