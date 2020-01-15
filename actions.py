# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.commonsdialog import msgbox


from java.io import File
from org.gvsig.andami import PluginsLocator
from org.gvsig.app import ApplicationLocator
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.tools import ToolsLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator

from org.gvsig.tools.swing.api.windowmanager import WindowManager

from org.gvsig.fmap.dal import DALLocator
from org.gvsig.fmap.dal.swing import DALSwingLocator 
from org.gvsig.fmap.mapcontext import MapContextLocator

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager

from addons.AccidentRate.accidentrateutils import AccidentRateConfig, disableArena2
from addons.AccidentRate.fechadecierre import FechaDeCierreDialog

class AccidentRateExtension(ScriptingExtension):
  def __init__(self):
    pass

  def canQueryByAction(self):
    return False

  def isEnabled(self,action=None):
    return True

  def isVisible(self,action=None):
    return True
    
  def execute(self,actionCommand, *args):
    actionCommand = actionCommand.lower()
    if actionCommand == "accidentrate-importer-showimporter":
      self.importData()
    elif actionCommand == "accidentrate-importer-showtablecreator":
      self.createTables()
    elif actionCommand == "accidentrate-closingdate-showdialog":
      self.closingDate()
    elif actionCommand == "accidentrate-addlayer":
      self.addAccidentsLayer()
    elif actionCommand == "accidentrate-search":
      self.showAccidentsSearch()
        
  def createTables(self):
    manager = getArena2ImportManager()
    dialog = manager.createTablestDialog()
    dialog.showWindow("Accidentes - Crear tablas de accidentes")

  def importData(self):
    manager = getArena2ImportManager()
    dialog = manager.createImportDialog()
    dialog.showWindow("Accidentes - Importar accidentes")
    
  def closingDate(self):
    dialog = FechaDeCierreDialog()
    dialog.showWindow("Accidentes - Fecha de cierre")

  def addAccidentsLayer(self):
    dataManager = DALLocator.getDataManager()
    workspace = dataManager.getDatabaseWorkspace("ARENA2_DB")
    if workspace == None:
      msgbox("Debera conectarse al espacio de trabajo de ARENA2_DB")
      return
    repo = workspace.getStoresRepository()
    store = repo.getStore("ARENA2_ACCIDENTES")
    layer = MapContextLocator.getMapContextManager().createLayer("Accidentes", store)
    gvsig.currentView().getMainWindow().getMapControl().addLayer(layer)
  
  def showAccidentsSearch(self):
    dataSwingManager = DALSwingLocator.getSwingManager()
    dataManager = DALLocator.getDataManager()
    winManager = ToolsSwingLocator.getWindowManager()
    workspace = dataManager.getDatabaseWorkspace("ARENA2_DB")
    if workspace == None:
      msgbox("Debera conectarse al espacio de trabajo de ARENA2_DB")
      return
    repo = workspace.getStoresRepository()
    store = repo.getStore("ARENA2_ACCIDENTES")
    panel = dataSwingManager.createFeatureStoreSearchPanel(store)
    winManager.showWindow(
      panel.asJComponent(), 
      "Busqueda de accidentes", 
      WindowManager.MODE.WINDOW
    )
    
def selfRegister():

  config = AccidentRateConfig()
  config.readConfig()
  if not config.getboolean("ARENA2","alreadyDisabled"):
    disableArena2()
    config.set("ARENA2","alreadyDisabled","false")
    config.writeConfig()
  
  application = ApplicationLocator.getManager()

  #
  # Registramos las traducciones
  #i18n = ToolsLocator.getI18nManager()
  #i18n.addResourceFamily("text",File(getResource(__file__,"i18n")))

  #
  # Registramos los iconos en el tema de iconos
  iconTheme = ToolsSwingLocator.getIconThemeManager().getCurrent()
  icon = File(getResource(__file__,"images","accidentrate-importer-showimporter.png")).toURI().toURL()
  iconTheme.registerDefault("scripting.AccidentRateExtension", "action", "accidentrate-importer-showimporter", None, icon)
  
  icon = File(getResource(__file__,"images","accidentrate-importer-showtablecreator.png")).toURI().toURL()
  iconTheme.registerDefault("scripting.AccidentRateExtension", "action", "accidentrate-importer-showtablecreator", None, icon)

  icon = File(getResource(__file__,"images","accidentrate-closingdate-showdialog.png")).toURI().toURL()
  iconTheme.registerDefault("scripting.AccidentRateExtension", "action", "accidentrate-closingdate-showdialog", None, icon)

  icon = File(getResource(__file__,"images","accidentrate-search.png")).toURI().toURL()
  iconTheme.registerDefault("scripting.AccidentRateExtension", "action", "accidentrate-search", None, icon)

  icon = File(getResource(__file__,"images","accidentrate-addlayer.png")).toURI().toURL()
  iconTheme.registerDefault("scripting.AccidentRateExtension", "action", "accidentrate-addlayer", None, icon)

  #
  # Creamos la accion 
  actionManager = PluginsLocator.getActionInfoManager()
  extension = AccidentRateExtension()
  
  action = actionManager.createAction(
    extension, 
    "accidentrate-importer-showtablecreator", # Action name
    "Creador de las tablas de accidentes", # Text
    "accidentrate-importer-showtablecreator", # Action command
    "accidentrate-importer-showtablecreator", # Icon name
    None, # Accelerator
    1009000901, # Position 
    "_Show_the_accidents_tables_creator_tool" # Tooltip
  )

  action = actionManager.registerAction(action)
  application.addMenu(action, u"_AccidentRate/Administration/Gesti\u00F3n de accidentes/Crear tablas de accidentes")

  action = actionManager.createAction(
    extension, 
    "accidentrate-importer-showimporter", # Action name
    "Importador de accidentes", # Text
    "accidentrate-importer-showimporter", # Action command
    "accidentrate-importer-showimporter", # Icon name
    None, # Accelerator
    1009000902, # Position 
    "_Show_the_accidents_import_tool" # Tooltip
  )
  action = actionManager.registerAction(action)
  application.addMenu(action, u"_AccidentRate/Administration/Gesti\u00F3n de accidentes/Importador de accidentes")
  
  action = actionManager.createAction(
    extension, 
    "accidentrate-closingdate-showdialog", # Action name
    "Administrar fecha de cierre", # Text
    "accidentrate-closingdate-showdialog", # Action command
    "accidentrate-closingdate-showdialog", # Icon name
    None, # Accelerator
    1009000903, # Position 
    "_Show_the_accidents_closing_date_tool" # Tooltip
  )
  action = actionManager.registerAction(action)
  application.addMenu(action, u"_AccidentRate/Administration/Gesti\u00F3n de accidentes/Fecha de cierre")

  action = actionManager.createAction(
    extension, 
    "accidentrate-search", # Action name
    "Busqueda de accidentes", # Text
    "accidentrate-search", # Action command
    "accidentrate-search", # Icon name
    None, # Accelerator
    1009000100, # Position 
    "Busqueda de accidentes" # Tooltip
  )
  action = actionManager.registerAction(action)
  application.addMenu(action, u"_AccidentRate/Gesti\u00F3n de accidentes/Busqueda de accidentes")

  action = actionManager.createAction(
    extension, 
    "accidentrate-addlayer", # Action name
    "Añadir capa de accidentes", # Text
    "accidentrate-addlayer", # Action command
    "accidentrate-addlayer", # Icon name
    None, # Accelerator
    1009000200, # Position 
    "Añadir capa de accidentes" # Tooltip
  )
  action = actionManager.registerAction(action)
  application.addMenu(action, u"_AccidentRate/Gesti\u00F3n de accidentes/A\u00F1adir capa de accidentes")

def main(*args):
  #selfRegister()
  x = AccidentRateExtension()
  x.showAccidentsSearch()
  
