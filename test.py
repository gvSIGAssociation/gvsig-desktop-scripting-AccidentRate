# encoding: utf-8

import gvsig

from gvsig import getResource

from addons.Arena2Importer import Arena2ImportLocator
from addons.AccidentRate import importrules


def testImport():
  Arena2ImportLocator.selfRegister()
  importrules.selfRegister()

  manager = Arena2ImportLocator.getManager()
  dialog = manager.createImportDialog()
  dialog.arena2filePicker.coerceAndSet(
    getResource(__file__,"..","Arena2Reader","datos", "test","TV_03_2019_01_Q1","victimas.xml")
  )
  dialog.showWindow("ARENA2 Importar accidentes")

def testCreateTables():
  manager = Arena2ImportLocator.getManager()
  dialog = manager.createTablestDialog()
  dialog.showWindow("ARENA2 Crear tablas de accidentes")

def main(*args):
  testImport()
