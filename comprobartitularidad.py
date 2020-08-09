# encoding: utf-8

import gvsig

import os

from gvsig import getResource

from gvsig.libs.formpanel import FormPanel, FormComponent
from gvsig.commonsdialog import msgbox

from java.lang import Thread
from javax.swing import SwingUtilities

from org.gvsig.tools import ToolsLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator

from org.gvsig.fmap.dal import DALLocator
from org.gvsig.fmap.dal.swing import DALSwingLocator 
from org.gvsig.expressionevaluator import ExpressionUtils
from org.gvsig.fmap.dal.swing.AbstractDALActionFactory import AbstractDALActionContext

from org.gvsig.tools.dynform import DynFormLocator
from org.gvsig.tools.util import ToolsUtilLocator

from addons.Arena2Importer.Arena2ImportLocator import getArena2ImportManager

from org.gvsig.expressionevaluator.swing import ExpressionEvaluatorSwingLocator


class ShowFormFromIssueActionContext(AbstractDALActionContext):
  def __init__(self, panel):
    AbstractDALActionContext.__init__(self,"Arena2ImportPanelShowFormFromIssue")
    self.panel = panel

  def getStore(self):
    return self.panel.report.getStore()
    
  def getSelectedsCount(self):
    table = self.panel.tblIssues
    return table.getSelectedRowCount()

  def getFilterForSelecteds(self):
    table = self.panel.tblIssues
    n = table.getSelectedRow()
    if n<0:
      return None
    n = table.convertRowIndexToModel(n)
    ID_ACCIDENTE = table.getModel().getAccidenteId(n)
    exp = ExpressionUtils.createExpression("ID_ACCIDENTE = '%s'" % ID_ACCIDENTE)
    return exp

class ExportFromIssueActionContext(AbstractDALActionContext):
  def __init__(self, panel):
    AbstractDALActionContext.__init__(self,"Arena2ImportPanelExportFromIssue")
    self.panel = panel

  def getStore(self):
    return self.panel.report.getStore()

class ComprobarTitularidadPanel(FormPanel):
  def __init__(self, importManager):
    FormPanel.__init__(self,getResource(__file__,"comprobartitularidad.xml"))
    self.importManager = importManager
    self.taskStatusController = None    
    self.report = self.importManager.createReport()
    self.initComponents()

  def initComponents(self):
    i18n = ToolsLocator.getI18nManager()
    toolsSwingManager = ToolsSwingLocator.getToolsSwingManager()
    dataManager = DALLocator.getDataManager()
    dataSwingManager = DALSwingLocator.getSwingManager()
    taskManager = ToolsSwingLocator.getTaskStatusSwingManager()
    expSwingManager = ExpressionEvaluatorSwingLocator.getManager()
    self.btnVerAccidente.setText("")
    self.btnExportIssues.setText("")

    self.filter = expSwingManager.createExpressionPickerController(
      self.txtFilter,
      self.btnFilter,
      self.btnFilterHistory,
      self.btnFilterBookmarks
    )
    self.taskStatusController = taskManager.createTaskStatusController(
      self.lblTaskTitle,
      self.lblTaskMessage,
      self.pgbTaskProgress
    )
    self.setVisibleTaskStatus(False)

    self.tblIssues.setModel(self.report.getTableModel())
    self.report.setCellEditors(self.tblIssues)

    dataSwingManager.setStoreAction(self.btnVerAccidente, "ShowForm", True, ShowFormFromIssueActionContext(self))
    dataSwingManager.setStoreAction(self.btnExportIssues, "Export", True, ExportFromIssueActionContext(self))
    
    self.lblIssuesMessage.setText("")
    self.tblIssues.getSelectionModel().addListSelectionListener(self.issuesSelectionChanged)
    self.tblIssues.setAutoCreateRowSorter(True)
    self.btnModifyIssues.setEnabled(False)
    self.btnVerAccidente.setEnabled(False)
    self.btnExportIssues.setEnabled(False)
    
    self.setPreferredSize(800,500)

  def btnModifyIssues_click(self, *args):
    selectionModel = self.tblIssues.getSelectionModel()
    if selectionModel.isSelectionEmpty():
      return
    report = self.report
    store = report.getStore()
    ft = store.getDefaultFeatureType().getCopy()
    for attr in ft:
      isHidden = not attr.getTags().getBoolean("editable",False)
      attr.setHidden(isHidden)
      #print "%s.isHidden() %s" % (attr.getName(), isHidden)
    f = store.createNewFeature(ft,False)
    dynformManager = DynFormLocator.getDynFormManager()
    x = f.getAsDynObject()
    form = dynformManager.createJDynForm(ft)
    winManager = ToolsSwingLocator.getWindowManager()
    form.asJComponent().setPreferredSize(Dimension(400,200))
    dialog = winManager.createDialog(form.asJComponent(), "Modificar incidencias", None, winManager.BUTTONS_OK_CANCEL)
    dialog.show(winManager.MODE.DIALOG)
    if dialog.getAction() == winManager.BUTTON_OK:
      form.getValues(x)
      for row in xrange(selectionModel.getMinSelectionIndex(), selectionModel.getMaxSelectionIndex()+1):
        if selectionModel.isSelectedIndex(row):
          row = self.tblIssues.convertRowIndexToModel(row)
          issue = report.getIssue(row).getEditable()
          for attr in ft:
            if not attr.isHidden():
              issue.set(attr.getName(), f.get(attr.getName()))
          report.putIssue(row,issue)
      report.refresh()

  def issuesSelectionChanged(self, event):
    row = self.tblIssues.getSelectedRow()
    if row<0 :
      self.btnVerAccidente.setEnabled(False)
      self.btnModifyIssues.setEnabled(False)
      return 
    self.btnVerAccidente.setEnabled(True)
    self.btnModifyIssues.setEnabled(True)
    model = self.tblIssues.getModel()
    x = model.getValueAt(row,model.getColumnCount()-1)
    self.message(x)

  def setVisibleTaskStatus(self, visible):
    self.lblTaskTitle.setVisible(visible)
    self.pgbTaskProgress.setVisible(visible)
    self.lblTaskMessage.setVisible(visible)

  def message(self, s):
    self.lblIssuesMessage.setText(s)
    
def main(*args):
  p = ComprobarTitularidadPanel(getArena2ImportManager())
  p.showWindow("Comprobar titularidad")
