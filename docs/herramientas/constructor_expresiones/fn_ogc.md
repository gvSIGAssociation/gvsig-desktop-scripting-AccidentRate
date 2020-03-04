{% comment %} encoding: utf-8 {% endcomment %}

{% comment %} Funciones OGC {% endcomment %}
 

**Funciones OGC**

| -------- | -------------
| ST_GeomFromText | Función que devuelve una geometría a partir de un cadena de texto conocido.
| ST_Point | Función que construye una geometría punto a partir de unas coordenadas.
| ST_GeomFromWKB | Función que crea una geometría a partir de una representación binaria conocida (WKB) y SRID opcional.
| ST_Union | Función que devuelve la unión de geometrías.
| ST_Intersects | Función que devuelve la intersección de geometrías.
| ST_Within | Función que devuelve el valor booleano si una geometría se encuentra en el interior de la otra.
| ST_Disjoint | Función que devuelve el valor booleano si varias geometrías se "cruzan espacialmente", si no comparten ningún espacio juntos.
| ST_Buffer | Función que devuelve una geometría que representa todos los puntos cuya distancia desde una geometría inicial es menor o igual que la distancia.
| ST_IsSimple | Devuelve verdadero si esta Geometría no tiene puntos geométricos anómalos, como la intersección propia o la tangencia propia.
| ST_Perimeter | Función que devuelve el perímetro de una geometría.
| ST_NumGeometries | Función que devuelve el número de geometrías.
| ST_Difference | Función que devuelve una geometría que representa la parte de una geometría no intersectada por otra.
| ST_Contains | Función que devuelve un booleano si una geometría contiene a otra.
| ST_GeometryN | Devuelve el enésimo elemento de geometría de una colección de geometría.
| ST_Dimension | Función que devuelve un entero con la dimensión de una geometría. 0 para puntos, 1 para líneas y 2 para polígonos.
| ST_Centroid | Función que calcula el centroide de una geometría como un punto.
| ST_Intersection | Función que devuelve una geometría igual a la porción compartida de dos geometrías.
| ST_Covers | Devuelve un valor booleano si algún punto de una geometría se encuentra dentro de otra.
| ST_Distance | Función que devuelve la mínima distancia cartesiana  en 2D entre dos geometrías.
| ST_Crosses | Devuelve un booleano si las geometrías proporcionadas tienen algunos, pero no todos, puntos interiores en común.
| ST_MakePoint | Función que crea un punto en 2D, 3D o 4D.
| ST_SRID | Función que devuelve el identificador de la referencia espacial de una geometría.
| ST_EndPoint | Función que devuelve el último punto de una geometría. Si la geometría es un punto devuelve NULL.
| ST_NumPoints | Función que devuelve el número de puntos de una geometría.
| ST_StartPoint | Función que devuelve el punto inicial de una geometría.
| ST_Envelope | Devuelve una geometría con forma rectangular con la extensión que envuelve una determinada geometría.
| ST_Touches | Función que devuelve un valor booleano si dos geometrías tienen un  punto en común.
| ST_Z | Devuelve la coordenada Z de un punto.
| ST_AsText | Función que devuelve una geometría en formato texto. 
| ST_Y | Devuelve la coordenada Y de un punto.
| ST_X | Devuelve la coordenada X de un punto.
| ST_SetSRID | Asigna el SRID a una geometría a partir de un valor entero.
| ST_IsValid | Función que devuelve un valor booleano si una geometría está bien formada.
| ST_CoveredBy | Función que devuelve un valor booleano si ningún punto de una geometría se encuentra fuera de otra geometría.
| ST_Overlaps | Devuelve un booleano si las geometrías comparten espacio, son de la misma dimensión, pero no están completamente contenidas entre sí.
| ST_ConvexHull | Calcula el “Convex Hull” de una geometría.
| ST_PointN | Función que devuelve n N punto de una geometría.
| ST_Area | Función que devuelve el área de una geometría.
