# encoding: utf-8

import gvsig
from java.util import Date
from java.text import DecimalFormat
from java.text import DateFormat
from java.awt import Color
from java.io import File

from gvsig.uselib import use_plugin
use_plugin("org.gvsig.lrs.app.mainplugin")


from gvsig import currentView
from gvsig import getResource
from org.gvsig.andami import PluginsLocator
from gvsig.libs.formpanel import FormPanel
from org.gvsig.fmap.geom import GeometryLocator
from org.gvsig.fmap.mapcontext import MapContextLocator
from org.gvsig.symbology import SymbologyLocator
from org.gvsig.fmap.geom import Geometry

from  java.text import SimpleDateFormat

from org.gvsig.tools.swing.api.windowmanager import WindowManager

from org.gvsig.fmap.dal import DALLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator

from org.gvsig.app.extension.AddLayer import createAddLayerDialog
from org.gvsig.expressionevaluator import ExpressionUtils

from org.gvsig.lrs.lib.api import LrsAlgorithmsLocator

from addons.AccidentRate.roadcatalog import getVigentStretchesFilter, getStretchFilter

class LocateByRoadPKAndDate(FormPanel):
  ACCIDENTRATE_LOCATE_BY_ROAD_PK_AND_DATE_GRAPHICS_ID="AccidentRateLocateByRoadPkAndDate"

  def __init__(self):
    FormPanel.__init__(self, getResource(__file__, "locatebyroadpkanddate.xml"))
    toolsSwingManager = ToolsSwingLocator.getToolsSwingManager()
    self.fechaPicker = toolsSwingManager.createDatePickerController(
      self.txtFecha,
      self.btnFecha
    )
    self.fechaPicker.set(Date())
    self.workspace = DALLocator.getDataManager().getDatabaseWorkspace('ARENA2_DB')
    if self.workspace == None:
      self.fechaPicker.setEnabled(False)
      self.txtCarretera.setEnabled(False)
      self.txtKm.setEnabled(False)
      self.txtMeters.setEnabled(False)
      self.btnLocalizar.setEnabled(False)
      self.btnCentrar.setEnabled(False)
      self.chkClear.setEnabled(False)
    self.table = self.workspace.getServerExplorer().open("SIGCAR_TRAMOS_CARRETERAS")
    if self.table == None:
      self.fechaPicker.setEnabled(False)
      self.txtCarretera.setEnabled(False)
      self.txtKm.setEnabled(False)
      self.txtMeters.setEnabled(False)
      self.btnLocalizar.setEnabled(False)
      self.btnCentrar.setEnabled(False)
      self.chkClear.setEnabled(False)


    self.setPreferredSize(450, 140)

  def btnCancelar_click(self, *e):
    self.hide()

  def btnLimpiar_click(self, *e):
    cleanLocations()
  
  def btnLocalizar_click(self, *e):
    points = []
    points = self.locate()
    view = currentView()
    self.paintPoints(view, points)
    view.refresh()

  def btnCentrar_click(self, *e):
    points = []
    points = self.locate()
    if len(points) > 0 :
      view = currentView()
      ct = self.getCT(view)
      self.paintPoints(view, points)
      geomManager = GeometryLocator.getGeometryManager();
      envelope = geomManager.createEnvelope(Geometry.SUBTYPES.GEOM2D)
      for point in points:
        p = geomManager.createFrom(point)
        if p.canBeReprojected(ct):
          p.reProject(ct)
          envelope.add(p)
      view.center(envelope)
      view.refresh()

  def getCT(self, view) :
    if view == None :
      return None
    srs = self.table.getDefaultFeatureType().getDefaultSRS();
    ct = srs.getCT(view.getProjection())
    return ct    
    
  def paintPoints(self, view, points):
    if view == None :
      return
    mapContext = view.getMapContext()
    graphics = mapContext.getGraphicsLayer()
    if(self.chkClear.isSelected()):
      graphics.removeGraphics(LocateByRoadPKAndDate.ACCIDENTRATE_LOCATE_BY_ROAD_PK_AND_DATE_GRAPHICS_ID)
    ct = self.getCT(view)
    geomManager = GeometryLocator.getGeometryManager()

    markerSymbol = getSymbol("locatePK")

    symbologyManager = SymbologyLocator.getSymbologyManager()
    textSymbol = symbologyManager.createSimpleTextSymbol()
    textSymbol.setFontSize(10)
    textSymbol.setHaloColor(view.getMapContext().getViewPort().getBackColor())
    textSymbol.setHaloWidth(2)
    textSymbol.setDrawWithHalo(True)

    carretera = self.txtCarretera.getText()
    fecha = self.fechaPicker.get()
    formato = DecimalFormat("0.000")
    for point in points:
      m = point.getCoordinateAt(2);
      km = m/1000
      textSymbol.setText(u"  "+carretera + u" [" + formato.format(km).replace(",", " + ")+u"] ("+DateFormat.getDateInstance().format(fecha)+u")")
      idMarkerSymbol = graphics.addSymbol(markerSymbol)
      idTextSymbol = graphics.addSymbol(textSymbol)
      clonedPoint = geomManager.createFrom(point)
      clonedPoint.reProject(ct);
      graphics.addGraphic(LocateByRoadPKAndDate.ACCIDENTRATE_LOCATE_BY_ROAD_PK_AND_DATE_GRAPHICS_ID, clonedPoint, idMarkerSymbol)
      graphics.addGraphic(LocateByRoadPKAndDate.ACCIDENTRATE_LOCATE_BY_ROAD_PK_AND_DATE_GRAPHICS_ID, clonedPoint, idTextSymbol)

  def locate(self):
    lrsManager = LrsAlgorithmsLocator.getLrsAlgorithmsManager()
    points = []
    fecha = None
    try:
      fecha = self.fechaPicker.get()
    except:
      return points
    carretera = self.txtCarretera.getText()
    kmStr = self.txtKm.getText()
    mStr = self.txtMeters.getText()
    m = None
    km = None
    meters = None
    try:
      km = int(kmStr)
    except:
        gvsig.commonsdialog.msgbox("'"+kmStr+u"' No es un valor válido.",
          u"Localizar tramo por PK y fecha",
          gvsig.commonsdialog.WARNING
        )
    if km and km  < 0:
      gvsig.commonsdialog.msgbox("'"+kmStr+u"' No es un valor válido.",
        u"Localizar tramo por PK y fecha",
        gvsig.commonsdialog.WARNING
      )
    try:
      meters = int(mStr)
    except:
        gvsig.commonsdialog.msgbox("'"+mStr+u"' No es un valor válido.",
          u"Localizar tramo por PK y fecha",
          gvsig.commonsdialog.WARNING
        )
    if meters and meters < 0:
      gvsig.commonsdialog.msgbox("'"+mStr+u"' No es un valor válido.",
        u"Localizar tramo por PK y fecha",
        gvsig.commonsdialog.WARNING
      )
    if fecha == None:
      gvsig.commonsdialog.msgbox(u" Por favor, introduzca una fecha.",
        u"Localizar tramo por PK y fecha",
        gvsig.commonsdialog.WARNING
      )
    
    if fecha != None and carretera and km and km>=0 and meters and meters>=0:
      m = 1000*int(kmStr)+int(mStr)
      filtro = getStretchFilter(fecha, carretera, m);
      featureSet = self.table.getFeatureSet(filtro);
      if featureSet.getSize() == 0:
        gvsig.commonsdialog.msgbox(u"No se ha podido encontrar el punto kilométrico con\n carretera "+carretera+u",\n fecha "+DateFormat.getDateInstance().format(fecha) +u",\n y punto kilométrico "+str(int(kmStr))+" + "+str(int(mStr)),
          u"Localizar tramo por PK y fecha",
          gvsig.commonsdialog.WARNING
        )
        
      itera = featureSet.iterable()
      for feature in itera:
        geometry = feature.getDefaultGeometry()
        geomType = geometry.getGeometryType()
        if not geomType.hasM():
          continue
        points.append(lrsManager.getMPointFromGeometry(geometry,float(m)))
    return points
  
  
def cleanLocations():
  view = currentView()
  if view == None :
    return
  mapContext = view.getMapContext();
  graphics = mapContext.getGraphicsLayer();
  graphics.removeGraphics(LocateByRoadPKAndDate.ACCIDENTRATE_LOCATE_BY_ROAD_PK_AND_DATE_GRAPHICS_ID)
  view.refresh()

def getSymbol(name):
  symbolManager = MapContextLocator.getSymbolManager();
  folder = File(getResource(__file__, "symbols"))
  print folder
  symbols = symbolManager.loadSymbols(folder, lambda x:str(x.getName()).lower().endswith(".gvssym"))
  for symbol in symbols:
    print symbol
    symbolId = getattr(symbol, "getID", None)
    if symbolId != None:
      print symbolId()
      if symbolId() == name:
        return symbol

  return symbolManager.createSymbol(Geometry.TYPES.POINT, Color.RED);

def main(*args):
  x = LocateByRoadPKAndDate()
  x.showWindow("Localizar tramo por PK y fecha")
  
