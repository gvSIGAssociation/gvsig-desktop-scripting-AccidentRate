# encoding: utf-8

import gvsig

from gvsig.uselib import use_plugin

use_plugin("org.gvsig.lrs.app.mainplugin")

from java.lang import String
from java.text import SimpleDateFormat
from org.gvsig.tools.dispose import DisposeUtils
from org.gvsig.tools.util import CachedValue
from org.gvsig.fmap.dal import DALLocator
from org.gvsig.fmap.geom import GeometryUtils
from org.gvsig.expressionevaluator import ExpressionUtils

try:
  from org.gvsig.lrs.lib.api import LrsAlgorithmsLocator
except:
  LrsAlgorithmsLocator = None

class StretchFeatureStoreCache(CachedValue):
  def reload(self):
    dataManager = DALLocator.getDataManager()
    repo = dataManager.getStoresRepository().getSubrepository("ARENA2_DB")
    self.setValue(repo.getStore("SIGCAR_TRAMOS_CARRETERAS"))


lrsManager = None
stretchFeatureStore = StretchFeatureStoreCache(5000);

def getLRSManager():
  if LrsAlgorithmsLocator == None:
    return None
  global lrsManager
  if lrsManager == None:
    lrsManager = LrsAlgorithmsLocator.getLrsAlgorithmsManager()
  return lrsManager

def getStretchFeatureStore():
  return stretchFeatureStore.get()
  

def checkRequirements():
  dataManager = DALLocator.getDataManager()
  s = u""
  if getLRSManager()==None:
    s += u"No se ha podido acceder al plugin de LRS, es posible que no se encuentre instalado.\n"
  try:
    ws = dataManager.getDatabaseWorkspace("ARENA2_DB")
    if ws == None:
      s += u"No se ha encontrado el espacio de trabajo de ARENA2_DB.\n"
    else:
      if not ws.isConnected():
        s += u"No se está conectado a un espacio de trabajo de ARENA2_DB.\n"
  except:
    s += u"No se ha podido acceder al espacio de trabajo ARENA2_DB.\n"
  if s.strip() == "":
    return None
  return s

def getVigentStretchesQuery(store, fecha):
  builder = ExpressionUtils.createExpressionBuilder()
  filtro = getVigentStretchesFilter(fecha)
  
  query = store.createFeatureQuery()
  query.addFilter(filtro)
  return query

def getVigentStretchesFilter(fecha):
  builder = ExpressionUtils.createExpressionBuilder()
  filtro = builder.and( 
    builder.group( builder.or( 
        builder.le(builder.variable("TC_FECHA_ENTRADA"), builder.date(fecha)),
        builder.is_null(builder.variable("TC_FECHA_ENTRADA"))
    )),
    builder.group( builder.or( 
        builder.ge(builder.variable("TC_FECHA_SALIDA"), builder.date(fecha)),
        builder.is_null(builder.variable("TC_FECHA_SALIDA"))
    ))
  ).toString()
  
  return filtro


def iif(cond, ontrue, onfalse):
  if cond:
    return ontrue
  return onfalse
  
def geocodificar(fecha, carretera, pk):
  if fecha == None or carretera == None or pk == None:
    return (None, None, "Fecha%s, carretera%s o pk%s nulo" % (
        iif(fecha==None, "*",""),
        iif(carretera==None, "*",""),
        iif(pk==None, "*","")
      )
    )
  strechesStore = getStretchFeatureStore()
  query = getVigentStretchesQuery(strechesStore, fecha) 

  builder = ExpressionUtils.createExpressionBuilder()
  expression = builder.eq(builder.variable("TC_MATRICULA"), builder.constant(carretera)).toString()
  streches = None  
  try:
    query.addFilter(expression)
    query.retrievesAllAttributes()
    streches = strechesStore.getFeatureSet(query).iterable()
    if streches.isEmpty():
      return (None, None, "Carretera '%s' no encontrada" % carretera)
    pk = pk * 1000 
    for strech in streches:
      location = getLRSManager().getMPointFromGeometry(strech.getDefaultGeometry(), pk)
      if location != None:
        # LRS devuelve un Point2DM y falla al guardarse en la BBDD (H2 por lo menos)
        location = GeometryUtils.createPoint(location.getX(), location.getY())
        return (location, strech, None)
    return (None, None, "kilometro %.3f no encontrado a fecha %s en '%s'." % (pk/1000,String.format("%td/%tm/%tY",fecha,fecha,fecha),carretera))
  finally:
    DisposeUtils.disposeQuietly(streches)

def findOwnership(fecha, carretera, pk):
  if fecha == None or carretera == None or pk == None:
    return None
  strechesStore = getStretchFeatureStore()
  query = getVigentStretchesQuery(strechesStore, fecha) 
  pk = pk * 1000 
  builder = ExpressionUtils.createExpressionBuilder()
  builder.and( builder.eq(builder.variable("TC_MATRICULA"), builder.constant(carretera)))
  builder.and( builder.le(builder.variable("TC_PK_I"), builder.constant(pk)))
  builder.and( builder.ge(builder.variable("TC_PK_F"), builder.constant(pk)))
  expression = builder.toString()
  query.addFilter(expression)
  query.retrievesAllAttributes()
  feature = strechesStore.findFirst(query)
  if feature == None:
    return None
  return feature.get("TC_TITULARIDAD")

def main0(*args):
  print checkRequirements()  

def main(*args):
    from java.util import Date
    fecha = Date()
    builder = ExpressionUtils.createExpressionBuilder()
    print builder.and( 
      builder.group( builder.or( 
          builder.le(builder.variable("TC_FECHA_ENTRADA"), builder.date(fecha)),
          builder.is_null(builder.variable("TC_FECHA_ENTRADA"))
      )),
      builder.group( builder.or( 
          builder.ge(builder.variable("TC_FECHA_SALIDA"), builder.date(fecha)),
          builder.is_null(builder.variable("TC_FECHA_SALIDA"))
      ))
    ).toString()      
    print builder.toString()
    """
    print getStretchFeatureStore()
    
    print "f",findOwnership(fecha, 'CV301', 10)
    
    print "f",findOwnership(fecha, 'CV-70', 49.7)
    """
