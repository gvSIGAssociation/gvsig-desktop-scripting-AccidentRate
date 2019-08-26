# encoding: utf-8

import gvsig
from gvsig import getResource


from java.io import File
from org.gvsig.andami import PluginsLocator
from org.gvsig.app import ApplicationLocator
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.tools import ToolsLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator

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

  #
  # Creamos la accion 
  actionManager = PluginsLocator.getActionInfoManager()
  extension = AccidentRateExtension()
  
  action = actionManager.createAction(
    extension, 
    "accidentrate-importer-showimporter", # Action name
    "Importador de accidentes", # Text
    "accidentrate-importer-showimporter", # Action command
    "accidentrate-importer-showimporter", # Icon name
    None, # Accelerator
    650700600, # Position 
    "_Show_the_accidents_import_tool" # Tooltip
  )
  action = actionManager.registerAction(action)
  application.addMenu(action, "tools/CEGESEV/Importador de accidentes")
  
  action = actionManager.createAction(
    extension, 
    "accidentrate-importer-showtablecreator", # Action name
    "Creador de las tablas de accidentes", # Text
    "accidentrate-importer-showtablecreator", # Action command
    "accidentrate-importer-showtablecreator", # Icon name
    None, # Accelerator
    650700600, # Position 
    "_Show_the_accidents_tables_creator_tool" # Tooltip
  )
  action = actionManager.registerAction(action)
  application.addMenu(action, "tools/CEGESEV/Crear tablas de accidentes")

  action = actionManager.createAction(
    extension, 
    "accidentrate-closingdate-showdialog", # Action name
    "Administrar fecha de cierre", # Text
    "accidentrate-closingdate-showdialog", # Action command
    "accidentrate-closingdate-showdialog", # Icon name
    None, # Accelerator
    650700600, # Position 
    "_Show_the_accidents_closing_date_tool" # Tooltip
  )
  action = actionManager.registerAction(action)
  application.addMenu(action, "tools/CEGESEV/Fecha de cierre")

def main(*args):
  selfRegister()
  
