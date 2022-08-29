# encoding: utf-8

import gvsig
from java.util import Date

from gvsig import getResource
from org.gvsig.andami import PluginsLocator
from gvsig.libs.formpanel import FormPanel

from  java.text import SimpleDateFormat

from org.gvsig.tools.swing.api.windowmanager import WindowManager

from org.gvsig.fmap.dal import DALLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator

from org.gvsig.app.extension.AddLayer import createAddLayerDialog

from addons.AccidentRate.roadcatalog import getVigentStretchesFilter

class CargaDeTramosDeCarreteras(FormPanel):
  def __init__(self):
    FormPanel.__init__(self, getResource(__file__, "cargadetramosdecarreteras.xml"))
    toolsSwingManager = ToolsSwingLocator.getToolsSwingManager()
    self.workspace = DALLocator.getDataManager().getDatabaseWorkspace('ARENA2_DB')
    self.fechaPicker = toolsSwingManager.createDatePickerController(
      self.txtFecha,
      self.btnFecha
    )
    if self.workspace == None:
      self.fechaPicker.setEnabled(False)
      self.btnAceptar.setEnabled(False)
    self.fechaPicker.set(Date())
    self.setPreferredSize(350, 100)

  def btnCancelar_click(self, *e):
    self.hide()
  
  def btnAceptar_click(self, *e):
    fecha = self.fechaPicker.get()
    if fecha != None:
      #fecha = SimpleDateFormat("dd/MM/yyyy").format(fecha)
      filtro = getVigentStretchesFilter(fecha);
      parameters = self.workspace.getStoresRepository().get("TRAMOS_CARRETERAS").getCopy();
      parameters.setBaseFilter(filtro)
      strFecha = SimpleDateFormat("dd/MM/yyyy").format(fecha)

      action = PluginsLocator.getActionInfoManager().getAction("view-layer-add")
      action.execute((
        "--ignoreVisibilityScaleCheck",
        "--dataParameters=",(parameters,),
        "--layerNames=",("TRAMOS_CARRETERAS"+"_"+strFecha,)
      ))
    
def main(*args):
  x = CargaDeTramosDeCarreteras()
  x.showWindow("Carga de capa de tramos de carreteras")
  
