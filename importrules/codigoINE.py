# encoding: utf-8

import gvsig
import sys
from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR

from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer
from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.AccidentRate.roadcatalog import checkRequirements

from org.apache.commons.lang3 import StringUtils

import java.lang.Exception
import java.lang.Throwable

from java.lang import String, Integer

from java.lang import Throwable

from org.gvsig.expressionevaluator import ExpressionUtils

import unicodedata

CODERR_CODIGO_INE_ERRONEO=1000
CODERR_CODIGO_INE_NO_ENCONTRADO=1001



class CodigoINETransform(Transform):
  def __init__(self, factory, **args):
    Transform.__init__(self, factory)
    self.workspace = args.get("workspace",None)
    self.repo = self.workspace.getStoresRepository()

  def apply(self, feature, *args):
    #mirar que tiene los campos provincia y municipio, si no los tiene return
    try:
      ft = feature.getStore().getDefaultFeatureType()
      if ft.get("COD_PROVINCIA") == None or ft.get("INE_PROVINCIA") == None or ft.get("COD_MUNICIPIO") == None or ft.get("INE_MUNICIPIO") == None:
        return
      
      if feature.get("COD_PROVINCIA") == None:
        return
      prov=feature.get("COD_PROVINCIA")
      
      storeP = self.repo.getStore("ARENA2_TR_INE_PROVINCIA")

      provOptions=prov.split("/")
      provOptions.append(prov)
      for i in provOptions:
        builder = ExpressionUtils.createExpressionBuilder()
        expression = builder.eq(builder.lower(builder.variable("PROVINCIA")), builder.lower(builder.constant(i))).toString()
        provData = storeP.findFirst(expression)
        if provData == None:
          logger("La provincia "+i+" no se encuentra en la tabla ARENA2_TR_INE_PROVINCIA" , LOGGER_INFO)
          continue
        feature.set("INE_PROVINCIA",provData.get("COD_INE"))
        break
      storeP.dispose()
    except:
      ex = sys.exc_info()[1]
      logger("Error importando archivos." + str(ex), gvsig.LOGGER_WARN, ex)
      return

    try:
      if feature.get("COD_MUNICIPIO") == None:
        return

      mun=feature.get("COD_MUNICIPIO")

      storeM = self.repo.getStore("ARENA2_TR_INE_MUNICIPIO")

      munOptions=mun.split("/")
      munOptions.append(mun)
      for j in munOptions:
        builder = ExpressionUtils.createExpressionBuilder()
        expression = builder.eq(builder.lower(builder.variable("MUNICIPIO")), builder.lower(builder.constant(j))).toString()
        munData = storeM.findFirst(expression)
        if munData == None:
          logger("El municipio "+j+" no se encuentra en la tabla ARENA2_TR_INE_MUNICIPIO" , LOGGER_INFO)
          continue
        feature.set("INE_MUNICIPIO",munData.get("COD_INE"))
        break
      storeM.dispose()
    except:
      ex = sys.exc_info()[1]
      logger("Error importando archivos." + str(ex), gvsig.LOGGER_WARN, ex)
      return


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
    
class IgnoreCodigoINEErrorAction(RuleFixer):
  def __init__(self):
    RuleFixer.__init__(self, "IgnoreCodigoINEError", "Ignora errores al obtener el codigo INE", True)

  def fix(self,feature, issue):
    ft = feature.getStore().getDefaultFeatureType()
    if ft.get("COD_PROVINCIA") == None or ft.get("INE_PROVINCIA") == None or ft.get("COD_MUNICIPIO") == None or ft.get("INE_MUNICIPIO") == None:
      return
    ineCodP=issue.get("INE_PROVINCIA")
    ineCodM=issue.get("INE_MUNICIPIO")
    feature["INE_PROVINCIA"]=ineCodP
    feature["INE_MUNICIPIO"]=ineCodM

class CodigoINERule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    self.workspace = args.get("workspace",None)
    self.repo = self.workspace.getStoresRepository()
    
  def execute(self, report, feature):
    try:
      ft = feature.getStore().getDefaultFeatureType()
      if ft.get("COD_PROVINCIA") == None or ft.get("COD_MUNICIPIO") == None:
        return
        
      if ft.get("INE_PROVINCIA") == None or ft.get("INE_MUNICIPIO") == None: #Preprocess
        #f1(self, report, feature)
        self.preprocess( report, feature)
      if ft.get("INE_PROVINCIA") != None and ft.get("INE_MUNICIPIO") != None: #Postprocess
        self.postprocess( report, feature)

    except:
      ex = sys.exc_info()[1]
      logger("Error al ejecutar la regla codigo INE, " + str(ex), gvsig.LOGGER_WARN, ex)
      return

  """
  def f1 (self, report, feature):
    try:
      prov=feature.get("COD_PROVINCIA")
      storeP = self.repo.getStore("ARENA2_DIC_INE_PROVINCIA")
  
      builder = ExpressionUtils.createExpressionBuilder()
      expression = builder.eq(builder.lower(builder.variable("PROVINCIA")), builder.lower(builder.constant(prov))).toString()
      provData = storeP.findFirst(expression)
      if provData != None:# Si existe un resultado con equivalencia directa lo trata la transformacion
        return
  
      jDMaxP=0
      provOptions=prov.split("/")
      provOptions.append(prov)
      for i in provOptions:
        logger("provOptions= "+str(i),LOGGER_WARN)
        builder = ExpressionUtils.createExpressionBuilder()
        expression = builder.eq(builder.lower(builder.variable("PROVINCIA")), builder.lower(builder.constant(i))).toString()
        provData = storeP.findFirst(expression)
        if provData == None:
          for j in storeP:
            provO=unicodedata.normalize('NFKD', i).encode('ASCII', 'ignore')
            provT=j.get("PROVINCIA")
            provT=unicodedata.normalize('NFKD', provT).encode('ASCII', 'ignore')
            provTOptions=provT.split("/")
            provTOptions.append(provT)
            for provTOption in provTOptions:
              logger("provTOption= "+str(provTOption),LOGGER_WARN)
              if isinstance(provTOption, basestring) and isinstance(provO, basestring):
                jaroDistance = StringUtils.getJaroWinklerDistance(provTOption.lower(), provO.lower())
                if jaroDistance > jDMaxP:
                  logger("jaroDistance= "+str(jaroDistance),LOGGER_WARN)
                  jDMaxP=jaroDistance
                  possibleProv=provT
                  possibleINEProv=j.get("ID")
              else:
                logger("El campo provincia o el diccionario tiene problemas", LOGGER_WARN) #CAMBIAR
                continue
        else:
          possibleProv=provData.get("PROVINCIA")
          possibleINEProv=provData.get("ID")
          break
  
      storeP.dispose()
  
      mun=feature.get("COD_MUNICIPIO")
      storeM = self.repo.getStore("ARENA2_DIC_INE_MUNICIPIO")
  
      builder = ExpressionUtils.createExpressionBuilder()
      expression = builder.eq(builder.lower(builder.variable("MUNICIPIO")), builder.lower(builder.constant(mun))).toString()
      munData = storeM.findFirst(expression)
      if munData != None: # Si existe un resultado con equivalencia directa lo trata la transformacion
        return
  
      jDMaxM=0
      munOptions=mun.split("/")
      munOptions.append(mun)
      for k in munOptions:
        logger("munOptions= "+str(k),LOGGER_WARN)
        builder = ExpressionUtils.createExpressionBuilder()
        expression = builder.eq(builder.lower(builder.variable("MUNICIPIO")), builder.lower(builder.constant(k))).toString()
        munData = storeM.findFirst(expression)
        if munData == None:
          for l in storeM:
            munO=unicodedata.normalize('NFKD', k).encode('ASCII', 'ignore')
            munT=l.get("MUNICIPIO")
            munT=unicodedata.normalize('NFKD', munT).encode('ASCII', 'ignore')
            munTOptions=munT.split("/")
            munTOptions.append(munT)
            for munTOption in munTOptions:
              logger("munTOption= "+str(munTOption),LOGGER_WARN)
              if isinstance(munTOption, basestring) and isinstance(munO, basestring):
                jaroDistance = StringUtils.getJaroWinklerDistance(munTOption.lower(), munO.lower())
                if jaroDistance > jDMaxM:
                  logger("jaroDistance= "+str(jaroDistance),LOGGER_WARN)
                  jDMaxM=jaroDistance
                  possibleMun=munT
                  possibleINEMun=l.get("COD_INE")
              else:
                logger("El campo municipio o el diccionario tiene problemas", LOGGER_WARN) #CAMBIAR
                continue
  
        else:
          possibleMun=munData.get("MUNICIPIO")
          possibleINEMun=munData.get("COD_INE")
          break
  
      storeM.dispose()
  
      report.add(
        feature.get("ID_ACCIDENTE"), 
        CODERR_CODIGO_INE_NO_ENCONTRADO,
        "Imposible asignar el codigo INE de la provincia "+str(prov)+" y el municipio "+ str(mun),
        fixerID="IgnoreCodigoINEError",
        selected=False,
        INE_PROVINCIA=possibleINEProv,
        PPROVINCIA=possibleProv,
        INE_MUNICIPIO=possibleINEMun,
        PMUNICIPIO=possibleMun
      )
  
    except:
      ex = sys.exc_info()[1]
      logger("Error al ejecutar la regla codigo INE (Antes de la importacion)" + str(ex), gvsig.LOGGER_WARN, ex)
      return

  """
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
          INE_MUNICIPIO=munData.get("COD_INE"),
          PMUNICIPIO=munData.get("MUNICIPIO")
        )
        
      elif provData != None and munData == None:
        report.add(
          feature.get("ID_ACCIDENTE"), 
          CODERR_CODIGO_INE_NO_ENCONTRADO,
          "Imposible asignar el codigo INE del municipio "+ str(mun),
          fixerID="IgnoreCodigoINEError",
          selected=False,
          INE_PROVINCIA=provData.get("COD_INE"),
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

        possibleProvData=self.pProv(prov, storeP)

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

        possibleMunData=self.pMun(mun, storeM)

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
        expression = builder.eq(builder.lower(builder.variable("COD_INE")), builder.lower(builder.constant(ineProv))).toString()
        provData = storeP.findFirst(expression)
        if provData == None:

          possibleProvData=self.pProv(prov, storeP)

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
        expression = builder.eq(builder.lower(builder.variable("COD_INE")), builder.lower(builder.constant(ineMun))).toString()
        munData = storeM.findFirst(expression)
        if munData == None:

          possibleMunData=self.pMun(mun, storeM)

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

  def pProv (self, prov, storeP):
    pProvData={}
    pProvData["possible"]=False
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
              pProvData["Prov"]=provT
              pProvData["INEProv"]=j.get("COD_INE")
              pProvData["possible"]=True
          else:
            logger("El campo provincia "+str(prov)+" o el campo "+str(j.get("PROVINCIA"))+" del diccionario tienen problemas", LOGGER_WARN) #CAMBIAR
            continue

    return pProvData

  def pMun (self, mun, storeM):
    pMunData={}
    pMunData["possible"]=False
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
              pMunData["Mun"]=munT
              pMunData["INEMun"]=j.get("COD_INE")
              pMunData["possible"]=True
          else:
            logger("El campo municipio "+str(mun)+" o el campo "+str(l.get("MUNICIPIO"))+" del diccionario tienen problemas", LOGGER_WARN) #CAMBIAR
            continue
            
    return pMunData

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

def selfRegister():
  manager = getArena2ImportManager()
  manager.addTransformFactory(CodigoINETransformFactory())
  manager.addRuleFactory(CodigoINERuleFactory())
  manager.addRuleFixer(IgnoreCodigoINEErrorAction())
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
  pass