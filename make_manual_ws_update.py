# encoding: utf-8

import gvsig

from addons.AccidentRate.importrules import geocode 
from addons.AccidentRate.importrules.codigoINE import transformCodigoINE
from org.gvsig.tools.dataTypes import DataTypes
from org.gvsig.tools.dispose import DisposeUtils
from org.gvsig.fmap.dal import DALLocator
from org.gvsig.tools.dynobject.DynField import RELATION_TYPE_COLLABORATION, RELATION_TYPE_AGGREGATE


def add_attribute_ESTADO_ACCIDENTE(ft):
  attr = ft.add("ESTADO_ACCIDENTE",4)
  attr.setSize(0)
  attr.setAllowIndexDuplicateds(False)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'ESTADO_ACCIDENTE')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Estado_accidente')
  attr.setOrder(30)
  attr.setPrecision(10)
  attr.setReadOnly(False)
  attr.setRelationType(1)
  attr.getForeingKey().setCodeName(u'ID')
  attr.getForeingKey().setForeingKey(True)
  attr.getForeingKey().setLabelFormula(u"FORMAT('%02d - %s',ID,DESCRIPCION)")
  attr.getForeingKey().setClosedList(True)
  attr.getForeingKey().setTableName(u'ARENA2_DIC_ESTADO_ACCIDENTE')
  tags = attr.getTags()
  tags.set(u'report.attr.label', u"FOREING_VALUE('ESTADO_ACCIDENTE.DESCRIPCION')")

def add_attribute_OPERACION(ft):
  attr = ft.add("OPERACION",8)
  attr.setSize(30)
  attr.setAllowIndexDuplicateds(False)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'OPERACION')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Operacion')
  attr.setOrder(40)
  attr.setPrecision(-1)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def updateft():
    dataManager = DALLocator.getDataManager()
    ws = dataManager.getDatabaseWorkspace("ARENA2_DB")
    server = ws.getServerExplorer()
    accidentesParameters = server.get("ARENA2_ACCIDENTES")
    dataManager = DALLocator.getDataManager()
    store = dataManager.openStore(accidentesParameters.getProviderName(),accidentesParameters)
    ft = store.getDefaultFeatureType()
    eft = None #store.getDefaultFeatureType().getEditable()
    if ft.get("OPERACION")==None: 
      if not store.isEditing():
        store.edit()
      if eft==None: 
        eft = store.getDefaultFeatureType().getEditable()
      add_attribute_OPERACION(eft)
    if ft.get("ESTADO_ACCIDENTE")==None: 
      if not store.isEditing():
        store.edit()
      if eft==None: 
        eft = store.getDefaultFeatureType().getEditable()
      add_attribute_ESTADO_ACCIDENTE(eft)

    
    if eft!=None:
      store.update(eft)
    if store.isEditing():
      store.finishEditing()
    DisposeUtils.dispose(store)
    return
    
def updateForRules():
    transformCodigoINE.updateWorkspace()
    geocode.updateWorkspace()




########
######## DGTT
########


def add_attribute_TOTAL_VICTIMAS_DGT(ft):
  attr = ft.add("TOTAL_VICTIMAS_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'TOTAL_VICTIMAS_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Total_victimas_DGT')
  attr.setOrder(270)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def add_attribute_TOTAL_MUERTOS_DGT(ft):
  attr = ft.add("TOTAL_MUERTOS_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'TOTAL_MUERTOS_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Total_muertos_DGT')
  attr.setOrder(280)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')
  tags.set(u'dal.search.attribute.priority', u'10')

def add_attribute_TOTAL_GRAVES_DGT(ft):
  attr = ft.add("TOTAL_GRAVES_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'TOTAL_GRAVES_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Total_graves_DGT')
  attr.setOrder(290)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')
  tags.set(u'dal.search.attribute.priority', u'11')

def add_attribute_TOTAL_LEVES_DGT(ft):
  attr = ft.add("TOTAL_LEVES_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'TOTAL_LEVES_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Total_Leves_DGT')
  attr.setOrder(300)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')
  tags.set(u'dal.search.attribute.priority', u'12')

def add_attribute_TOTAL_ILESOS_DGT(ft):
  attr = ft.add("TOTAL_ILESOS_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'TOTAL_ILESOS_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Total_ilesos_DGT')
  attr.setOrder(310)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def add_attribute_TOTAL_VEHICULOS_DGT(ft):
  attr = ft.add("TOTAL_VEHICULOS_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'TOTAL_VEHICULOS_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Total_vehiculos_implicados_DGT')
  attr.setOrder(320)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')
  tags.set(u'dal.search.attribute.priority', u'13')

def add_attribute_TOTAL_CONDUCTORES_DGT(ft):
  attr = ft.add("TOTAL_CONDUCTORES_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'TOTAL_CONDUCTORES_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Total_conductores_implicados_DGT')
  attr.setOrder(330)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def add_attribute_TOTAL_PASAJEROS_DGT(ft):
  attr = ft.add("TOTAL_PASAJEROS_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'TOTAL_PASAJEROS_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Total_pasajeros_implicados_DGT')
  attr.setOrder(340)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def add_attribute_TOTAL_PEATONES_DGT(ft):
  attr = ft.add("TOTAL_PEATONES_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'TOTAL_PEATONES_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Total_peatones_implicados_DGT')
  attr.setOrder(350)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def add_attribute_NUM_TURISMOS_DGT(ft):
  attr = ft.add("NUM_TURISMOS_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'NUM_TURISMOS_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Num_turismos_implicados_DGT')
  attr.setOrder(360)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def add_attribute_NUM_FURGONETAS_DGT(ft):
  attr = ft.add("NUM_FURGONETAS_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'NUM_FURGONETAS_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Num_furgonetas_implicadas_DGT')
  attr.setOrder(370)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def add_attribute_NUM_CAMIONES_DGT(ft):
  attr = ft.add("NUM_CAMIONES_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'NUM_CAMIONES_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Num_camiones_implicados_DGT')
  attr.setOrder(380)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def add_attribute_NUM_AUTOBUSES_DGT(ft):
  attr = ft.add("NUM_AUTOBUSES_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'NUM_AUTOBUSES_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Num_autobuses_implicados_DGT')
  attr.setOrder(390)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def add_attribute_NUM_CICLOMOTORES_DGT(ft):
  attr = ft.add("NUM_CICLOMOTORES_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'NUM_CICLOMOTORES_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Num_ciclomotores_implicados_DGT')
  attr.setOrder(400)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def add_attribute_NUM_MOTOCICLETAS_DGT(ft):
  attr = ft.add("NUM_MOTOCICLETAS_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'NUM_MOTOCICLETAS_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Num_motocicletas_implicadas_DGT')
  attr.setOrder(410)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def add_attribute_NUM_BICICLETAS_DGT(ft):
  attr = ft.add("NUM_BICICLETAS_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'NUM_BICICLETAS_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Num_bicicletas_implicadas_DGT')
  attr.setOrder(420)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')

def add_attribute_NUM_OTROS_VEHI_DGT(ft):
  attr = ft.add("NUM_OTROS_VEHI_DGT",4)
  attr.setSize(10)
  attr.setAllowIndexDuplicateds(True)
  attr.setAllowNull(True)
  attr.setDataProfileName(None)
  attr.setDescription(u'NUM_OTROS_VEHI_DGT')
  attr.setGroup(None)
  attr.setHidden(False)
  attr.setIsAutomatic(False)
  attr.setIsIndexAscending(True)
  attr.setIsIndexed(False)
  attr.setIsPrimaryKey(False)
  attr.setIsReadOnly(False)
  attr.setIsTime(False)
  attr.setLabel(u'_Num_otros_vehiculos_implicados_DGT')
  attr.setOrder(430)
  attr.setPrecision(0)
  attr.setReadOnly(False)
  attr.setRelationType(0)
  tags = attr.getTags()
  tags.set(u'dynform.readonly', u'True')



def updateDGT():
    dataManager = DALLocator.getDataManager()
    ws = dataManager.getDatabaseWorkspace("ARENA2_DB")
    server = ws.getServerExplorer()
    accidentesParameters = server.get("ARENA2_ACCIDENTES")
    dataManager = DALLocator.getDataManager()
    store = dataManager.openStore(accidentesParameters.getProviderName(),accidentesParameters)
    ft = store.getDefaultFeatureType()
    eft = None #store.getDefaultFeatureType().getEditable()
    myfuncs = [ [add_attribute_TOTAL_VICTIMAS_DGT,"TOTAL_VICTIMAS_DGT"],
      [add_attribute_TOTAL_MUERTOS_DGT,"TOTAL_MUERTOS_DGT"],
      [add_attribute_TOTAL_GRAVES_DGT,"TOTAL_GRAVES_DGT"],
      [add_attribute_TOTAL_LEVES_DGT,"TOTAL_LEVES_DGT"],
      [add_attribute_TOTAL_ILESOS_DGT,"TOTAL_ILESOS_DGT"],
      [add_attribute_TOTAL_VEHICULOS_DGT,"TOTAL_VEHICULOS_DGT"],
      [add_attribute_TOTAL_CONDUCTORES_DGT,"TOTAL_CONDUCTORES_DGT"],
      [add_attribute_TOTAL_PASAJEROS_DGT,"TOTAL_PASAJEROS_DGT"],
      [add_attribute_TOTAL_PEATONES_DGT,"TOTAL_PEATONES_DGT"],
      [add_attribute_NUM_TURISMOS_DGT,"NUM_TURISMOS_DGT"],
      [add_attribute_NUM_FURGONETAS_DGT,"NUM_FURGONETAS_DGT"],
      [add_attribute_NUM_CAMIONES_DGT,"NUM_CAMIONES_DGT"],
      [add_attribute_NUM_AUTOBUSES_DGT,"NUM_AUTOBUSES_DGT"],
      [add_attribute_NUM_CICLOMOTORES_DGT,"NUM_CICLOMOTORES_DGT"],
      [add_attribute_NUM_MOTOCICLETAS_DGT,"NUM_MOTOCICLETAS_DGT"],
      [add_attribute_NUM_BICICLETAS_DGT,"NUM_BICICLETAS_DGT"],
      [add_attribute_NUM_OTROS_VEHI_DGT,"NUM_OTROS_VEHI_DGT"]]

    for addattr in myfuncs:
        if ft.get(addattr[1])==None: 
          if not store.isEditing():
            store.edit()
          if eft==None: 
            eft = store.getDefaultFeatureType().getEditable()
          addattr[0](eft)
      
    if eft!=None:
      store.update(eft)
    if store.isEditing():
      store.finishEditing()
    DisposeUtils.dispose(store)
    return










    
def main(*args):
    #updateDGT()
    #updateft()
    updateForRules()
    pass
