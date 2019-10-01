# encoding: utf-8

import gvsig

from addons.AccidentRate.roadcatalog import geocodificar

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory

class GeocodeTransform(Transform):
  def __init__(self, factory):
    Transform.__init__(self, factory)

  def apply(self, feature, *args):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    p, msg = geocodificar(
      feature.get("FECHA_ACCIDENTE"), 
      feature.get("CARRETERA"), 
      feature.get("KM")
    )
    if p!=None:
      print "GeocodeTransform.apply: update MAPA to ", p
      feature.set("MAPA",p)
      

class GeocodeTransformFactory(TransformFactory):
  def __init__(self):
    TransformFactory.__init__(self,"Geocode (LRS)")

  def create(self, *args):
    return GeocodeTransform(self)
    

class GeocodeRule(Rule):
  def __init__(self, factory):
    Rule.__init__(self, factory)
    
  def execute(self, report, feature):
    #print "GeocodeRule.execute: ", self.getFactory().getName(), feature
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    p, msg = geocodificar(
      feature.get("FECHA_ACCIDENTE"), 
      feature.get("CARRETERA"), 
      feature.get("KM")
    )
    if p==None:
      report.add(
        feature.get("ID_ACCIDENTE"), 
        self.getName(), 
        msg
      )


class GeocodeRuleFactory(RuleFactory):
  def __init__(self):
    RuleFactory.__init__(self,"Geocode (LRS)")

  def create(self, *args):
    rule = GeocodeRule(self)
    #print "GeocodeRuleFactory.create: ", rule
    return rule

def selfRegister():
  manager = getArena2ImportManager()
  manager.addTransformFactory(GeocodeTransformFactory())
  manager.addRuleFactory(GeocodeRuleFactory())
  
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
  