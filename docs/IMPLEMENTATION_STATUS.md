# Estado de implementación — 29 de octubre de 2026

Implementación y validación terminadas en `codex/maintenance-sql-analytics`. [PR #3](https://github.com/GzoC/my_sql_project_01/pull/3): integración en `main` pendiente de autorización específica. Base histórica `8cc0767c9210c2d5b06c7ed9215361d60675efe0`; ejercicio educativo original preservado en `legacy/intro_sql` y en el historial.

## Evidencia ejecutada

- **Local:** 13 pruebas de integridad y métricas aprobadas con Python 3.12.13 y SQLite 3.53.1; Ruff aprobado; informe completo y exportación opcional de la base ejecutados. Versiones y resultados en `reports/metrics.json`.
- **CI de implementación:** [40929598293](https://github.com/GzoC/my_sql_project_01/actions/runs/40929598293) aprobada para `ef9704dbebb22ad4a70710a97ca3af46fe39db2c`. Python 3.11/3.13 ejecutan pruebas, generación del informe, construcción de wheel e instalación/ejecución fuera del checkout. La ejecución push 40929536597 también pasó. Los checks del PR registran las ejecuciones posteriores de documentación.
- **Datos y artefactos:** manifiesto SHA256 comprobado contra los bytes preparados para Git, con finales de línea LF para conservar hashes al cambiar de plataforma. Planes SQL conservados para inspección; no se afirma mejora de rendimiento.
- **Navegador real local:** escritorio 1280×900 y viewport móvil 390×844 (375 px de contenido por la barra de desplazamiento), sin desbordamiento horizontal de la página. Cinco tablas, enlaces CSV y navegación al backlog comprobados. La tabla móvil permite desplazamiento horizontal con teclado.
- **Descarga real:** `03_backlog.csv` descargado desde el informe coincide byte a byte con `reports/03_backlog.csv`; SHA256 `1e1fc3283526322faf10e96477e36162c1c471119bb0f66221f1295ce1dab517`. Las cinco exportaciones CSV se comprueban además en la suite de pruebas.
- **Consola:** sin advertencias ni errores en la inspección de escritorio. La pestaña de prueba se cerró y el servidor local 8505 se detuvo al guardar el checkpoint.

Capturas: [escritorio](images/sql-desktop.png) y [backlog móvil](images/sql-mobile.png). Corresponden al informe generado, no a datos de una planta real.

## Entrega y límites

Siete tablas relacionadas, contratos de fechas/turnos/tipos/claves, cinco consultas con CTE y ventanas, unión de paradas solapadas, datos sintéticos reproducibles y CLI sin dependencias externas de ejecución. Informes HTML, Markdown, CSV y JSON con las cinco respuestas y sus límites.

Bundle, ZIP de código, artefactos y evidencia local preservados en checkpoints externos al repositorio. El último cambio de cierre incorpora estas capturas y documentación; no modifica consultas ni resultados.

Solo queda la autorización específica para integrar y comprobar después la CI de `main`. No se ha publicado un sitio web ni ejecutado Docker. No se atribuyen datos reales, ahorros, OEE ni resultados de benchmark.
