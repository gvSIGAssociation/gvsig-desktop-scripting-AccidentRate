
# Inicio

Esto es una prueba


```python
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

    self.w
```
