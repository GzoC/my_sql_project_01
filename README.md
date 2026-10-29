# SQL para decisiones de mantenimiento

**De órdenes y paradas a cinco decisiones verificables, con consultas abiertas y datos sintéticos reproducibles.**

Python · SQLite · CTE · funciones de ventana · integridad relacional · analítica industrial

El escenario inventa 12 activos, 261 órdenes y 90 días de operación. No contiene datos de una planta real. El foco es demostrar modelado, calidad de datos y razonamiento temporal: una parada duplicada no debe duplicar horas; una falla abierta no debe reducir artificialmente el MTTR.

## Reproducir en un comando

Python 3.11 o posterior con SQLite 3.37 o posterior. Sin librerías externas de ejecución.

```bash
git clone https://github.com/GzoC/my_sql_project_01.git
cd my_sql_project_01
python -m maintenance_sql
```

Abre `reports/index.html` en un navegador. [Lee las cinco respuestas](reports/RESULTS.md) directamente en GitHub. El comando genera tablas CSV, HTML, Markdown, JSON, datos sintéticos, hashes y planes de ejecución. Vuelve a ejecutarlo para reproducir el informe con la misma semilla; sobrescribe los artefactos de esa carpeta de salida.

```bash
python -m maintenance_sql --output reports_marzo --start "2025-03-01 00:00:00" --end "2025-04-01 00:00:00"
python -m maintenance_sql --output reports_seed7 --seed 7
python -m maintenance_sql --output reports_db --save-db var/maintenance.sqlite3
python -m unittest discover -s tests -v
```

`--save-db` es opcional y rechaza un archivo ya existente. La base se genera en memoria; el archivo guardado permite consultas de lectura con un cliente SQLite. La CLI instalada con `pip install .` es `maintenance-sql` y funciona fuera del checkout.

## Las cinco preguntas

| Pregunta | Técnica SQL | Decisión posible |
|---|---|---|
| ¿Qué activos concentran las paradas? | Unión de intervalos con máximo acumulado, CTE y Pareto | Investigar causas y cobertura en los activos líderes |
| ¿Cómo varía el tiempo de restauración por activo? | Agregación condicional y censura al corte | Revisar capacidad de restauración sin ocultar fallas abiertas |
| ¿Qué órdenes siguen abiertas? | Snapshot temporal y ROW_NUMBER | Priorizar órdenes urgentes y antiguas |
| ¿Qué repuestos concentran el costo? | Precio histórico por consumo y suma acumulada | Revisar abastecimiento sin inventar ahorros |
| ¿Cuánta disponibilidad queda en los turnos? | Intersección de intervalos y calendario | Examinar tiempo perdido dentro del plan, sin llamarlo OEE |

Las consultas están en [maintenance_sql/sql](maintenance_sql/sql). [Definiciones y modelo](docs/METHODOLOGY.md) · [Procedencia](docs/DATA.md) · [Estado y evidencia](docs/IMPLEMENTATION_STATUS.md).

## Resultado del escenario de referencia

Con semilla 42, Equipo 02 concentra 532,72 horas calendario de parada (21,48%). Su disponibilidad en turnos es 70,52%; la diferencia responde al calendario de 8 horas diarias. Ocho órdenes permanecen abiertas al corte. Los variadores concentran 83,27% del costo sintético de repuestos. Estas cifras describen el escenario generado, no desempeño profesional ni resultados industriales medidos.

Los planes `EXPLAIN QUERY PLAN` se guardan para inspección. No se afirma una mejora de rendimiento por añadir índices; se necesitarían una carga representativa y una comparación medida.

## Pruebas y límites

Las pruebas usan casos calculables a mano: intervalos anidados/solapados/abiertos, límites exactos del período, fallas sin restaurar, precios históricos, cierre posterior al corte, ausencia de turnos, restricciones y rollback. La CI reproduce el informe y ejecuta el wheel instalado fuera del repositorio en Python 3.11/3.13.

Se asume registro completo de eventos y turnos para calcular disponibilidad. Una ausencia de paradas registradas no demuestra cobertura de sensores. No se estiman OEE, MTBF, costos laborales, ahorro ni productividad. El MTTR de casos completados puede subestimar los casos largos censurados.

## Antecedente educativo

El ejercicio original de pedidos y productos se conserva sin reescribir en [legacy/intro_sql](legacy/intro_sql). Su README y notebook describen aquella versión; no son instrucciones de la aplicación actual. Historial base: `8cc0767c9210c2d5b06c7ed9215361d60675efe0`.

Autor: [GzoC](https://github.com/GzoC). Código y datos sintéticos: [MIT](LICENSE).

English: Reproducible maintenance analytics with SQLite, temporal snapshots, interval union, data constraints and five inspectable business decisions. All operational data are synthetic.
