# encoding: utf-8

import gvsig

from addons.AccidentRate.roadcatalog import geocodificar, checkRequirements
from addons.AccidentRate.importrules.titularidad import CODERR_CARRETERAKM_NO_ENCONTRADA
from addons.AccidentRate.importrules.titularidad import CODERR_KM_NO_ENCONTRADO

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer


class GeocodeTransform(Transform):
  def __init__(self, factory):
    Transform.__init__(self, factory)

  def apply(self, feature, *args):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    p, f, msg = geocodificar(
      feature.get("FECHA_ACCIDENTE"), 
      feature.get("CARRETERA"), 
      feature.get("KM")
    )
    if p==None:
      feature.set("MAPA",None)
    else:
      #print "GeocodeTransform.apply: update MAPA to ", p
      feature.set("MAPA",p)
      feature.set("ID_TRAMO", f.get("id_tramo"))
    
      

class GeocodeTransformFactory(TransformFactory):
  def __init__(self):
    TransformFactory.__init__(self,"[GVA] Geocode (LRS)")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo es posible realizar la geocodificacion.\n"+s
    return None
    
  def create(self, *args):
    return GeocodeTransform(self)
    
class IgnoreGeocodeErrorAction(RuleFixer):
  def __init__(self):
    RuleFixer.__init__(self, "IgnoreGeocodeError", "Ignora errores de geocodificacion", True)

  def fix(self,feature, args):
    pass

class GeocodeRule(Rule):
  def __init__(self, factory, **args):
    Rule.__init__(self, factory)
    
  def execute(self, report, feature):
    #print "GeocodeRule.execute: ", self.getFactory().getName(), feature
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    titularidad_accidente = feature.get("TITULARIDAD_VIA")
    p, f, msg = geocodificar(
      feature.get("FECHA_ACCIDENTE"), 
      feature.get("CARRETERA"), 
      feature.get("KM")
    )
    if p==None:
      errcode = CODERR_CARRETERAKM_NO_ENCONTRADA
      if msg.lower().startswith("kilometro"):
        errcode = CODERR_KM_NO_ENCONTRADO
      report.add(
        feature.get("ID_ACCIDENTE"), 
        errcode,
        msg,
        fixerID="IgnoreGeocodeError",
        CARRETERA=feature.get("CARRETERA"),
        PK=feature.get("KM"),        
        TITULARIDAD_ACCIDENTE=titularidad_accidente,
        FECHA=feature.get("FECHA_ACCIDENTE"),
        PROVINCIA=feature.get("COD_PROVINCIA")
      )


class GeocodeRuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,"[GVA] Fail if not Geocode (LRS)")

  def create(self, **args):
    rule = GeocodeRule(self, **args)
    #print "GeocodeRuleFactory.create: ", rule
    return rule

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo es posible realizar la geocodificacion.\n"+s
    return None

  def isSelectedByDefault(self):
    return False

def selfRegister():
  manager = getArena2ImportManager()
  manager.addTransformFactory(GeocodeTransformFactory())
  manager.addRuleFactory(GeocodeRuleFactory())
  manager.addRuleFixer(IgnoreGeocodeErrorAction())
  manager.addRuleErrorCode(100,"100 - Carretera/km no encontrada")
  
def test():
  from java.util import Date

  transform = GeocodeTransform()
  datos = (
    { "FECHA_ACCIDENTE":Date("22/12/2018") , "CARRETERA":"CV-95" , "KM": 181 },
    { "FECHA_ACCIDENTE":Date("12/12/2018") , "CARRETERA":"CV-921" , "KM": 23 },
    { "FECHA_ACCIDENTE":Date("21/12/2018") , "CARRETERA":"CV-84" , "KM": 145 },
    { "FECHA_ACCIDENTE":Date("21/12/2018") , "CARRETERA":"N-332" , "KM": 908 },
  )
  for dato in datos:
    transform.apply(dato)
    print dato.get("MAPA",None)
      
def main(*args):
  #test()
  selfRegister()
  