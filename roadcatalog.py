# encoding: utf-8

import gvsig

from gvsig.uselib import use_plugin

use_plugin("org.gvsig.cegesev.roadcatalog.app.mainplugin")
use_plugin("org.gvsig.lrs.app.mainplugin")

from org.gvsig.tools.dispose import DisposeUtils

from org.gvsig.fmap.geom import GeometryUtils

try:
  from org.gvsig.cegesev.roadcatalog import AccidentCatalogLocator
  from org.gvsig.lrs.lib.api import LrsAlgorithmsLocator
except:
  AccidentCatalogLocator = None
  LrsAlgorithmsLocator = None

carreterasManager = None
lrsManager = None

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

def geocodificar(fecha, carretera, pk):
  if fecha == None or carretera == None or pk == None:
    return (None, "Fecha, carretera o pk nulo")
  strechesStore = getCarreterasManager().getStretchFeatureStore()
  query = getCarreterasManager().getVigentStretchesQuery(strechesStore, fecha) 

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
  strechesStore = getCarreterasManager().getStretchFeatureStore()
  query = getCarreterasManager().getVigentStretchesQuery(strechesStore, fecha) 

  expression = "matricula = '%s' and pk_i >= %s and pk_f <= %s" % (carretera, pk, pk)
  query.addFilter(expression)
  query.retrievesAllAttributes()
  feature = strechesStore.findFirst(query)
  if feature == None:
    return None
  return feature.get("titularidad")


def main(*args):
    pass
