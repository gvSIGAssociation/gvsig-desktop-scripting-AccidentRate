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
from java.time import DayOfWeek

class AsignarTipoDiaCitTransform(Transform):
  def __init__(self, factory, **args):
    Transform.__init__(self, factory)
    self.workspace = args.get("workspace",None)
    self.repo = self.workspace.getStoresRepository()

  def apply(self, feature, *args):
    tags = feature.getType().getTags()
    storeName = tags.getString("accidentrate.storename",None)

    festivosStore = self.repo.getStore("SIGCAR_FESTIVOS")
    try:
      #if feature.getType().get("LID_ACCIDENTE") != None:
      if storeName == "ARENA2_ACCIDENTES":
        fecha = feature.get("FECHA_ACCIDENTE")
        if fecha in ("",None):
          return
        fecha = DataTypeUtils.toLocalDate(fecha);
        #idAccidente = feature.get("ID_ACCIDENTE")
        diaMes = fecha.getDayOfMonth()
        
        tipoDia = findTipoDia(self.repo, fecha)
        extra = feature.get("EXTRA")
        extra = addDataToJsonExtra(extra, diaMes, tipoDia)
        feature.set("EXTRA", extra)
        return
  
      if storeName in ( "ARENA2_VEHICULOS", "ARENA2_CONDUCTORES", "ARENA2_PASAJEROS", "ARENA2_PEATONES"):
        accidente = feature.getForeignFeature("ID_ACCIDENTE")
        if accidente == None:
          logger("No se ha encontrado el accidente '%s'."%feature.get("ID_ACCIDENTE"), LOGGER_WARN)
        else:
          extra = feature.get("EXTRA")
          extra = addDataToJsonExtra(extra, accidente.get("DIA_CIT"), accidente.get("TIPO_DIA_CIT"))
          feature.set("EXTRA", extra)
        return
      print "Skip feature %r" %storeName
    finally:
      DisposeUtils.disposeQuietly(festivosStore)

def findTipoDia(repo, fecha):
  festivosStore = repo.getStore("SIGCAR_FESTIVOS")
  try:
    builder = ExpressionUtils.createExpressionBuilder()
    filter = builder.eq(builder.variable("FES_FECHA"), builder.constant(fecha))
    festivo = festivosStore.findFirst(filter.toString())
    if festivo != None or fecha.getDayOfWeek() == DayOfWeek.SUNDAY:
      return 2 #festivo
      
    builder = ExpressionUtils.createExpressionBuilder()
    filter = builder.eq(builder.variable("FES_FECHA"), builder.constant(fecha.plusDays(1))) # Añadir un día a la fecha
    vispera = festivosStore.findFirst(filter.toString()) 
    if vispera != None or fecha.getDayOfWeek() == DayOfWeek.SATURDAY:
      return 1 #Anterior a festivo
      
    builder = ExpressionUtils.createExpressionBuilder()
    filter = builder.eq(builder.variable("FES_FECHA"), builder.constant(fecha.minusDays(1))) # Quitar un día a la fecha
    eosfora = festivosStore.findFirst(filter.toString()) 
    if eosfora != None or fecha.getDayOfWeek() == DayOfWeek.MONDAY:
      return 3 #Posterior a festivo
  
    
    return 0 #Laborable
  finally:
    DisposeUtils.disposeQuietly(festivosStore)

    
  
def addDataToJsonExtra(extra, diaMes, tipoDia):
  if extra in (None, ""):
    extraJson = Json.createObjectBuilder()
  else:
    extraJson = Json.createObjectBuilder(extra)
  extraJson.add("dia_cit",diaMes)
  extraJson.add("tipo_dia_cit",tipoDia)
  return  extraJson.build()

class AsignarTipoDiaCitTransformFactory(TransformFactory):
  def __init__(self):
    TransformFactory.__init__(self,u"[GVA] Asignar Tipo de día")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo es posible realizar la asignacion del día y del tipo de día\n"+s
    return None
    
  def create(self,  **args):
    return AsignarTipoDiaCitTransform(self, **args)
    
def selfRegister():
  manager = getArena2ImportManager()
  manager.addTransformFactory(AsignarTipoDiaCitTransformFactory())


def test():
  from java.util import Date
  try:
    dataManager = DALLocator.getDataManager()
    workspace = dataManager.getDatabaseWorkspace("ARENA2_DB")
    store = workspace.getStoresRepository().getStore("ARENA2_ACCIDENTES")
    storeVehiculos = workspace.getStoresRepository().getStore("ARENA2_VEHICULOS")

    dataManager = DALLocator.getDataManager()
    trans = dataManager.createTransaction()
    trans.begin()
    trans.add(store)
    trans.add(storeVehiculos)

    
    factory = AsignarTipoDiaCitTransformFactory()
    transform = factory.create(workspace = workspace)
    f0 = store.findFirst("ID_ACCIDENTE =  '202303018000001'").getEditable() #04/01/2023 laborable
    f1 = store.findFirst("ID_ACCIDENTE =  '202303043000001'").getEditable() #05/01/2023 vispera de reyes
    f2 = store.findFirst("ID_ACCIDENTE =  '202303024000001'").getEditable() #06/01/2023 reyes
    f3 = store.findFirst("ID_ACCIDENTE =  '202312094000001'").getEditable() #07/01/2023 eósfora de reyes
    f4 = store.findFirst("ID_ACCIDENTE =  '202303021000001'").getEditable() #14/01/2023 sábado
    f5 = store.findFirst("ID_ACCIDENTE =  '202303004000001'").getEditable() #15/01/2023 domingo
    f6 = store.findFirst("ID_ACCIDENTE =  '202303059000005'").getEditable() #16/01/2023 lunes
    features = [f0, f1, f2, f3, f4, f5, f6]
    store.edit()
    for feature in features:
      transform.apply(feature)
      store.update(feature)
      print u"%s %s: %s | %s" %(feature.get("ID_ACCIDENTE"), feature.get("FECHA_ACCIDENTE") ,feature.get("DIA_CIT"), feature.getLabelOfValue("TIPO_DIA_CIT"))
      vehiculos = storeVehiculos.getFeatureSet(u"ID_ACCIDENTE = '"+feature.get("ID_ACCIDENTE")+u"'")
      #for vehiculo in feature.get("VEHICULOS"):
      storeVehiculos.edit()
      for vehiculo in vehiculos:
        ved =  vehiculo.getEditable()
        transform.apply(ved)
        vehiculos.update(ved)
        #storeVehiculos.update(ved)
        print u"\t%s %s %s: %s | %s" %(ved.get("ID_VEHICULO"), ved.get("MARCA_NOMBRE") , ved.get("MODELO") ,ved.get("DIA_CIT"), ved.getLabelOfValue("TIPO_DIA_CIT"))
      storeVehiculos.finishEditing()
    store.finishEditing()
    trans.commit()    
  finally:
   store.dispose()
   trans.dispose()

def main(*args):
  #selfRegister()
  test()
  
  
