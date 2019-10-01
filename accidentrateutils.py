# encoding: utf-8

import gvsig

from gvsig import getResource

import os.path
from ConfigParser import SafeConfigParser

from java.io import File

from org.gvsig.fmap.dal.store.jdbc import JDBCServerExplorerParameters 
from org.gvsig.fmap.dal import DALLocator
from org.gvsig.scripting import ScriptingLocator

"""

* Carreteras
  - Repasar codigo asociado a forms
  - Los puntos no estan en su sitio.
  - Filtro en la importacion y fix

Transformaviones


report List<Incidencia>

Regla 
- execute(report)
- fix(params)
- getparameters

Inicdencia
 - fr
 - regla 
 - mensaje
 - applyfix
"""
def getDataFolder():
  return ScriptingLocator.getManager().getDataFolder("CEGESEV").getAbsolutePath()

class AccidentRateConfig(SafeConfigParser):
  def __init__(self):
    SafeConfigParser.__init__(self)

  def readConfig(self):
    fname = os.path.join(getDataFolder(),"accidentrate.cfg")
    self.read(fname)
    if not self.has_section("ARENA2"):
      self.add_section("ARENA2")
    if not self.has_option("ARENA2","alreadyDisabled"):
      self.set("ARENA2","alreadyDisabled","false")
      with open(fname, 'wb') as configfile:
        self.write(configfile)
  
  def writeConfig(self):
    fname = os.path.join(getDataFolder(),"accidentrate.cfg")
    with open(fname, 'wb') as configfile:
      self.write(configfile)

def disableArena2():
  manager = ScriptingLocator.getManager()
  fname = getResource(__file__, "..", "Arena2Importer","autorun.py")
  script = manager.getScript(File(fname))
  script.setEnabled(False)
  script.save()

def addArena2Workspace():
  dataManager = DALLocator.getDataManager()
  pool = dataManager.getDataServerExplorerPool()

  for entry in pool:
      if isinstance(entry.getExplorerParameters(), JDBCServerExplorerParameters):
        if entry.getName()=="ARENA2_DB":
          workspace = dataManager.createDatabaseWorkspaceManager(entry.getExplorerParameters())
          if workspace.isValidStoresRepository():
            dataManager.addDatabaseWorkspace(workspace)
          break

def main(*args):
  #addArena2Workspace()
  pass
  
  
