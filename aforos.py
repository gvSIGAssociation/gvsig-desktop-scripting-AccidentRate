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
from org.gvsig.tools.dataTypes import DataTypeUtils

class MedidasAforosFeatureStoreCache(CachedValue):
  def reload(self):
    dataManager = DALLocator.getDataManager()
    repo = dataManager.getStoresRepository().getSubrepository("ARENA2_DB")
    self.setValue(repo.getStore("SIGCAR_MEDIDAS_AFORO"))


medidasAforoFeatureStore = MedidasAforosFeatureStoreCache(5000);

def getMedidasAforoFeatureStore():
  return medidasAforoFeatureStore.get()
  

def checkRequirements():
  dataManager = DALLocator.getDataManager()
  s = u""
  try:
    ws = dataManager.getDatabaseWorkspace("ARENA2_DB")
    if ws == None:
      s += u"No se ha encontrado el espacio de trabajo de ARENA2_DB.\n"
    else:
      if not ws.isConnected():
        s += u"No se está conectado a un espacio de trabajo de ARENA2_DB.\n"
      else:
        repo = ws.getStoresRepository()
        if not repo.contains("SIGCAR_MEDIDAS_AFORO") :
          s += u"No existe la tabla 'SIGCAR_MEDIDAS_AFORO' en el espacio de trabajo.\n"
  except:
    s += u"No se ha podido acceder al espacio de trabajo ARENA2_DB.\n"

  if s.strip() == "":
    return None
  return s

def getMedidasAforosQuery(store, fecha, carretera, pk):
  builder = ExpressionUtils.createExpressionBuilder()
  filtro = getMedidasAforosFilter(fecha, carretera, pk)
  #print filtro
  
  query = store.createFeatureQuery()
  query.addFilter(filtro)
  return query


def getMedidasAforosFilter(fecha, carretera, pk):
  '''
  Sería algo así como:
  - que la carretera coincida
  - que el año coincida
  
  - si no tiene rekilometraje que el pk esté entre MAFO_PK_I y MAFO_PK_F
  
  - si tiene rekilometraje 
      - si la fecha es anterior al MAFO_REKI_FECHA que el pk esté entre MAFO_PK_I y MAFO_PK_F 
      - si la fecha es igual o posterior a MAFO_REKI_FECHA que el pk esté entre MAFO_REKI_PK_I y MAFO_REKI_PK_F
   
  '''
  pk = pk * 1000 #el pk viene en km y en la tabla de aforos está en metros
  builder = ExpressionUtils.createExpressionBuilder()
  builder.and(builder.eq(builder.variable("MAFO_CARRETERA"), builder.constant(carretera)))
  builder.and(builder.eq(builder.variable("MAFO_ANO"), builder.constant(DataTypeUtils.toLocalDate(fecha).year)))
  
  builder.and(
    builder.or(
      builder.and(
        builder.or(
            builder.is_null(builder.variable("MAFO_REKI_FECHA")),
            builder.gt(builder.variable("MAFO_REKI_FECHA"), builder.date(fecha))
        ),
        builder.and(
                builder.le(builder.variable("MAFO_PK_I"), builder.constant(pk)),
                builder.gt(builder.variable("MAFO_PK_F"), builder.constant(pk))
        )
      )
      ,
      builder.and(
        builder.not_is_null(builder.variable("MAFO_REKI_FECHA")),
        builder.and(
          builder.le(builder.variable("MAFO_REKI_FECHA"), builder.date(fecha)),
          builder.and(
            builder.le(builder.variable("MAFO_REKI_PK_I"), builder.constant(pk)),
            builder.gt(builder.variable("MAFO_REKI_PK_F"), builder.constant(pk))
          )
        )
      )
    )
  )

  return builder.toString()

def iif(cond, ontrue, onfalse):
  if cond:
    return ontrue
  return onfalse
  
def findMedidaAforo(fecha, carretera, pk):
  if fecha == None or carretera == None or pk == None:
    return (None,  "Fecha%s, carretera%s o pk%s nulo" % (
        iif(fecha==None, "*",""),
        iif(carretera==None, "*",""),
        iif(pk==None, "*","")
      )
    )
  medidasAforosStore = getMedidasAforoFeatureStore()
  query = getMedidasAforosQuery(medidasAforosStore, fecha, carretera, pk) 

  try:
    query.retrievesAllAttributes()
    medidaAforo = medidasAforosStore.findFirst(query)
    #print medidaAforo
    if(medidaAforo == None):
      return (None, "kilometro %.3f no encontrado a fecha %s en '%s'." % (pk/1000,String.format("%td/%tm/%tY",fecha,fecha,fecha),carretera))
    return (medidaAforo, None)
  finally:
    pass

def main(*args):
  print checkRequirements()  

def main0(*args):
    from java.util import Date
    fecha = Date(115,9,1)
    carretera = "CV-81"
    pk = 32000
    print getMedidasAforosFilter(fecha, carretera, pk)

    #medidaAforo, msg = findMedidaAforo(fecha, carretera, pk)
    #print medidaAforo

