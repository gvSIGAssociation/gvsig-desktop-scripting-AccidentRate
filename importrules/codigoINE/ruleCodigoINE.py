# encoding: utf-8

import gvsig
import sys
from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR

import unicodedata

from addons.AccidentRate.importrules.codigoINE import codigoINE

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
from addons.AccidentRate.importrules.codigoINE import codigoINE

###
### RULE
###

class CodigoINERule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    self.workspace = args.get("workspace",None)
    self.repo = self.workspace.getStoresRepository()

  def selfConfigure(self, ws): #, explorer):
    codigoINE.selfConfigureCodigoINE(ws)
    
  def execute(self, report, feature):
    try:
      ft = feature.getStore().getDefaultFeatureType()
      if ft.get("COD_PROVINCIA") == None or ft.get("COD_MUNICIPIO") == None:
        return
        
      if ft.get("INE_PROVINCIA") == None or ft.get("INE_MUNICIPIO") == None:
        self.preprocess( report, feature)
      if ft.get("INE_PROVINCIA") != None and ft.get("INE_MUNICIPIO") != None:
        self.postprocess( report, feature)

    except:
      ex = sys.exc_info()[1]
      logger("Error al ejecutar la regla codigo INE, " + str(ex), gvsig.LOGGER_WARN, ex)
      return

  def preprocess (self, report, feature):
    try:
      prov=feature.get("COD_PROVINCIA")
      storeP = self.repo.getStore("ARENA2_TR_INE_PROVINCIA")
      mun=feature.get("COD_MUNICIPIO")
      storeM = self.repo.getStore("ARENA2_TR_INE_MUNICIPIO")

      logger(prov)
      logger(mun)

      builder = ExpressionUtils.createExpressionBuilder()
      expression = builder.eq(builder.lower(builder.variable("PROVINCIA")), builder.lower(builder.constant(prov))).toString()
      provData = storeP.findFirst(expression)
      storeP.dispose()

      builder = ExpressionUtils.createExpressionBuilder()
      expression = builder.eq(builder.lower(builder.variable("MUNICIPIO")), builder.lower(builder.constant(mun))).toString()
      munData = storeM.findFirst(expression)
      storeM.dispose()
      
      if provData != None and munData != None: # Si existe un resultado con equivalencia directa lo trata la transformacion
        return
        
      elif provData == None and munData != None:
        report.add(
          feature.get("ID_ACCIDENTE"), 
          CODERR_CODIGO_INE_NO_ENCONTRADO,
          "Imposible asignar el codigo INE de la provincia "+str(prov),
          fixerID="IgnoreCodigoINEError",
          selected=False,
          INE_PROVINCIA=None,
          PPROVINCIA=None,
          INE_MUNICIPIO=munData.get("MUN_INE"),
          PMUNICIPIO=munData.get("MUNICIPIO")
        )
        
      elif provData != None and munData == None:
        report.add(
          feature.get("ID_ACCIDENTE"), 
          CODERR_CODIGO_INE_NO_ENCONTRADO,
          "Imposible asignar el codigo INE del municipio "+ str(mun),
          fixerID="IgnoreCodigoINEError",
          selected=False,
          INE_PROVINCIA=provData.get("PROV_INE"),
          PPROVINCIA=provData.get("PROVINCIA"),
          INE_MUNICIPIO=None,
          PMUNICIPIO=None
        )
        
      else:
        report.add(
          feature.get("ID_ACCIDENTE"), 
          CODERR_CODIGO_INE_NO_ENCONTRADO,
          "Imposible asignar el codigo INE de la provincia "+str(prov)+" y el municipio "+ str(mun),
          fixerID="IgnoreCodigoINEError",
          selected=False,
          INE_PROVINCIA=None,
          PPROVINCIA=None,
          INE_MUNICIPIO=None,
          PMUNICIPIO=None
        )

    except:
      ex = sys.exc_info()[1]
      logger("Error al ejecutar la regla codigo INE (Antes de la importacion)" + str(ex), gvsig.LOGGER_WARN, ex)
      return

  def postprocess (self, report, feature):
    try:
      #COMPROBAR SI ESTAN VACIOS
      if feature.get("INE_PROVINCIA") == None: 
        prov=feature.get("COD_PROVINCIA")
        storeP = self.repo.getStore("ARENA2_TR_INE_PROVINCIA")

        possibleProvData=self.possibleProv(prov, storeP)

        if possibleProvData["possible"]:
          report.add(
            feature.get("ID_ACCIDENTE"), 
            CODERR_CODIGO_INE_PROVINCIA_NO_ENCONTRADO,
            "No se ha podido asignar el codigo INE de la provincia "+ str(prov),
            fixerID="IgnoreCodigoINEError",
            selected=False,
            INE_PROVINCIA=possibleProvData["INEProv"],
            PPROVINCIA=possibleProvData["Prov"]
          )
        storeP.dispose()
        
      if feature.get("INE_MUNICIPIO") == None:
        mun=feature.get("COD_MUNICIPIO")
        storeM = self.repo.getStore("ARENA2_TR_INE_MUNICIPIO")

        possibleMunData=self.possibleMun(mun, storeM)

        if possibleMunData["possible"]:
          report.add(
            feature.get("ID_ACCIDENTE"), 
            CODERR_CODIGO_INE_MUNICIPIO_NO_ENCONTRADO,
            "No se ha podido asignar el codigo INE del municipio "+ str(mun),
            fixerID="IgnoreCodigoINEError",
            selected=False,
            INE_MUNICIPIO=possibleMunData["INEMun"],
            PMUNICIPIO=possibleMunData["Mun"]
          )
        storeM.dispose()

      #COMPROBAR SI ESTAN BIEN 
      if feature.get("INE_PROVINCIA") != None:
        prov=feature.get("COD_PROVINCIA")
        ineProv=feature.get("INE_PROVINCIA")
        storeP = self.repo.getStore("ARENA2_TR_INE_PROVINCIA")

        builder = ExpressionUtils.createExpressionBuilder()
        expression = builder.eq(builder.lower(builder.variable("PROV_INE")), builder.lower(builder.constant(ineProv))).toString()
        provData = storeP.findFirst(expression)
        if provData == None:

          possibleProvData=self.possibleProv(prov, storeP)

          if possibleProvData["possible"]:
            report.add(
              feature.get("ID_ACCIDENTE"), 
              CODERR_CODIGO_INE_PROVINCIA_ERRONEO,
              "El codigo INE de la provincia "+str(prov)+" es erroneo ",
              fixerID="IgnoreCodigoINEError",
              selected=False,
              INE_PROVINCIA=possibleProvData["INEProv"],
              PPROVINCIA=possibleProvData["Prov"]
            )

        expression = builder.eq(builder.lower(builder.variable("PROVINCIA")), builder.lower(builder.constant(prov))).toString()
        provData = storeP.findFirst(expression)
        if provData.get("PROV_INE") != ineProv:

          possibleProvData=self.possibleProv(prov, storeP)

          if possibleProvData["possible"]:
            report.add(
              feature.get("ID_ACCIDENTE"), 
              CODERR_CODIGO_INE_PROVINCIA_ERRONEO,
              "El codigo INE de la provincia "+str(prov)+" es erroneo ",
              fixerID="IgnoreCodigoINEError",
              selected=False,
              INE_PROVINCIA=possibleProvData["INEProv"],
              PPROVINCIA=possibleProvData["Prov"]
            )
          storeP.dispose()

      if feature.get("INE_MUNICIPIO") != None:
        mun=feature.get("COD_MUNICIPIO")
        ineMun=feature.get("INE_MUNICIPIO")
        storeM = self.repo.getStore("ARENA2_TR_INE_MUNICIPIO")

        builder = ExpressionUtils.createExpressionBuilder()
        expression = builder.eq(builder.lower(builder.variable("MUN_INE")), builder.lower(builder.constant(ineMun))).toString()
        munData = storeM.findFirst(expression)
        if munData == None:

          possibleMunData=self.possibleMun(mun, storeM)

          if possibleMunData["possible"]:
            report.add(
              feature.get("ID_ACCIDENTE"), 
              CODERR_CODIGO_INE_MUNICIPIO_ERRONEO,
              "El codigo INE del municipio "+str(mun)+" es erroneo ",
              fixerID="IgnoreCodigoINEError",
              selected=False,
              INE_MUNICIPIO=possibleMunData["INEMun"],
              PMUNICIPIO=possibleMunData["Mun"]
            )

        expression = builder.eq(builder.lower(builder.variable("MUNICIPIO")), builder.lower(builder.constant(mun))).toString()
        munData = storeM.findFirst(expression)
        if munData.get("MUN_INE") != ineMun:

          possibleMunData=self.possibleMun(mun, storeM)

          if possibleMunData["possible"]:
            report.add(
              feature.get("ID_ACCIDENTE"), 
              CODERR_CODIGO_INE_MUNICIPIO_ERRONEO,
              "El codigo INE del municipio "+str(mun)+" es erroneo ",
              fixerID="IgnoreCodigoINEError",
              selected=False,
              INE_MUNICIPIO=possibleMunData["INEMun"],
              PMUNICIPIO=possibleMunData["Mun"]
            )
        storeM.dispose()
      else:
        return

    except:
      ex = sys.exc_info()[1]
      logger("Error al ejecutar la regla codigo INE (Despues de la importacion)" + str(ex), gvsig.LOGGER_WARN, ex)
      return

  def possibleProv (self, prov, storeP):
    possibleProvData={}
    possibleProvData["possible"]=False
    jDMaxP=0
    
    provOptions=prov.split("/")
    provOptions.append(prov)
    for i in provOptions:
      builder = ExpressionUtils.createExpressionBuilder()
      expression = builder.eq(builder.lower(builder.variable("PROVINCIA")), builder.lower(builder.constant(i))).toString()
      provData = storeP.findFirst(expression)
      if provData == None:
        for j in storeP:
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
            logger("El campo provincia "+str(prov)+" o el campo "+str(j.get("PROVINCIA"))+" del diccionario tienen problemas", LOGGER_WARN) #CAMBIAR
            continue

    return possibleProvData

  def possibleMun (self, mun, storeM):
    possibleMunData={}
    possibleMunData["possible"]=False
    jDMaxM=0
    
    munOptions=mun.split("/")
    munOptions.append(mun)
    for i in munOptions:
      builder = ExpressionUtils.createExpressionBuilder()
      expression = builder.eq(builder.lower(builder.variable("MUNICIPIO")), builder.lower(builder.constant(i))).toString()
      munData = storeM.findFirst(expression)
      if munData == None:
        for j in storeM:
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
            logger("El campo municipio "+str(mun)+" o el campo "+str(j.get("MUNICIPIO"))+" del diccionario tienen problemas", LOGGER_WARN) #CAMBIAR
            continue
            
    return possibleMunData

###
### RULE FACTORY
###
class CodigoINERuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,"[GVA] Fail if not add INE Code (LRS)")

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
    codigoINE.selfConfigureCodigoINE(ws)
    
def main(*args):

    #Remove this lines and add here your code

    print "hola mundo"
    pass
