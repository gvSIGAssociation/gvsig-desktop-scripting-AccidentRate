# encoding: utf-8

import gvsig
import sys
from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR

import unicodedata

from addons.AccidentRate.importrules.codigoINE.codigoINE import IneUtils, selfConfigureCodigoINE, CODERR_CODIGO_INE_NO_ENCONTRADO, CODERR_CODIGO_INE_PROV_NO_ENCONTRADO, CODERR_CODIGO_INE_MUNI_NO_ENCONTRADO, CODERR_CODIGO_INE_PROV_ERRONEO, CODERR_CODIGO_INE_MUNI_ERRONEO

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

###
### RULE
###

class CodigoINERule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    self.workspace = args.get("workspace",None)
    self.repo = self.workspace.getStoresRepository()
    self.ineUtils = IneUtils(self.repo)

  def selfConfigure(self, ws): #, explorer):
    selfConfigureCodigoINE(ws)
    
  def execute(self, report, feature):
    try:
      ft = feature.getStore().getDefaultFeatureType()
      if ft.get("COD_PROVINCIA") == None or ft.get("COD_MUNICIPIO") == None:
        return
        
      if ft.get("INE_PROVINCIA") == None or ft.get("INE_MUNICIPIO") == None:
        self.preprocess( report, feature)
      else:
        #if ft.get("INE_PROVINCIA") != None and ft.get("INE_MUNICIPIO") != None:
        self.postprocess( report, feature)

    except:
      ex = sys.exc_info()[1]
      logger(u"Error al ejecutar la regla codigo INE, " + ex, gvsig.LOGGER_WARN, ex)
      return

  def preprocess (self, report, feature): #process without INE fields
    try:
      prov=feature.get("COD_PROVINCIA")
      mun=feature.get("COD_MUNICIPIO")

      #logger(prov)
      #logger(mun)

      munData = self.ineUtils.findMuni(mun)
      provData = self.ineUtils.findProv(prov)
      
      if provData != None and munData != None: # Si existe un resultado con equivalencia directa lo trata la transformacion
        return
        
      elif provData == None and munData != None:
        report.add(
          feature.get("ID_ACCIDENTE"), 
          CODERR_CODIGO_INE_NO_ENCONTRADO,
          u"Imposible asignar el codigo INE de la provincia "+prov,
          fixerID="FixCodigoINEProvError",
          selected=False #,
          #INE_MUNICIPIO=munData.get("MUN_INE"),
          #PMUNICIPIO=munData.get("MUNICIPIO")
        )
        
      elif provData != None and munData == None:
        report.add(
          feature.get("ID_ACCIDENTE"), 
          CODERR_CODIGO_INE_NO_ENCONTRADO,
          u"Imposible asignar el codigo INE del municipio "+ mun,
          fixerID="FixCodigoINEMuniError",
          selected=False #,
          #INE_PROVINCIA=provData.get("PROV_INE"),
          #PPROVINCIA=provData.get("PROVINCIA")
        )
        
      else:
        report.add(
          feature.get("ID_ACCIDENTE"), 
          CODERR_CODIGO_INE_NO_ENCONTRADO,
          u"Imposible asignar los codigos INE de la provincia "+prov+u" y el municipio "+ mun,
          fixerID="FixCodigoINEProvMuniError",
          selected=False #,
          #INE_PROVINCIA=None,
          #PPROVINCIA=None,
          #INE_MUNICIPIO=None,
          #PMUNICIPIO=None
        )

    except:
      ex = sys.exc_info()[1]
      logger(u"Error al ejecutar la regla codigo INE (Antes de la importacion)" + ex, gvsig.LOGGER_WARN, ex)
      return

  def postprocess (self, report, feature): #process with INE fields
    issueProv = None
    issueINEProv = None
    issueMuni = None
    issueINEMuni = None
    try:
      #COMPROBAR SI ESTAN VACIOS
      if feature.get("INE_PROVINCIA") == None: 
        prov=feature.get("COD_PROVINCIA")

        possibleProvData=self.possibleProv(prov)

        if possibleProvData["possible"]:
          report.add(
            feature.get("ID_ACCIDENTE"), 
            CODERR_CODIGO_INE_PROV_NO_ENCONTRADO,
            u"No se ha podido asignar el codigo INE de la provincia "+ prov,
            fixerID="FixCodigoINEProvError",
            selected=True,
            INE_PROVINCIA=possibleProvData["INEProv"],
            PPROVINCIA=possibleProvData["Prov"]
          )
        
      if feature.get("INE_MUNICIPIO") == None:
        mun=feature.get("COD_MUNICIPIO")

        possibleMunData=self.possibleMun(mun)

        if possibleMunData["possible"]:
          report.add(
            feature.get("ID_ACCIDENTE"), 
            CODERR_CODIGO_INE_MUNI_NO_ENCONTRADO,
            u"No se ha podido asignar el codigo INE del municipio "+ mun,
            fixerID="FixCodigoINEMuniError",
            selected=True,
            INE_MUNICIPIO=possibleMunData["INEMun"],
            PMUNICIPIO=possibleMunData["Mun"]
          )

      #COMPROBAR SI ESTAN BIEN 
      if feature.get("INE_PROVINCIA") != None:
        prov=feature.get("COD_PROVINCIA")
        ineProv=feature.getString("INE_PROVINCIA")
        provData = self.ineUtils.findProvByINE(ineProv)
        if provData == None:

          possibleProvData=self.possibleProv(prov)

          if possibleProvData["possible"]:
            issueINEProv = report.add(
              feature.get("ID_ACCIDENTE"), 
              CODERR_CODIGO_INE_PROV_ERRONEO,
              u"El codigo INE de la provincia "+prov+u" es erroneo ",
              fixerID="FixCodigoINEProvError",
              selected=True,
              INE_PROVINCIA=possibleProvData["INEProv"],
              PPROVINCIA=possibleProvData["Prov"]
            )

        provData = self.ineUtils.findProv(prov)
        if provData != None and provData.get("PROV_INE") != ineProv:

          possibleProvData=self.possibleProv(prov)

          if possibleProvData["possible"]:
            issueProv = report.add(
              feature.get("ID_ACCIDENTE"), 
              CODERR_CODIGO_INE_PROV_ERRONEO,
              u"El codigo INE de la provincia "+prov+u" es erroneo ",
              fixerID="FixCodigoINEProvError",
              selected=True,
              INE_PROVINCIA=possibleProvData["INEProv"],
              PPROVINCIA=possibleProvData["Prov"]
            )

      if issueProv != None:
        issueProv.set("SELECTED",False)
        report.updateIssue(issueProv)
      
      if issueINEProv != None:
        issueINEProv.set("SELECTED",False)
        report.updateIssue(issueINEProv)
      
      if feature.get("INE_MUNICIPIO") != None:
        mun=feature.get("COD_MUNICIPIO")
        ineMun=feature.get("INE_MUNICIPIO")

        munData = self.ineUtils.findMuniByINE(ineMun)
        if munData == None:

          possibleMunData=self.possibleMun(mun)

          if possibleMunData["possible"]:
            issueINEMuni=report.add(
              feature.get("ID_ACCIDENTE"), 
              CODERR_CODIGO_INE_MUNI_ERRONEO,
              u"El codigo INE del municipio "+mun+u" es erroneo ",
              fixerID="FixCodigoINEMuniError",
              selected=True,
              INE_MUNICIPIO=possibleMunData["INEMun"],
              PMUNICIPIO=possibleMunData["Mun"]
            )

        munData = self.ineUtils.findMuni(mun)
        if munData != None and munData.get("MUN_INE") != ineMun:

          possibleMunData=self.possibleMun(mun)

          if possibleMunData["possible"]:
            issueMuni=report.add(
              feature.get("ID_ACCIDENTE"), 
              CODERR_CODIGO_INE_MUNI_ERRONEO,
              u"El codigo INE del municipio "+mun+u" es erroneo ",
              fixerID="FixCodigoINEMuniError",
              selected=True,
              INE_MUNICIPIO=possibleMunData["INEMun"],
              PMUNICIPIO=possibleMunData["Mun"]
            )
            
      if issueMuni != None:
        issueMuni.set("SELECTED",False)
        report.updateIssue(issueMuni)

      if issueINEMuni != None:
        issueINEMuni.set("SELECTED",False)
        report.updateIssue(issueINEMuni)

      else:
        return

    except:
      ex = sys.exc_info()[1]
      logger(u"Error al ejecutar la regla codigo INE (Despues de la importacion)" + ex, gvsig.LOGGER_WARN, ex)
      return

  def possibleProv(self, prov):
    possibleProvData={}
    possibleProvData["possible"]=False
    if prov == None:
      return possibleProvData

    jDMaxP=0
    
    provOptions=prov.split("/")
    provOptions.append(prov)
    for i in provOptions:
      provData = self.ineUtils.findProv(i)
      if provData == None:
        for j in self.ineUtils.getProvs():
          provO=unicodedata.normalize('NFKD', i).encode('ASCII', 'ignore')
          provT=j.get("PROVINCIA")
          provT=unicodedata.normalize('NFKD', provT).encode('ASCII', 'ignore')
          if isinstance(provT, basestring) and isinstance(provO, basestring):
            jaroDistance = StringUtils.getJaroWinklerDistance(provT.lower(), provO.lower())
            if jaroDistance > jDMaxP:
              jDMaxP=jaroDistance
              possibleProvData["Prov"]=j.get("PROVINCIA")
              possibleProvData["INEProv"]=j.get("PROV_INE")
              possibleProvData["possible"]=True
          else:
            logger(u"El campo provincia "+prov+u" o el campo "+j.get("PROVINCIA")+u" del diccionario tienen problemas", LOGGER_WARN) #CAMBIAR
            continue

    return possibleProvData

  def possibleMun(self, mun):
    possibleMunData={}
    possibleMunData["possible"]=False
    if mun == None:
      return possibleMunData
    jDMaxM=0
    
    munOptions=mun.split("/")
    munOptions.append(mun)
    for i in munOptions:
      munData = self.ineUtils.findMuni(i)
      if munData == None:
        for j in self.ineUtils.getMunis():
          munO=unicodedata.normalize('NFKD', i).encode('ASCII', 'ignore')
          munT=j.get("MUNICIPIO")
          munT=unicodedata.normalize('NFKD', munT).encode('ASCII', 'ignore')
          if isinstance(munT, basestring) and isinstance(munO, basestring):
            jaroDistance = StringUtils.getJaroWinklerDistance(munT.lower(), munO.lower())
            if jaroDistance > jDMaxM:
              jDMaxM=jaroDistance
              possibleMunData["Mun"]=j.get("MUNICIPIO")
              possibleMunData["INEMun"]=j.get("MUN_INE")
              possibleMunData["possible"]=True
          else:
            logger(u"El campo municipio "+mun+u" o el campo "+j.get("MUNICIPIO")+u" del diccionario tienen problemas", LOGGER_WARN) #CAMBIAR
            continue
            
    return possibleMunData

  def restart(self):
    self.ineUtils.restartMunisAndProvsCache()



###
### RULE FACTORY
###
class CodigoINERuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,"[GVA] Fail if not add INE Code")

  def create(self, **args):
    rule = CodigoINERule(self, **args)
    #print "GeocodeRuleFactory.create: ", rule
    return rule

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo es posible realizar asignar codigo INE.\n"+s
    return None
    
  def selfConfigure(self, ws): #, explorer):
    selfConfigureCodigoINE(ws)



    
def main(*args):

    #Remove this lines and add here your code

    print "hola mundo"
    pass
