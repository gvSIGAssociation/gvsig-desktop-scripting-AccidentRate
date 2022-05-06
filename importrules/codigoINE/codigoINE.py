# encoding: utf-8

import gvsig
import sys
from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR

from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer
from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.AccidentRate.roadcatalog import checkRequirements
from addons.Arena2Reader.arena2readerutils import getOpenStoreParametersOfDictionaryByPath
from gvsig import getResource

      
from org.gvsig.fmap.dal import DALLocator
from org.gvsig.expressionevaluator import ExpressionUtils
from org.gvsig.tools.dynobject.DynField import RELATION_TYPE_COLLABORATION, RELATION_TYPE_AGGREGATE
from org.gvsig.tools.dataTypes import DataTypes
from org.gvsig.fmap.dal import DALLocator

from org.apache.commons.lang3 import StringUtils

import java.lang.Exception
import java.lang.Throwable
from java.lang import String, Integer

from java.lang import Throwable

from transformCodigoINE import CodigoINETransformFactory
from ruleCodigoINE import CodigoINERuleFactory
from org.gvsig.tools.dispose import DisposeUtils
import unicodedata

CODERR_CODIGO_INE_ERRONEO=1000
CODERR_CODIGO_INE_NO_ENCONTRADO=1001
CODERR_CODIGO_INE_PROV_ERRONEO=1002
CODERR_CODIGO_INE_PROV_NO_ENCONTRADO=1003
CODERR_CODIGO_INE_MUNI_ERRONEO=1004
CODERR_CODIGO_INE_MUNI_NO_ENCONTRADO=1005
CODERR_CODIGO_INE_PROV_MUNI_ERRONEO=1006
CODERR_CODIGO_INE_PROV_MUNI_NO_ENCONTRADO=1007


def add_attribute_INE_PROVINCIA(ft):
    attr = ft.add("INE_PROVINCIA",4)
    attr.setSize(10)
    attr.setAllowIndexDuplicateds(True)
    attr.setAllowNull(True)
    attr.setDataProfileName(None)
    attr.setDescription(u'INE_PROVINCIA')
    attr.setGroup(None)
    attr.setHidden(False)
    attr.setIsAutomatic(False)
    attr.setIsIndexAscending(True)
    attr.setIsIndexed(True)
    attr.setIsPrimaryKey(False)
    attr.setIsReadOnly(False)
    attr.setIsTime(False)
    attr.setLabel(u'_INE_Provincia')
    attr.setOrder(140)
    attr.setPrecision(0)
    attr.setReadOnly(False)
    attr.setRelationType(RELATION_TYPE_COLLABORATION)
    attr.getForeingKey().setCodeName(u'PROV_INE')
    attr.getForeingKey().setForeingKey(True)
    attr.getForeingKey().setLabelFormula(u"FORMAT('%02d - %s',PROV_INE,PROVINCIA)")
    attr.getForeingKey().setClosedList(True)
    attr.getForeingKey().setTableName(u'ARENA2_DIC_INE_PROVINCIA')
    
def add_attribute_INE_MUNICIPIO(ft):
    attr = ft.add("INE_MUNICIPIO",4)
    attr.setSize(10)
    attr.setAllowIndexDuplicateds(True)
    attr.setAllowNull(True)
    attr.setDataProfileName(None)
    attr.setDescription(u'INE_MUNICIPIO')
    attr.setGroup(None)
    attr.setHidden(False)
    attr.setIsAutomatic(False)
    attr.setIsIndexAscending(True)
    attr.setIsIndexed(True)
    attr.setIsPrimaryKey(False)
    attr.setIsReadOnly(False)
    attr.setIsTime(False)
    attr.setLabel(u'_INE_Municipio')
    attr.setOrder(140)
    attr.setPrecision(0)
    attr.setReadOnly(False)
    attr.setRelationType(RELATION_TYPE_COLLABORATION)
    attr.getForeingKey().setCodeName(u'MUN_INE')
    attr.getForeingKey().setForeingKey(True)
    attr.getForeingKey().setLabelFormula(u"FORMAT('%02d - %s',MUN_INE,MUNICIPIO)")
    attr.getForeingKey().setClosedList(True)
    attr.getForeingKey().setTableName(u'ARENA2_DIC_INE_MUNICIPIO')

def createTableAndFill(workspace, tableName):
      # Create table
      #self.status.message("Creando "+tableName)
      #self.status.incrementCurrentValue()
      server = workspace.getServerExplorer()
      
      fname = getResource(__file__,"data", tableName+".csv")
            
      if fname == None:
        return
      parameters = getOpenStoreParametersOfDictionaryByPath(fname)
      addparams = server.getAddParameters(tableName)
      ft = addparams.getDefaultFeatureType()
      dataManager = DALLocator.getDataManager()
      store = dataManager.openStore(parameters.getProviderName(),parameters)
      ft.copyFrom(store.getDefaultFeatureType())
      store.dispose()
      server.add(tableName, addparams, False)

      # Fill table
      #self.status.message("Importando "+tableName)
      #self.status.incrementCurrentValue()

      params_src = getOpenStoreParametersOfDictionaryByPath(fname)
      params_dst = server.get(tableName)
      store_src = dataManager.openStore(params_src.getProviderName(),params_src)
      store_dst = dataManager.openStore(params_dst.getProviderName(),params_dst)
      store_src.copyTo(store_dst)
      store_src.dispose()
      store_dst.dispose()


def updateTableWorkspace(workspace, tableName):
      params = workspace.getServerExplorer().get(tableName)
      workspace.writeStoresRepositoryEntry(tableName, params)


def selfConfigureCodigoINE(ws): #workspace
    #ws = self.getWorkspace()
    server = ws.getServerExplorer()

    # Tables to configure
    tables_to_configure = ["ARENA2_DIC_INE_MUNICIPIO", "ARENA2_DIC_INE_PROVINCIA", "ARENA2_TR_INE_PROVINCIA", "ARENA2_TR_INE_MUNICIPIO"]

    for table_to_configure in tables_to_configure:
      if not server.exists(server.get(table_to_configure)):
        createTableAndFill(ws, table_to_configure)
        
      if not ws.exists(table_to_configure):
        updateTableWorkspace(ws, table_to_configure)

    # Fields to add
    accidentesParameters = server.get("ARENA2_ACCIDENTES")
    dataManager = DALLocator.getDataManager()
    store = dataManager.openStore(accidentesParameters.getProviderName(),accidentesParameters)
    ft = store.getDefaultFeatureType()
    eft = None #store.getDefaultFeatureType().getEditable()
    if ft.get("INE_PROVINCIA")==None: 
      if not store.isEditing():
        store.edit()
      if eft==None: 
        eft = store.getDefaultFeatureType().getEditable()
      add_attribute_INE_PROVINCIA(eft)
    if ft.get("INE_MUNICIPIO")==None:
      if not store.isEditing():
        store.edit()
      if eft==None: 
        eft = store.getDefaultFeatureType().getEditable()
      add_attribute_INE_MUNICIPIO(eft)
    if eft!=None:
      store.update(eft)
    if store.isEditing():
      store.finishEditing()
    DisposeUtils.dispose(store)




class FixCodigoINEProvErrorAction(RuleFixer):
  def __init__(self):
    RuleFixer.__init__(self, "FixCodigoINEProvError", "Arregla el codigo INE de la provincia", True)

  def fix(self,feature, issue):
    ft = feature.getStore().getDefaultFeatureType()
    if ft.get("COD_PROVINCIA") == None or ft.get("INE_PROVINCIA") == None:
      return
    ineCodP=issue.get("INE_PROVINCIA")
    feature["INE_PROVINCIA"]=ineCodP


class FixCodigoINEMuniErrorAction(RuleFixer):
  def __init__(self):
    RuleFixer.__init__(self, "FixCodigoINEMuniError", "Arregla el codigo INE del municipio", True)

  def fix(self,feature, issue):
    ft = feature.getStore().getDefaultFeatureType()
    if ft.get("COD_MUNICIPIO") == None or ft.get("INE_MUNICIPIO") == None:
      return
    ineCodM=issue.get("INE_MUNICIPIO")
    feature["INE_MUNICIPIO"]=ineCodM

class FixCodigoINEProvMuniErrorAction(RuleFixer):
  def __init__(self):
    RuleFixer.__init__(self, "FixCodigoINEProvMuniError", "Arregla el codigo INE de la provincia y municipio", True)

  def fix(self,feature, issue):
    ft = feature.getStore().getDefaultFeatureType()
    if ft.get("COD_PROVINCIA") == None or ft.get("INE_PROVINCIA") == None or ft.get("COD_MUNICIPIO") == None or ft.get("INE_MUNICIPIO") == None:
      return
    ineCodP=issue.get("INE_PROVINCIA")
    ineCodM=issue.get("INE_MUNICIPIO")
    feature["INE_PROVINCIA"]=ineCodP
    feature["INE_MUNICIPIO"]=ineCodM

      
def selfRegister():

  manager = getArena2ImportManager()
  manager.addTransformFactory(CodigoINETransformFactory())
  manager.addRuleFactory(CodigoINERuleFactory())
  manager.addRuleFixer(FixCodigoINEProvErrorAction())
  manager.addRuleFixer(FixCodigoINEMuniErrorAction())
  manager.addRuleFixer(FixCodigoINEProvMuniErrorAction())
  manager.addRuleErrorCode(
    CODERR_CODIGO_INE_NO_ENCONTRADO,
    "%s - Codigo INE no encontrado" % CODERR_CODIGO_INE_NO_ENCONTRADO
  )
  manager.addRuleErrorCode(
    CODERR_CODIGO_INE_ERRONEO,
    "%s - Codigo INE erroneo" % CODERR_CODIGO_INE_ERRONEO
  )


  manager.addReportAttribute("INE_PROVINCIA", Integer, size=02, label="Codigo INE Provincia propuesto", isEditable=True)
  manager.addReportAttribute("INE_MUNICIPIO", Integer, size=05, label="Codigo INE Municipio propuesto", isEditable=True)
  manager.addReportAttribute("PPROVINCIA", String, size=100, label="Provincia propuesto", isEditable=True)
  manager.addReportAttribute("PMUNICIPIO", String, size=100, label="Municipio propuesto", isEditable=True)
  
def main(*args):
  
  print "h"