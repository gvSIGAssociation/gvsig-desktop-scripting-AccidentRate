{% rem encoding: utf-8 %}

# Introducción

El presente documento se centra en definir las diferentes soluciones que permite la herramienta de software libre gvSIG Desktop para la gestión de datos sobre accidentes de tráfico, así como toda la información derivada de estos.

Dicha información se obtiene gracias a la aplicación de la dirección general de tráfico Arena2, un sistema de captura, almacenamiento y gestión de datos sobre accidentes de tráfico, vehículos implicados y personas (conductores, pasajeros y peatones) para dicha institución.

Como se detalla anteriormente los elementos sobre los que Arena2 centra su atención son:

**Accidentes de tráfico**. Entendido este como una acción producida o con origen en vías o terrenos objeto de la legislación de tráfico, circulación de vehículos a motor y seguridad vial en la cual una o varias personas fallecen o son heridas y en la que al menos existe un vehículo en movimiento.

**Vehículo**. Se considera que un vehículo forma parte o está implicado en un accidente de tráfico si este hace colisión con otro vehículo, peatones, animales o cualquiera otro obstáculo. Estos elementos también pueden considerarse parte de un accidente aun sin hacer colisión, si la posición de estos provoca las premisas detalladas en el anterior párrafo.

**Personas**. Una persona implicada en un accidente de tráfico es cualquier ocupante de un vehículo envuelto en uno de los casos descritos en el apartado vehículo, o cualquier otra cuando resulten afectada en alguna de las situaciones descritas en el apartado accidentes de tráfico. Las personas que forman parte en un accidente de tráfico pueden ser;

* Conductor. Persona a cargo de los mandos del vehículo.
* Pasajero. Persona que sin ser conductor se encuentra dentro o sobre el vehículo, o es arrollada mientras se está subiendo o bajando del vehículo.
* Peatón. Persona que sin ser conductor ni pasajero se ve implicada en el accidente.

Arena2 a parte de ser un sistema de captura, almacenamiento y gestión de información permite el tratamiento y gestión de la información recogida para la elaboración de estadística e informes de accidentalidad.

El formato seleccionado por la aplicación dicha información es el formato de intercambio XML, un estándar de intercambio de información estructurada entre diferentes plataformas tanto online como offline.

GvSIG desktop es un sistema de información geográfica libre, con licencia GNU/GPL, mantenido por la Asociación gvSIG el cual ha desarrollado una herramienta capaz de importar los datos proporcionados por el software Arena2, almacenarlos y tratarlos de forma que sobre estos se pueda realizar búsquedas, filtrados, generación de informes, exportación de datos y todas aquellas acciones necesarias para el estudio de la accidentalidad a cualquier escala, desde el ámbito nacional hasta el ámbito local.
