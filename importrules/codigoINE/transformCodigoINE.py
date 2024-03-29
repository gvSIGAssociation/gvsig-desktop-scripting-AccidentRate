# encoding: utf-8

import gvsig
import sys
from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR

import unicodedata

from addons.AccidentRate.importrules.codigoINE.codigoINE import IneUtils, selfConfigureCodigoINE
#from addons.AccidentRate.importrules.codigoINE.codigoINE import add_attribute_INE_PROVINCIA
#from addons.AccidentRate.importrules.codigoINE.codigoINE import add_attribute_INE_MUNICIPIO

from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer
from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.AccidentRate.roadcatalog import checkRequirements

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

class CodigoINETransform(Transform):
  def __init__(self, factory, **args):
    Transform.__init__(self, factory)
    self.workspace = args.get("workspace",None)
    self.repo = self.workspace.getStoresRepository()
    self.ineUtils = IneUtils(self.repo)


  def apply(self, feature, *args):
    #mirar que tiene los campos provincia y municipio, si no los tiene return
    
    try:
      ft = feature.getStore().getDefaultFeatureType()
      if ft.get("COD_PROVINCIA") == None or ft.get("INE_PROVINCIA") == None or ft.get("COD_MUNICIPIO") == None or ft.get("INE_MUNICIPIO") == None:
        return

      if feature.get("INE_PROVINCIA") ==None or feature.get("INE_PROVINCIA") == 0:
        self.transformProv(feature)
        
      if feature.get("INE_MUNICIPIO") ==None or feature.get("INE_MUNICIPIO") == 0:
        self.transformMun(feature)
        
    except:
      ex = sys.exc_info()[1]
      logger("Error importando archivos." + str(ex), gvsig.LOGGER_WARN, ex)
      return


  def transformProv(self, feature):
    try:
      if feature.get("COD_PROVINCIA") == None:
        return
        
      prov=feature.get("COD_PROVINCIA")
      
      provOptions=prov.split("/")
      provOptions.append(prov)
      for i in provOptions:
        provData = self.ineUtils.findProv(i)
        if provData == None:
          logger("La provincia "+i+" no se encuentra en la tabla ARENA2_TR_INE_PROVINCIA" , LOGGER_INFO)
          continue
        feature.set("INE_PROVINCIA",provData.get("PROV_INE"))
        break
    except:
      ex = sys.exc_info()[1]
      logger("Error importando archivos." + str(ex), gvsig.LOGGER_WARN, ex)
      return

  def transformMun(self, feature):
    try:
      if feature.get("COD_MUNICIPIO") == None:
        return

      mun=feature.get("COD_MUNICIPIO")

      munData = self.ineUtils.findMuni(mun)
      if munData == None:
        logger("El municipio "+mun+" no se encuentra en la tabla ARENA2_TR_INE_MUNICIPIO" , LOGGER_INFO)
      else:
        feature.set("INE_MUNICIPIO",munData.get("MUN_INE"))
        logger("El municipio "+mun+" actualizado con: "+str(munData.get("MUN_INE")) , LOGGER_INFO)
      
    except:
      ex = sys.exc_info()[1]
      logger("Error importando archivos." + str(ex), gvsig.LOGGER_WARN, ex)
      return

  def restart(self):
    self.ineUtils.restartMunisAndProvsCache()
          
class CodigoINETransformFactory(TransformFactory):
  def __init__(self):
    TransformFactory.__init__(self,"[GVA] Codigo INE")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo es posible obtener los codigos INE.\n"+s
    return None

  def create(self, **args):
    return CodigoINETransform(self,**args)

  def selfConfigure(self, ws): #, explorer):
    selfConfigureCodigoINE(ws)

def updateWorkspace():
  dataManager = DALLocator.getDataManager()
  ws = dataManager.getDatabaseWorkspace("ARENA2_DB")
  f = CodigoINETransformFactory()
  f.create(workspace=ws)
  f.selfConfigure(ws)
  
def main(*args):
  #updateWorkspace()
  """
  server = ws.getServerExplorer()
  print "one:",type(server)
  toCheck = server.get("ARENA2_DIC_INE_MUNICIPIO")
  print server.exists(toCheck)
  print "done"
  """
  pass
