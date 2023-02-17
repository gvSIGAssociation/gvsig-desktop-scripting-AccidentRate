# encoding: utf-8

import gvsig

import sys
import java.lang.Exception
import java.lang.Throwable

from java.lang import RuntimeException
from addons.Arena2Importer.postprocess.postprocess import PostProcess, PostProcessFactory
from gvsig import logger, LOGGER_WARN, LOGGER_ERROR
from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from org.gvsig.tools.dispose import DisposeUtils
from org.gvsig.fmap.dal.feature import FeatureStore
from org.gvsig.fmap.dal import DALLocator, DataTransaction


class DeleteDeregisteredAccidents(PostProcess):

  def __init__(self, factory, workspace, expressionFilter, status):
    PostProcess.__init__(self, factory)
    self.workspace = workspace
    self.expressionFilter = expressionFilter
    self.status = status

  def execute(self):
    trans = None
    try:
      repo = self.workspace.getStoresRepository()
      accidentesStore = repo.getStore("ARENA2_ACCIDENTES")
      accidentesBajaStore = repo.getStore("SIGCAR_ACCIDENTES_BAJA")
      dataManager = DALLocator.getDataManager()
      trans = dataManager.createTransaction()
      trans.begin()
      trans.add(accidentesStore)
      trans.add(accidentesBajaStore)
      accidentes = accidentesStore.getFeatureSet('"ESTADO_ACCIDENTE"=2')
      trans.add(accidentes)
      self.status.setRangeOfValues(0,accidentes.getSize())
      self.status.setCurValue(0)
      accidentesBajaStore.edit(FeatureStore.MODE_APPEND)
      accidentesStore.edit()
      for accidente in accidentes:
        idAccidente = accidente.get("ID_ACCIDENTE")
        if self.status.isCancellationRequested():
          self.status.cancel()
          trans.abort()
          return
        baja = accidentesBajaStore.createNewFeature();
        baja.set("ACCB_ACCIDENTE_ID", idAccidente)
        informe = accidente.getForeignFeature("COD_INFORME")
        if informe == None:
          logger("Accidente %s sin informe"%idAccidente, LOGGER_WARN)
          raise RuntimeException("Accidente %s sin informe"%idAccidente)
        baja.set("ACCB_FECHA_BAJA", informe.get("FECHA_INI_EXPORT"))
        baja.set("ACCB_DATOS",accidente.toJson({"mode":5})) # TOJSON_MODE_DEEP + TOJSON_MODE_COLLECTIONS
        accidentesBajaStore.insert(baja)
        self.deleteChilds(idAccidente)
        accidentes.delete(accidente)
        self.status.incrementCurrentValue()
      trans.commit()
    except java.lang.Throwable, ex:
      logger("Error registrando como de baja accidentes.", LOGGER_WARN, ex)
      DataTransaction.rollbackQuietly(trans)
      self.status.message("Error registrando como de baja accidentes (%s)" % str(ex))
      self.status.abort()
      raise ex
    except:
      logger("Error registrando como de baja accidentes.")
      ex = sys.exc_info()[1]
      logger("Error registrando como de baja accidentes. " + str(ex), gvsig.LOGGER_WARN, ex)
      DataTransaction.rollbackQuietly(trans)
      self.status.message("Error transformando accidentes (%s)" % str(ex))
      self.status.abort()
      raise ex
    finally:
      DisposeUtils.disposeQuietly(trans)
      

  def deleteChilds(self, accidentId):
    server = self.workspace.getServerExplorer()
    params = server.getOpenParameters()
    for tableName in (
      "ARENA2_PEATONES", 
      "ARENA2_PASAJEROS", 
      "ARENA2_CONDUCTORES", 
      "ARENA2_VEHICULOS"):      
      builder = server.createSQLBuilder()
      delete = builder.delete()
      delete.table().database(params.getDBName()).schema(params.getSchema()).name(tableName)
      delete.where().and(delete.where().eq(
              builder.column("ID_ACCIDENTE"),
              builder.expression().constant(accidentId)
      ))
      sql = delete.toString()
      server.execute(sql)
    DisposeUtils.dispose(server)


class DeleteDeregisteredAccidentsFactory(PostProcessFactory):
  
  def __init__(self):
    PostProcessFactory.__init__(self,"[GVA] Borrado de accidentes dados de baja")
    
  def create(self, workspace, expressionFilter, status):
    rule = DeleteDeregisteredAccidents(self, workspace, expressionFilter, status)
    return rule

  def isSelectedByDefault(self):
    return True

def selfRegister():
  manager = getArena2ImportManager()
  manager.addPostProcessFactory(DeleteDeregisteredAccidentsFactory())

def main(*args):
  pass
