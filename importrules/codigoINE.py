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
    try:
      ft = feature.getStore().getDefaultFeatureType()
      if ft.get("COD_PROVINCIA") == None or ft.get("INE_PROVINCIA") == None or ft.get("COD_MUNICIPIO") == None or ft.get("INE_MUNICIPIO") == None:
        return

      if feature.get("INE_PROVINCIA") == None or feature.get("INE_PROVINCIA") == 0:
        self.transformProv(feature)
        
      if feature.get("INE_MUNICIPIO") == None or feature.get("INE_MUNICIPIO") == 0:
        self.transformMun(feature)
        
    except:
      ex = sys.exc_info()[1]
      logger("Error importando archivos." + str(ex), gvsig.LOGGER_WARN, ex)
      return

  # Método de la transformación que actua sobre el campo COD_PROVINCIA.
  def transformProv(self, feature):
    try:
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
        feature.set("INE_PROVINCIA",provData.get("PROV_INE"))
        break
      storeP.dispose()
    except:
      ex = sys.exc_info()[1]
      logger("Error importando archivos." + str(ex), gvsig.LOGGER_WARN, ex)
      return

  # Método de la transformación que actua sobre el campo COD_MUNICIPIO.
  def transformMun(self, feature):
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
        feature.set("INE_MUNICIPIO",munData.get("MUN_INE"))
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
    
class CodigoINEErrorFixer(RuleFixer):
  def __init__(self):
    RuleFixer.__init__(self, "CodigoINEError", "Asigna el codigo INE", True)

  def fix(self,feature, issue):
    ft = feature.getStore().getDefaultFeatureType()
    if ft.get("COD_PROVINCIA") == None or ft.get("INE_PROVINCIA") == None or ft.get("COD_MUNICIPIO") == None or ft.get("INE_MUNICIPIO") == None:
      return
    ineCodP=issue.get("INE_PROVINCIA")
    ineCodM=issue.get("INE_MUNICIPIO")
    feature["INE_PROVINCIA"]=ineCodP
    feature["INE_MUNICIPIO"]=ineCodM

    print str(feature.get("INE_PROVINCIA"))
    print str(feature.get("INE_MUNICIPIO"))

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
        
      if ft.get("INE_PROVINCIA") == None or ft.get("INE_MUNICIPIO") == None:
        self.preprocess( report, feature)
      if ft.get("INE_PROVINCIA") != None and ft.get("INE_MUNICIPIO") != None:
        self.postprocess( report, feature)

    except:
      ex = sys.exc_info()[1]
      logger("Error al ejecutar la regla codigo INE, " + str(ex), gvsig.LOGGER_WARN, ex)
      return

# Método de la regla que se ejecuta al comprobar la integridad, paso previo al proceso de importación.
# Comprueba si los campos COD_PROVINCIA y COD_MUNICIPIO del accidente tienen equivalencia en las tablas ARENA2_TR_INE_PROVINCIA
# y ARENA2_TR_INE_MUNICIPIO.
  def preprocess (self, report, feature):
    try:
      prov=feature.get("COD_PROVINCIA")
      storeP = self.repo.getStore("ARENA2_TR_INE_PROVINCIA")
      mun=feature.get("COD_MUNICIPIO")
      storeM = self.repo.getStore("ARENA2_TR_INE_MUNICIPIO")

      builder = ExpressionUtils.createExpressionBuilder()
      expression = builder.eq(builder.lower(builder.variable("PROVINCIA")), builder.lower(builder.constant(prov))).toString()
      provData = storeP.findFirst(expression)
      storeP.dispose()

      expression = builder.eq(builder.lower(builder.variable("MUNICIPIO")), builder.lower(builder.constant(mun))).toString()
      munData = storeM.findFirst(expression)
      storeM.dispose()
      
      if provData != None and munData != None: # Si existe un resultado con equivalencia directa lo trata la transformacion
        return
        
      elif provData == None and munData != None: #Si el accidente no tiene una provincia equivalente pero si un municipio
        report.add(
          feature.get("ID_ACCIDENTE"), 
          CODERR_CODIGO_INE_NO_ENCONTRADO,
          "Imposible asignar el codigo INE de la provincia "+str(prov),
          fixerID="CodigoINEError",
          selected=False,
          INE_PROVINCIA=None,
          PPROVINCIA=None,
          INE_MUNICIPIO=munData.get("MUN_INE"),
          PMUNICIPIO=munData.get("MUNICIPIO")
        )
        
      elif provData != None and munData == None: #Si el accidente no tiene un municipio equivalente pero si una provincia
        report.add(
          feature.get("ID_ACCIDENTE"), 
          CODERR_CODIGO_INE_NO_ENCONTRADO,
          "Imposible asignar el codigo INE del municipio "+ str(mun),
          fixerID="CodigoINEError",
          selected=False,
          INE_PROVINCIA=provData.get("PROV_INE"),
          PPROVINCIA=provData.get("PROVINCIA"),
          INE_MUNICIPIO=None,
          PMUNICIPIO=None
        )
        
      else: #Si el accidente no tiene ni provincia ni municipio equivalente
        report.add(
          feature.get("ID_ACCIDENTE"), 
          CODERR_CODIGO_INE_NO_ENCONTRADO,
          "Imposible asignar el codigo INE de la provincia "+str(prov)+" y el municipio "+ str(mun),
          fixerID="CodigoINEError",
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

# Método de la regla que se ejecuta al comprobar la integridad de una BBDD ya importada.
# Comprueba si los campos INE_PROVINCIA y INE_MUNICIPIO del accidente estan rellenos y si su información es correcta 
# conforme a los campos COD_PROVINCIA y COD_MUNICIPIO.
  def postprocess (self, report, feature):
    try:
      prov=feature.get("COD_PROVINCIA")
      ineProv=feature.get("INE_PROVINCIA")
      storeP = self.repo.getStore("ARENA2_TR_INE_PROVINCIA")
      mun=feature.get("COD_MUNICIPIO")
      ineMun=feature.get("INE_MUNICIPIO")
      storeM = self.repo.getStore("ARENA2_TR_INE_MUNICIPIO")

      builder = ExpressionUtils.createExpressionBuilder()

      provMunEmpty=False
      provMunError=False
      
      #PASO 1.- Comprueba si los campos INE_PROVINCIA y INE_MUNICIPIO estan vacios.
      if ineProv == None and ineMun == None: # Ambos campos estan vacios

        possibleProvData=self.possibleProv(prov, storeP)
        possibleMunData=self.possibleMun(mun, storeM)


        if possibleProvData["possible"] and possibleMunData["possible"]:
          report.add(
            feature.get("ID_ACCIDENTE"), 
            CODERR_CODIGO_INE_NO_ENCONTRADO,
            "No se ha podido asignar el codigo INE de la provincia "+ str(prov)+" ni el codigo INE del municipio "+ str(mun),
            fixerID="CodigoINEError",
            selected=False,
            INE_PROVINCIA=possibleProvData["INEProv"],
            PPROVINCIA=possibleProvData["Prov"],
            INE_MUNICIPIO=possibleMunData["INEMun"],
            PMUNICIPIO=possibleMunData["Mun"]
          )
        storeP.dispose()
        provMunEmpty=True
        
      
      if ineProv == None and provMunEmpty == False: #Solo el campo INE_PROVINCIA esta vacio

        possibleProvData=self.possibleProv(prov, storeP)

        if possibleProvData["possible"]:
          report.add(
            feature.get("ID_ACCIDENTE"), 
            CODERR_CODIGO_INE_NO_ENCONTRADO,
            "No se ha podido asignar el codigo INE de la provincia "+ str(prov),
            fixerID="CodigoINEError",
            selected=False,
            INE_PROVINCIA=possibleProvData["INEProv"],
            PPROVINCIA=possibleProvData["Prov"]
          )
        storeP.dispose()
        
      if ineMun == None and provMunEmpty == False: #Solo el campo INE_MUNICIPIO esta vacio

        possibleMunData=self.possibleMun(mun, storeM)

        if possibleMunData["possible"]:
          report.add(
            feature.get("ID_ACCIDENTE"), 
            CODERR_CODIGO_INE_NO_ENCONTRADO,
            "No se ha podido asignar el codigo INE del municipio "+ str(mun),
            fixerID="CodigoINEError",
            selected=False,
            INE_MUNICIPIO=possibleMunData["INEMun"],
            PMUNICIPIO=possibleMunData["Mun"]
          )
        storeM.dispose()

      #PASO 2.- Comprueba si los campos INE_PROVINCIA y INE_MUNICIPIO son correctos conforme a los campos COD_PROVINCIA y COD_MUNICIPIO.

      if ineProv != None and ineMun != None:
        #Primero comprueba si los campos COD_PROVINCIA y COD_MUNICIPIO se corresponden con algun valor de las tablas
        # ARENA2_TR_INE_PROVINCIA y ARENA2_TR_INE_MUNICIPIO
        expressionP = builder.eq(builder.lower(builder.variable("PROVINCIA")), builder.lower(builder.constant(prov))).toString()
        expressionM = builder.eq(builder.lower(builder.variable("MUNICIPIO")), builder.lower(builder.constant(mun))).toString()
        provData = storeP.findFirst(expressionP)
        munData = storeM.findFirst(expressionM)
        if provData == None and munData == None: # Si no hay equivalencia en ningun campo lanza sugerencias
        
          possibleProvData=self.possibleProv(prov, storeP)
          possibleMunData=self.possibleMun(mun, storeM)

          if possibleProvData["possible"] and possibleMunData["possible"]:
            report.add(
              feature.get("ID_ACCIDENTE"), 
              CODERR_CODIGO_INE_ERRONEO,
              "La provincia "+str(prov)+" y el municipio "+str(mun)+" son erroneos ",
              fixerID="CodigoINEError",
              selected=False,
              INE_PROVINCIA=possibleProvData["INEProv"],
              PPROVINCIA=possibleProvData["Prov"],
              INE_MUNICIPIO=possibleMunData["INEMun"],
              PMUNICIPIO=possibleMunData["Mun"]
            )
        if provData != None and munData == None:# Si solo hay equivalencia en el campo COD_PROVINCIA 
                                                # comprueba que el codigo INE_PROVINCIA del accidente
                                                # se corresponde con el de la equivalencia de la tabla 
                                                # ARENA2_TR_INE_PROVINCIA
                                                
          if provData.get("PROV_INE") != ineProv: # No existe correspondencia, lanza sugerencias
  
            possibleProvData=self.possibleProv(prov, storeP)
            possibleMunData=self.possibleMun(mun, storeM)
  
            if possibleProvData["possible"] and possibleMunData["possible"]:
              report.add(
                feature.get("ID_ACCIDENTE"), 
                CODERR_CODIGO_INE_ERRONEO,
                "El codigo INE de la provincia "+str(prov)+" y el municipio "+str(mun)+" son erroneos ",
                fixerID="CodigoINEError",
                selected=False,
                INE_PROVINCIA=possibleProvData["INEProv"],
                PPROVINCIA=possibleProvData["Prov"],
                INE_MUNICIPIO=possibleMunData["INEMun"],
                PMUNICIPIO=possibleMunData["Mun"]
              )
          else: # Existe correspondencia, lanza sugerencias solo para el municipio
            possibleMunData=self.possibleMun(mun, storeM)

            if possibleMunData["possible"]:
              report.add(
                feature.get("ID_ACCIDENTE"), 
                CODERR_CODIGO_INE_ERRONEO,
                "El codigo INE de la provincia "+str(prov)+" es correcto pero el municipio "+str(mun)+" es erroneo ",
                fixerID="CodigoINEError",
                selected=False,
                INE_PROVINCIA=ineProv,
                PPROVINCIA=prov,
                INE_MUNICIPIO=possibleMunData["INEMun"],
                PMUNICIPIO=possibleMunData["Mun"]
              )
              
        if provData == None and munData != None: # Si solo hay equivalencia en el campo COD_MUNICIPIO 
                                                 # comprueba que el codigo INE_MUNICIPIO del accidente
                                                 # se corresponde con el de la equivalencia de la tabla 
                                                 # ARENA2_TR_INE_MUNICIPIO
                                                
        
          if munData.get("MUN_INE") != ineMun: # No existe correspondencia, lanza sugerencias
  
            possibleProvData=self.possibleProv(prov, storeP)
            possibleMunData=self.possibleMun(mun, storeM)
  
            if possibleProvData["possible"] and possibleMunData["possible"]:
              report.add(
                feature.get("ID_ACCIDENTE"), 
                CODERR_CODIGO_INE_ERRONEO,
                "La provincia "+str(prov)+" y el codigo INE del municipio "+str(mun)+" son erroneos ",
                fixerID="CodigoINEError",
                selected=False,
                INE_PROVINCIA=possibleProvData["INEProv"],
                PPROVINCIA=possibleProvData["Prov"],
                INE_MUNICIPIO=possibleMunData["INEMun"],
                PMUNICIPIO=possibleMunData["Mun"]
              )
          else: # Existe correspondencia, lanza sugerencias solo para la provincia
            possibleProvData=self.possibleProv(prov, storeP)

            if possibleProvData["possible"]:
              report.add(
                feature.get("ID_ACCIDENTE"), 
                CODERR_CODIGO_INE_ERRONEO,
                "La provincia "+str(prov)+" es erronea y el codigo INE del municipio "+str(mun)+" es correcto ",
                fixerID="CodigoINEError",
                selected=False,
                INE_PROVINCIA=possibleProvData["INEProv"],
                PPROVINCIA=possibleProvData["Prov"],
                INE_MUNICIPIO=ineMun,
                PMUNICIPIO=mun
              )
        else: # Si hay equivalencia en los dos campos comprueba la correspondencia de los codigos INE del accidente 
              # con los de los elementos correspondientes de las tablas
          if provData.get("PROV_INE") != ineProv and munData.get("MUN_INE") != ineMun: # Los codigos INE del accidente 
                                                                                       # de ambos campos no se corresponden
                                                                                       # con los de las tablas.

            possibleProvData=self.possibleProv(prov, storeP)
            possibleMunData=self.possibleMun(mun, storeM)
  
            if possibleProvData["possible"] and possibleMunData["possible"] :
              report.add(
                feature.get("ID_ACCIDENTE"), 
                CODERR_CODIGO_INE_ERRONEO,
                "El codigo INE de la provincia "+str(prov)+" y del municipio "+str(mun)+" son erroneos ",
                fixerID="CodigoINEError",
                selected=False,
                INE_PROVINCIA=possibleProvData["INEProv"],
                PPROVINCIA=possibleProvData["Prov"],
                INE_MUNICIPIO=possibleMunData["INEMun"],
                PMUNICIPIO=possibleMunData["Mun"]
              )
              
          if provData.get("PROV_INE") == ineProv and munData.get("MUN_INE") != ineMun: # Solo el codigo INE de la provincia 
                                                                                       # se corresponde

            possibleMunData=self.possibleMun(mun, storeM)
  
            if possibleMunData["possible"]:
              report.add(
                feature.get("ID_ACCIDENTE"), 
                CODERR_CODIGO_INE_ERRONEO,
                "El codigo INE de la provincia "+str(prov)+" es correcto pero el del municipio "+str(mun)+" es erroneo ",
                fixerID="CodigoINEError",
                selected=False,
                INE_PROVINCIA=ineProv,
                PPROVINCIA=prov,
                INE_MUNICIPIO=possibleMunData["INEMun"],
                PMUNICIPIO=possibleMunData["Mun"]
              )

          if provData.get("PROV_INE") != ineProv and munData.get("MUN_INE") == ineMun: # Solo el codigo INE del municipio 
                                                                                       # se corresponde

            possibleProvData=self.possibleProv(prov, storeP)
  
            if possibleProvData["possible"]:
              report.add(
                feature.get("ID_ACCIDENTE"), 
                CODERR_CODIGO_INE_ERRONEO,
                "El codigo INE de la provincia "+str(prov)+" es erroneo y el del municipio "+str(mun)+" es correcto ",
                fixerID="CodigoINEError",
                selected=False,
                INE_PROVINCIA=possibleProvData["INEProv"],
                PPROVINCIA=possibleProvData["Prov"],
                INE_MUNICIPIO=ineMun,
                PMUNICIPIO=mun
              )
            
        storeP.dispose()
        storeM.dispose()
        provMunError=True

      if feature.get("INE_PROVINCIA") != None and provMunError == False:
      
        #Primero comprueba si el campo COD_PROVINCIA se corresponde con algun valor de la tabla ARENA2_TR_INE_PROVINCIA
        expression = builder.eq(builder.lower(builder.variable("PROVINCIA")), builder.lower(builder.constant(prov))).toString()
        provData = storeP.findFirst(expression)
        if provData == None: # Si no hay equivalencia lanza una sugerencia
        
          possibleProvData=self.possibleProv(prov, storeP)

          if possibleProvData["possible"]:
            report.add(
              feature.get("ID_ACCIDENTE"), 
              CODERR_CODIGO_INE_ERRONEO,
              "La provincia "+str(prov)+" es erronea ",
              fixerID="CodigoINEError",
              selected=False,
              INE_PROVINCIA=possibleProvData["INEProv"],
              PPROVINCIA=possibleProvData["Prov"]
            )
            
        else:
          if provData.get("PROV_INE") != ineProv: # Si hay equivalencia comprueba que el codigo INE_PROVINCIA del accidente
                                                  # se corresponde con el de la equivalencia de la tabla ARENA2_TR_INE_PROVINCIA
  
            possibleProvData=self.possibleProv(prov, storeP)
  
            if possibleProvData["possible"]:
              report.add(
                feature.get("ID_ACCIDENTE"), 
                CODERR_CODIGO_INE_ERRONEO,
                "El codigo INE de la provincia "+str(prov)+" es erroneo ",
                fixerID="CodigoINEError",
                selected=False,
                INE_PROVINCIA=possibleProvData["INEProv"],
                PPROVINCIA=possibleProvData["Prov"]
              )
        storeP.dispose()

      if feature.get("INE_MUNICIPIO") != None and provMunError == False:

        #Primero comprueba si el campo COD_MUNICIPIO se corresponde con algun valor de la tabla ARENA2_TR_INE_MUNICIPIO
        expression = builder.eq(builder.lower(builder.variable("MUNICIPIO")), builder.lower(builder.constant(mun))).toString()
        munData = storeM.findFirst(expression)
        if munData == None: # Si no hay equivalencia lanza una sugerencia

          possibleMunData=self.possibleMun(mun, storeM)

          if possibleMunData["possible"]:
            report.add(
              feature.get("ID_ACCIDENTE"), 
              CODERR_CODIGO_INE_ERRONEO,
              "El municipio "+str(mun)+" es erroneo ",
              fixerID="CodigoINEError",
              selected=False,
              INE_MUNICIPIO=possibleMunData["INEMun"],
              PMUNICIPIO=possibleMunData["Mun"]
            )
        else:
          if munData.get("MUN_INE") != ineMun: # Si hay equivalencia comprueba que el codigo INE_MUNICIPIO del accidente
                                               # se corresponde con el de la equivalencia de la tabla ARENA2_TR_INE_MUNICIPIO
  
            possibleMunData=self.possibleMun(mun, storeM)
  
            if possibleMunData["possible"]:
              report.add(
                feature.get("ID_ACCIDENTE"), 
                CODERR_CODIGO_INE_ERRONEO,
                "El codigo INE del municipio "+str(mun)+" es erroneo ",
                fixerID="CodigoINEError",
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

# Método de la regla que se utiliza para aportar una sugerencia al usuario cuando el campo INE_PROVINCIA 
# del accidente esta vacio o muestra información no correcta con respecto al campo COD_PROVINCIA
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
          logger(provO)
          logger(provT)
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
      else:
        possibleProvData["Prov"]=provData.get("PROVINCIA")
        possibleProvData["INEProv"]=provData.get("PROV_INE")
        possibleProvData["possible"]=True
        return possibleProvData
        
    return possibleProvData

# Método de la regla que se utiliza para aportar una sugerencia al usuario cuando el campo INE_MUNICIPIO 
# del accidente esta vacio o muestra información no correcta con respecto al campo COD_MUNICIPIO
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
      else:
        possibleMunData["Mun"]=munData.get("MUNICIPIO")
        possibleMunData["INEMun"]=munData.get("MUN_INE")
        possibleMunData["possible"]=True
        return possibleMunData

    return possibleMunData

class CodigoINERuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,"[GVA] Fail if not add INE Code (LRS)")

  def create(self, **args):
    rule = CodigoINERule(self, **args)
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
  manager.addRuleFixer(CodigoINEErrorFixer())
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