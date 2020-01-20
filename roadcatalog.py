# encoding: utf-8

import gvsig

from gvsig.uselib import use_plugin

use_plugin("org.gvsig.cegesev.roadcatalog.app.mainplugin")
use_plugin("org.gvsig.lrs.app.mainplugin")

from java.text import SimpleDateFormat
from org.gvsig.tools.dispose import DisposeUtils
from org.gvsig.tools.util import CachedValue
from org.gvsig.fmap.dal import DALLocator
from org.gvsig.fmap.geom import GeometryUtils

try:
  from org.gvsig.cegesev.roadcatalog import AccidentCatalogLocator
except:
  AccidentCatalogLocator = None

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

carreterasManager = None
lrsManager = None
stretchFeatureStore = StretchFeatureStoreCache(5000);

def getCarreterasManager():
  global carreterasManager
  if carreterasManager == None:
    carreterasManager = AccidentCatalogLocator.getManager()
  return carreterasManager

def getLRSManager():
  global lrsManager
  if lrsManager == None:
    lrsManager = LrsAlgorithmsLocator.getLrsAlgorithmsManager()
  return lrsManager

def getStretchFeatureStore():
  return stretchFeatureStore.get()

def getVigentStretchesQuery(store, fecha):
  #query = getCarreterasManager().getVigentStretchesQuery(store, fecha) 
  dateFormatter = SimpleDateFormat("dd/MM/yyyy")
  formatedDate = dateFormatter.format(fecha)
  filtro = "( fecha_entrada <= '%s' OR fecha_entrada IS NULL) AND ('%s' <= fecha_salida OR fecha_salida IS NULL)" % (
    formatedDate,
    formatedDate
  )
  query = store.createFeatureQuery()
  query.addFilter(filtro)
  return query

def geocodificar(fecha, carretera, pk):
  if fecha == None or carretera == None or pk == None:
    return (None, "Fecha, carretera o pk nulo")
  strechesStore = getStretchFeatureStore()
  query = getVigentStretchesQuery(strechesStore, fecha) 

  expression = "matricula = '%s'" % carretera
  try:
    query.addFilter(expression)
    query.retrievesAllAttributes()
    streches = strechesStore.getFeatureSet(query)
    if len(streches)<1:
      return (None,"Carretera '%s' no encontrada" % carretera)

    for strech in streches:
      location = getLRSManager().getMPointFromGeometry(strech.getDefaultGeometry(), pk)
      if location != None:
        # LRS devuelve un Point2DM y falla al guardarse en la BBDD (H2 por lo menos)
        location = GeometryUtils.createPoint(location.getX(), location.getY())
        return (location, None)
    return (None, "kilometro %s no encontrado en '%s'." % (pk,carretera))
  finally:
    DisposeUtils.disposeQuietly(streches)

def findOwnership(fecha, carretera, pk):
  if fecha == None or carretera == None or pk == None:
    return None
  strechesStore = getStretchFeatureStore()
  query = getVigentStretchesQuery(strechesStore, fecha) 

  expression = "matricula = '%s' and pk_i >= %s and pk_f <= %s" % (carretera, pk, pk)
  query.addFilter(expression)
  query.retrievesAllAttributes()
  feature = strechesStore.findFirst(query)
  if feature == None:
    return None
  return feature.get("titularidad")


def main(*args):
    pass
