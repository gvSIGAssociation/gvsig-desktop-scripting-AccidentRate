
# Notas y convenciones a usar 

Cada seccion del documento debera ir a un fichero independiente, es decir, 
no debe haber mas de un *"titulo"* en un fichero *".md"*.

Por cada fichero *md* se crearan dos, el fichero y otro de mismo nombre acabado
en "_t.md". Ademas si el fichero tiene imagenes, se creara una carpeta del mismo nombre
que el fichero pero acabada en "_files".

Ademas en una carpeta donde hayn varios documento, tendremos un fichero 'index.md', 
en el que crearemos el indice con los documentos de la carpeta.

Por ultimo, existira un fichero 'all.md' que incluira los documentos que 
corresponda para generar el document ODT/PDF con toda la documentacion.

Por ejemplo:

```
informes_files
formularios_files
all.md
formularios.md
formularios_t.md
index.md
informes.md
informes_t.md
```

* Los documentos *"informes.md"* y *'formularios.md'* no contendran *titulos*.
* Las imagenes que vayan en *"informes.md"* estaran en la carpeta *informes_files*,
  y se utilizaran rutas relativas para insertarlas en el documento.
* El documento *"informes_t.md"*, contendra solo un titulo de primer orden y 
  un include relativo del fichero *"informes.md"*.
* El documento *'index.md'* contendra un indice de los documentos para mostrar 
  en la web. Los enlaces a los *md* seran a los acabados en *"_t.md"*.

  Por ejmplo:
  
  ```
  {% comment %} encoding: utf-8 {% endcomment %}
  
  # Consulta de datos
  
  * [Informes](informes_t.md)
  
  * [Formularios](formularios_t.md)
  ```

* El fichero *'all.md'* contendra los titulos e includes necesarios para montar
  el documento completo y poder producir un ODT/PDF.
  
  Por ejmplo:
  
  ```
  {% comment %} encoding: utf-8 {% endcomment %}
  
  # Consulta de datos

  ## Informes
  
  {% include informes.md %}
  
  ## Formularios
  
  {% include formularios.md %}
  ```
  