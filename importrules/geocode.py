# encoding: utf-8

import gvsig

from java.lang import String, Integer, Double

from addons.AccidentRate.roadcatalog import geocodificar, checkRequirements
from addons.AccidentRate.importrules.titularidad import TITULARIDAD_AUTONOMICA
from addons.AccidentRate.roadcatalog import CODERR_CARRETERA_FECHA_O_PK_NO_INDICADOS, CODERR_CARRETERAKM_NO_ENCONTRADA, CODERR_KM_NO_ENCONTRADO, CODERR_SENTIDO_NO_VALIDO


from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer

from org.gvsig.fmap.dal import DALLocator
from org.gvsig.tools.dataTypes import DataTypes
from org.gvsig.tools.dispose import DisposeUtils

class GeocodeTransform(Transform):
  def __init__(self, factory, **args):
    Transform.__init__(self, factory)
    self.workspace = args.get("workspace",None)
    self.repo = self.workspace.getStoresRepository()
    
  def apply(self, feature, *args):
    if feature.getType().get("LID_ACCIDENTE") == None:
      # Si no es la tabla de accidentes no hacenos nada
      return
    carretera = feature.get("CARRETERA")
    if carretera in ("",None):
      feature.set("MAPA",None)
      return
    p, f, msg, errcode = geocodificar(
      feature.get("FECHA_ACCIDENTE"), 
      feature.get("CARRETERA"), 
      feature.get("KM"),
      feature.get("SENTIDO")
    )
    if p==None:
      feature.set("MAPA",None)
      feature.set("ID_TRAMO_CARRETERA", None)
    else:
      #print "GeocodeTransform.apply: update MAPA to ", p
      feature.set("MAPA",p)
      feature.set("ID_TRAMO_CARRETERA", f.get("ID_TRAMO_CARRETERA"))
    
      

class GeocodeTransformFactory(TransformFactory):
  def __init__(self):
    TransformFactory.__init__(self,"[GVA] Geocode (LRS)")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo es posible realizar la geocodificacion.\n"+s
    return None
    
  def create(self,  **args):
    return GeocodeTransform(self, **args)
    
  def selfConfigure(self, ws):
    # crear campo ID_TRAMO_CARRETERA
    server = ws.getServerExplorer()
    accidentesParameters = server.get("ARENA2_ACCIDENTES")
    dataManager = DALLocator.getDataManager()
    store = dataManager.openStore(accidentesParameters.getProviderName(),accidentesParameters)
    ft = store.getDefaultFeatureType()
    eft = None #store.getDefaultFeatureType().getEditable()
    if ft.get("ID_TRAMO_CARRETERA")==None: 
      if not store.isEditing():
        store.edit()
      if eft==None: 
        eft = store.getDefaultFeatureType().getEditable()
      add_attribute_ID_TRAMO_CARRETERA(eft)
    
    if eft!=None:
      store.update(eft)
    if store.isEditing():
      store.finishEditing()
    DisposeUtils.dispose(store)
    return
    
def add_attribute_ID_TRAMO_CARRETERA(ft):
    attr = ft.add("ID_TRAMO_CARRETERA",DataTypes.INT)
    attr.setSize(10)
    attr.setAllowIndexDuplicateds(True)
    attr.setAllowNull(True)
    attr.setDataProfileName(None)
    attr.setDescription(u'ID_TRAMO_CARRETERA')
    attr.setGroup(None)
    attr.setHidden(False)
    attr.setIsAutomatic(False)
    attr.setIsIndexAscending(True)
    attr.setIsIndexed(True)
    attr.setIsPrimaryKey(False)
    attr.setIsReadOnly(False)
    attr.setIsTime(False)
    attr.setLabel(u'_ID_TRAMO_CARRETERA')
    attr.setOrder(140)
    attr.setPrecision(0)
    attr.setReadOnly(False)
    
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
    carretera = feature.get("CARRETERA")
    calleNombre = feature.get("CALLE_NOMBRE")
    if not (calleNombre in ("",None)):
      return
    if titularidad_accidente != TITULARIDAD_AUTONOMICA:
      return
    if carretera in ("",None):
      errcode = CODERR_CARRETERA_FECHA_O_PK_NO_INDICADOS
      report.add(
        feature.get("ID_ACCIDENTE"), 
        errcode,
        "Ni carretera ni calle indicadas",
        fixerID="IgnoreGeocodeError",
        selected=True,
        CARRETERA=feature.get("CARRETERA"),
        PK=feature.get("KM"),        
        TITULARIDAD_ACCIDENTE=titularidad_accidente,
        FECHA=feature.get("FECHA_ACCIDENTE"),
        PROVINCIA=feature.get("COD_PROVINCIA")
      )      
      return
    p, f, errmsg, errcode= geocodificar(
      feature.get("FECHA_ACCIDENTE"), 
      carretera, 
      feature.get("KM"),
      feature.get("SENTIDO")
    )
    if p==None:
      report.add(
        feature.get("ID_ACCIDENTE"), 
        errcode,
        errmsg,
        fixerID="IgnoreGeocodeError",
        selected=True,
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
  manager.addRuleErrorCode(
    CODERR_CARRETERAKM_NO_ENCONTRADA,
    "%s - Carretera/km no encontrada"%CODERR_CARRETERAKM_NO_ENCONTRADA
  )
  manager.addRuleErrorCode(
    CODERR_KM_NO_ENCONTRADO,
    "%s - km no encontrado" % CODERR_KM_NO_ENCONTRADO
  )
  manager.addRuleErrorCode(
    CODERR_CARRETERA_FECHA_O_PK_NO_INDICADOS,
    "%s - Carretera, fecha o pk no indicados" % CODERR_CARRETERA_FECHA_O_PK_NO_INDICADOS
  )
  manager.addRuleErrorCode(
    CODERR_SENTIDO_NO_VALIDO,
    "%s - Sentido no valido" % CODERR_SENTIDO_NO_VALIDO
  )


  

  manager.addReportAttribute("CARRETERA",String, size=45, label="Carretera", isEditable=True)
  manager.addReportAttribute("PK",Double, label="PK", isEditable=True)
  manager.addReportAttribute("TITULARIDAD_ACCIDENTE",Integer, size=10, label="Titularidad acc.")
  manager.addReportAttribute("FECHA",String, size=45, label="Fecha")
  manager.addReportAttribute("PROVINCIA",String, size=45, label="Provincia")

  
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
    
def updateWorkspace():
  dataManager = DALLocator.getDataManager()
  ws = dataManager.getDatabaseWorkspace("ARENA2_DB")
  f = GeocodeTransformFactory()
  f.create(workspace=ws)
  f.selfConfigure(ws)

def test2():
  from java.util import Date
  try:
    dataManager = DALLocator.getDataManager()
    workspace = dataManager.getDatabaseWorkspace("ARENA2_DB")
    store = workspace.getStoresRepository().getStore("ARENA2_ACCIDENTES")
    f = store.findFirst("ID_ACCIDENTE =  '201503002000001'").getEditable()
    factory = GeocodeTransformFactory()
    transform = factory.create(workspace=workspace)
    transform.apply(f)
    print f.get("ID_TRAMO_CARRETERA")
  finally:
   store.dispose()

  
def main(*args):
  test2()
  
  ##updateWorkspace()
  #selfRegister()
  pass
  
  