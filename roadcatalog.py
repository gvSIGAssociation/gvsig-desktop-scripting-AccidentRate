# encoding: utf-8

import gvsig

from gvsig.uselib import use_plugin

use_plugin("org.gvsig.lrs.app.mainplugin")

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
    #store = getCarreterasManager().getStretchFeatureStore()
    dataManager = DALLocator.getDataManager()
    pool = dataManager.getDataServerExplorerPool()
    explorerParams = pool.get("carreteras_gva").getExplorerParameters()
    explorerParams.setSchema("layers")
    explorer = dataManager.openServerExplorer(explorerParams.getProviderName(), explorerParams)
    params = explorer.get("tramos_carreteras")
    store = dataManager.openStore(params.getProviderName(), params)
    self.setValue(store)

lrsManager = None
stretchFeatureStore = StretchFeatureStoreCache(5000);


def getLRSManager():
  global lrsManager
  if lrsManager == None:
    lrsManager = LrsAlgorithmsLocator.getLrsAlgorithmsManager()
  return lrsManager

def getStretchFeatureStore():
  return stretchFeatureStore.get()

def checkRequirements():
  dataManager = DALLocator.getDataManager()
  s = ""
  if getLRSManager()==None:
    s += "No se ha podido acceder al plugin de LRS, es posible que no se encuentre instalado.\n"
  pool = dataManager.getDataServerExplorerPool()
  if pool.get("carreteras_gva")==None:
    s += "No se ha podido localizar la conexion 'carreteras_gva' para poder acceder a las capas de carreteras\n"
  else:
    try:
      explorerParams = pool.get("carreteras_gva").getExplorerParameters()    
      explorerParams.setSchema("layers")
      explorer = dataManager.openServerExplorer(explorerParams.getProviderName(), explorerParams)
      params = explorer.get("tramos_carreteras")
    except:
      params = None
      
    if params == None:
      s += "No se ha podido acceder a la tabla 'layers.tramos_carreteras'.\n"
  if s.strip() == "":
    return None
  return s

def getVigentStretchesQuery(store, fecha):
  builder = ExpressionUtils.createExpressionBuilder()
  filtro = builder.and( 
    builder.group( builder.or( 
        builder.le(builder.variable("fecha_entrada"), builder.date(fecha)),
        builder.is_null(builder.variable("fecha_entrada"))
    )),
    builder.group( builder.or( 
        builder.le(builder.variable("fecha_salida"), builder.date(fecha)),
        builder.is_null(builder.variable("fecha_salida"))
    ))
  ).toString()
  
  #dateFormatter = SimpleDateFormat("dd/MM/yyyy")
  #formatedDate = dateFormatter.format(fecha)
  #filtro = "( fecha_entrada <= '%s' OR fecha_entrada IS NULL) AND ('%s' <= fecha_salida OR fecha_salida IS NULL)" % (
  #  formatedDate,
  #  formatedDate
  #)
  
  query = store.createFeatureQuery()
  query.addFilter(filtro)
  return query

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
  expression = builder.eq(builder.variable("matricula"), builder.constant(carretera)).toString()
  #expression = "matricula = '%s'" % carretera
  try:
    query.addFilter(expression)
    query.retrievesAllAttributes()
    streches = strechesStore.getFeatureSet(query)
    if len(streches)<1:
      return (None, None, "Carretera '%s' no encontrada" % carretera)

    for strech in streches:
      location = getLRSManager().getMPointFromGeometry(strech.getDefaultGeometry(), pk)
      if location != None:
        # LRS devuelve un Point2DM y falla al guardarse en la BBDD (H2 por lo menos)
        location = GeometryUtils.createPoint(location.getX(), location.getY())
        return (location, strech, None)
    return (None, None, "kilometro %s no encontrado en '%s'." % (pk,carretera))
  finally:
    DisposeUtils.disposeQuietly(streches)

def findOwnership(fecha, carretera, pk):
  if fecha == None or carretera == None or pk == None:
    return None
  strechesStore = getStretchFeatureStore()
  query = getVigentStretchesQuery(strechesStore, fecha) 

  builder = ExpressionUtils.createExpressionBuilder()
  builder.and( builder.eq(builder.variable("matricula"), builder.constant(carretera)))
  builder.and( builder.ge(builder.variable("pk_i"), builder.constant(pk)))
  builder.and( builder.le(builder.variable("pk_f"), builder.constant(pk)))
  expression = builder.toString()
  #expression = "matricula = '%s' and pk_i >= %s and pk_f <= %s" % (carretera, pk, pk)
  query.addFilter(expression)
  query.retrievesAllAttributes()
  feature = strechesStore.findFirst(query)
  if feature == None:
    return None
  return feature.get("titularidad")


def main(*args):
    from java.util import Date
    fecha = Date()
    builder = ExpressionUtils.createExpressionBuilder()
    print builder.and( 
      builder.group( builder.or( 
          builder.le(builder.variable("fecha_entrada"), builder.date(fecha)),
          builder.is_null(builder.variable("fecha_entrada"))
      )),
      builder.group( builder.or( 
          builder.le(builder.variable("fecha_salida"), builder.date(fecha)),
          builder.is_null(builder.variable("fecha_salida"))
      ))
    ).toString()      
    print builder.toString()
