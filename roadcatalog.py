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

CODERR_CARRETERAKM_NO_ENCONTRADA = 100
CODERR_KM_NO_ENCONTRADO = 101
CODERR_SENTIDO_NO_VALIDO = 103
CODERR_CARRETERA_FECHA_O_PK_NO_INDICADOS = 104

try:
  from org.gvsig.lrs.lib.api import LrsAlgorithmsLocator
except:
  LrsAlgorithmsLocator = None

SENTIDO_ASCENDENTE = 1
SENTIDO_DESCENDENTE = 2
SENTIDO_MIXTO = 3

class StretchFeatureStoreCache(CachedValue):
  def reload(self):
    dataManager = DALLocator.getDataManager()
    repo = dataManager.getStoresRepository().getSubrepository("ARENA2_DB")
    self.setValue(repo.getStore("SIGCAR_TRAMOS_CARRETERAS"))

class DicSentidoCache(CachedValue):
  def reload(self):
    dataManager = DALLocator.getDataManager()
    repo = dataManager.getStoresRepository().getSubrepository("ARENA2_DB")
    store = repo.getStore("ARENA2_DIC_SENTIDO")
    d = dict()
    for f in store.getFeatureSet():
      d[f.get('ID')] = f.get('DESCRIPCION')
    DisposeUtils.dispose(store)
    self.setValue(d)

lrsManager = None
stretchFeatureStore = StretchFeatureStoreCache(5000);
dicSentido = DicSentidoCache(30000);

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
  # [ TC_FECHA_ENTRADA, TC_FECHA_SALIDA [
  builder = ExpressionUtils.createExpressionBuilder()
  filtro = builder.and( 
    builder.group( builder.or( 
        builder.le(builder.variable("TC_FECHA_ENTRADA"), builder.date(fecha)),
        builder.is_null(builder.variable("TC_FECHA_ENTRADA"))
    )),
    builder.group( builder.or( 
        builder.gt(builder.variable("TC_FECHA_SALIDA"), builder.date(fecha)),
        builder.is_null(builder.variable("TC_FECHA_SALIDA"))
    ))
  ).toString()
  
  return filtro


def getStretchesQuery(store, fecha, carretera, m):
  builder = ExpressionUtils.createExpressionBuilder()
  filtro = getStretchFilter(fecha, carretera, m)
  #print filtro
  query = store.createFeatureQuery()
  query.addFilter(filtro)
  return query

def getStretchFilter(fecha, carretera, m):
  # [ TC_FECHA_ENTRADA, TC_FECHA_SALIDA [
  builder = ExpressionUtils.createExpressionBuilder()
  builder.and(builder.or( 
            builder.le(builder.variable("TC_FECHA_ENTRADA"), builder.date(fecha)),
            builder.is_null(builder.variable("TC_FECHA_ENTRADA"))
          ))
  builder.and(builder.or( 
            builder.gt(builder.variable("TC_FECHA_SALIDA"), builder.date(fecha)),
            builder.is_null(builder.variable("TC_FECHA_SALIDA"))
          ))
  builder.and( 
    builder.eq(builder.variable("TC_MATRICULA"), builder.constant(carretera))
  )
  builder.and(builder.or(
    builder.and( 
      builder.le(builder.variable("TC_PK_I"), builder.constant(m)),
      builder.ge(builder.variable("TC_PK_F"), builder.constant(m))
    ),
    builder.and( 
      builder.le(builder.variable("TC_PK_F"), builder.constant(m)),
      builder.ge(builder.variable("TC_PK_I"), builder.constant(m))
    )))


  
  filtro = builder.toString()
  return filtro
  


def iif(cond, ontrue, onfalse):
  if cond:
    return ontrue
  return onfalse
  
def geocodificar(fecha, carretera, pk, sentido=None):
  if fecha == None or carretera == None or pk == None:
    return (None, None, "Fecha%s, carretera%s o pk%s nulo" % (
        iif(fecha==None, "*",""),
        iif(carretera==None, "*",""),
        iif(pk==None, "*","")
      ),
      CODERR_CARRETERA_FECHA_O_PK_NO_INDICADOS
    )
  sentidoStr = None
  if sentido != None:
    sentidoStr = dicSentido.get().get(sentido, None)
    if sentidoStr==None:
      #Incidencia de sentido no válido en el accidente [SENTIDO NO VALIDO]
      return (None, None, "Sentido '%s' no válido." %(sentido), CODERR_SENTIDO_NO_VALIDO)
  
  stretchesStore = getStretchFeatureStore()
  pk = pk * 1000 
  query = getStretchesQuery(stretchesStore, fecha, carretera, pk) 

  builder = ExpressionUtils.createExpressionBuilder()
  #expression = builder.eq(builder.variable("TC_MATRICULA"), builder.constant(carretera)).toString()
  stretches = None  
  it = None
  try:
    #query.addFilter(expression)
    query.retrievesAllAttributes()
    stretches = stretchesStore.getFeatureSet(query)
    if stretches.isEmpty():
        #Incidencia de carretera no encontrada [CARRETERA NO ENCONTRADA]
        return (None, None, "Carretera '%s' no encontrada" % carretera, CODERR_CARRETERAKM_NO_ENCONTRADA)
        
    bestStretch = None
    bestLocation = None
    it = stretches.iterable()
    for stretch in it:
      location = getLRSManager().getMPointFromGeometry(stretch.getDefaultGeometry(), pk)
      if location != None:
          # LRS devuelve un Point2DM y falla al guardarse en la BBDD (H2 por lo menos)
        location = GeometryUtils.createPoint(location.getX(), location.getY())

        # TODO: Ver si todo coincide y darlo por bueno
        if sentido != None and sentido == stretch.get('TC_SENTIDO'):
          return (location, stretch, None, None)
         
        if bestStretch == None:
          bestStretch = stretch
          bestLocation = location
        else:
         if isBetterStretch(bestStretch, stretch, sentido):
            bestStretch = stretch
            bestLocation = location
    if bestStretch == None: #Punto kilometrico no encontrado
      if sentido==None:
        #Incidencia de punto kilometrico no encontrado en la carretera [PUNTO KM NO ENCONTRADO]
        return (None, None, "kilometro %.3f no encontrado a fecha %s en '%s'." % (pk/1000,String.format("%td/%tm/%tY",fecha,fecha,fecha),carretera), CODERR_KM_NO_ENCONTRADO)
      else:
        sentidoStr = dicSentido.get().get(sentido, None)
        #Incidencia de punto kilometrico no encontrado en la carretera en el sentido [PUNTO KM NO ENCONTRADO]
        return (None, None, "kilometro %.3f no encontrado a fecha %s en '%s' en sentido '%s'." % (pk/1000,String.format("%td/%tm/%tY",fecha,fecha,fecha),carretera,sentidoStr), CODERR_KM_NO_ENCONTRADO)
    else:
      if sentido == None:
        return (bestLocation, bestStretch, None, None)
      else: 
        if bestStretch.get("TC_SENTIDO") in (None, SENTIDO_MIXTO, sentido):
          return (bestLocation, bestStretch, None, None)
        else:
          #Incidencia el sentido del accidente no coincide con el sentido del tramo encontrado  [SENTIDO NO VALIDO]
          return (None, None, "kilometro %.3f no encontrado a fecha %s en '%s' en sentido '%s'." % (pk/1000,String.format("%td/%tm/%tY",fecha,fecha,fecha),carretera,sentidoStr), CODERR_SENTIDO_NO_VALIDO)
    return (bestLocation, bestStretch, None, None)
  finally:
    DisposeUtils.disposeQuietly(it)
    DisposeUtils.disposeQuietly(stretches)

def isBetterStretch(bestStretch, stretch, sentido):
  s = sentido
  if sentido == None:
    s = SENTIDO_ASCENDENTE

  if s == bestStretch.get('TC_SENTIDO'):
    return False
  if s == stretch.get('TC_SENTIDO'):
    return True
  if stretch.get('TC_SENTIDO') == SENTIDO_MIXTO:
    return True
  return False
 
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
  pass

def main1(*args):
    from java.util import Date
    fecha = Date()
    builder = ExpressionUtils.createExpressionBuilder()
    print builder.and( 
      builder.group( builder.or( 
          builder.le(builder.variable("TC_FECHA_ENTRADA"), builder.date(fecha)),
          builder.is_null(builder.variable("TC_FECHA_ENTRADA"))
      )),
      builder.group( builder.or( 
          builder.gt(builder.variable("TC_FECHA_SALIDA"), builder.date(fecha)),
          builder.is_null(builder.variable("TC_FECHA_SALIDA"))
      ))
    ).toString()      
    print builder.toString()
    """
    print getStretchFeatureStore()
    
    print "f",findOwnership(fecha, 'CV301', 10)
    
    print "f",findOwnership(fecha, 'CV-70', 49.7)
    """
