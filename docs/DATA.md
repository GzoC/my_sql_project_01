# Procedencia: escenario enteramente sintético

No se descargan datos personales, empresariales ni de una planta. `maintenance_sql/synthetic.py` genera un escenario inventado de 12 activos y 90 días (enero–marzo de 2025), turnos de 08:00 a 16:00 UTC todos los días y una mezcla de órdenes correctivas/preventivas. Semilla predeterminada 42 mediante Random de Python. Se registra versión del intérprete y SQLite.

Con semilla 42: 12 activos, 261 órdenes, 184 fallas, 326 reportes de parada, 1.080 turnos, 6 repuestos y 363 consumos. Las probabilidades, duraciones y precios fueron elegidos para ilustrar consultas; no se ajustaron a una distribución industrial ni se calibraron con mediciones.

Hay reportes anidados intencionales y fallas abiertas al final del escenario. Un activo puede acumular reportes mientras una parada anterior continúa; se interpretan como registros de eventos concurrentes, no prueba de que estuviera operando. Los precios en USD son ficticios. No hay impuestos, moneda mixta, mano de obra ni stock.

Cada ejecución exporta las siete tablas a `reports/data`, los resultados y versiones a `metrics.json` y un manifiesto SHA256 de artefactos. `query_plans.json` depende de la versión de SQLite; no se exige igualdad entre entornos. La semilla y el mismo entorno reproducen datos y resultados. Cambiar la ventana no altera los datos generados.

El dataset educativo anterior de seis pedidos y cinco productos está preservado en legacy/intro_sql, ajeno a los resultados actuales. Código y escenario sintético se distribuyen bajo MIT.
