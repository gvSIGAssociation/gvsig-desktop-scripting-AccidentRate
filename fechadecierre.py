# encoding: utf-8

import gvsig

from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

from  java.text import SimpleDateFormat

from org.gvsig.fmap.dal import DALLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator

class FechaDeCierreDialog(FormPanel):
  def __init__(self):
    FormPanel.__init__(self, getResource(__file__, "fechadecierre.xml"))

    toolsSwingManager = ToolsSwingLocator.getToolsSwingManager()

    self.workspace = DALLocator.getDataManager().getDatabaseWorkspace('ARENA2_DB')

    self.fechaPicker = toolsSwingManager.createDatePickerController(
      self.txtFechaDeCierre,
      self.btnFechaDeCierre
    )
    if self.workspace == None:
      self.fechaPicker.setEnabled(False)
      self.btnGuardar.setEnabled(False)
    else:
      fechaDeCierre = self.workspace.get('CEGESEV.accidentes.fecha_de_cierre')
      if fechaDeCierre == None:
        self.fechaPicker.set(None)
      else:
        fechaDeCierre = SimpleDateFormat("dd/MM/yyyy").parse(fechaDeCierre)
        self.fechaPicker.coerceAndSet(fechaDeCierre)

    self.setPreferredSize(350, 100)

  def btnCancelar_click(self, *e):
    self.hide()
  
  def btnGuardar_click(self, *e):
    fechaDeCierre = self.fechaPicker.get()
    if fechaDeCierre != None:
      fechaDeCierre = SimpleDateFormat("dd/MM/yyyy").format(fechaDeCierre)
    self.workspace.set('CEGESEV.accidentes.fecha_de_cierre', fechaDeCierre)
    self.hide()
    

    
def main(*args):
  x = FechaDeCierreDialog()
  x.showWindow("Accidentes - Fecha de cierre")
  
