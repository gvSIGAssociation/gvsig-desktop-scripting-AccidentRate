# encoding: utf-8

import gvsig

from addons.AccidentRate.aforos import findMedidaAforo, checkRequirements

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager
from addons.Arena2Importer.integrity import Transform, TransformFactory, Rule, RuleFactory, RuleFixer

from org.gvsig.fmap.dal import DALLocator
from org.gvsig.tools.dataTypes import DataTypes
from org.gvsig.tools.dispose import DisposeUtils

class AsignarMedidasAforosTransform(Transform):
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
      feature.set("COD_AFORO",None)
      return
    f, msg = findMedidaAforo(
      feature.get("FECHA_ACCIDENTE"), 
      feature.get("CARRETERA"), 
      feature.get("KM")
    )
    #print repr(f)
    if f == None:
      #print "NADA"
      feature.set("COD_AFORO",None)
    else:
      #print repr(f.get("LID_MEDIDA_AFORO"))
      feature.set("COD_AFORO", f.get("LID_MEDIDA_AFORO"))

class AsignarMedidasAforosTransformFactory(TransformFactory):
  def __init__(self):
    TransformFactory.__init__(self,"[GVA] Asignar Medidas Aforos")

  def checkRequirements(self):
    s = checkRequirements()
    if s != None:
      return self.getName()+".\nNo es posible realizar la asignacion.de medidas aforos\n"+s
    return None
    
  def create(self,  **args):
    return AsignarMedidasAforosTransform(self, **args)
    
def selfRegister():
  manager = getArena2ImportManager()
  manager.addTransformFactory(AsignarMedidasAforosTransformFactory())

  
def test():
  from java.util import Date
  try:
    dataManager = DALLocator.getDataManager()
    workspace = dataManager.getDatabaseWorkspace("ARENA2_DB")
    store = workspace.getStoresRepository().getStore("ARENA2_ACCIDENTES")
    f = store.findFirst("ID_ACCIDENTE =  '1993030000089'").getEditable()
    factory = AsignarMedidasAforosTransformFactory()
    transform = factory.create(workspace = workspace)
    transform.apply(f)
    print f.get("COD_AFORO")
    print f
  finally:
   store.dispose()
    
def main(*args):
  #selfRegister()
  test()
  
  
