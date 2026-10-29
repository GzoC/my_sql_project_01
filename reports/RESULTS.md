# Cinco decisiones de mantenimiento con SQL

**Datos 100% sintéticos. No describen una planta real ni acreditan ahorros.**

Período UTC: [2025-01-01 00:00:00, 2025-04-01 00:00:00). Semilla 42.

## 01 · ¿Qué activos concentran las paradas?

Equipo 02 concentra 532.72 h (21.48%) de parada en el escenario.

Horas calendario de todas las paradas registradas, planificadas o no. Se unen solapamientos antes de sumar. Revisar causas del activo líder; no equivale a pérdida de producción.

[Tabla completa](01_downtime.csv)

## 02 · ¿Cómo varía el tiempo de restauración por activo?

Equipo 04 tiene el mayor MTTR observado: 6.29 h. 8 fallas están censuradas al corte y no entran al promedio.

MTTR = promedio de tiempo hasta restauración de fallas iniciadas en el período y restauradas al corte. Las censuradas se cuentan aparte; no se asigna cero. No mide horas efectivas de trabajo ni elimina sesgo por exclusión de fallas abiertas.

[Tabla completa](02_mttr.csv)

## 03 · ¿Qué órdenes siguen abiertas al corte?

8 órdenes abiertas; 8 vencidas al corte.

Estado reconstruido con fechas al corte, incluso si una orden se cerró después. Prioridad 1 es más urgente; age_rank_in_asset ordena antigüedad dentro del activo. Revisar vencidas y carga del equipo; no es una orden automática de ejecución.

[Tabla completa](03_backlog.csv)

## 04 · ¿Qué repuestos concentran el costo?

Variador: USD 272,800.00, 83.27% del costo de consumo.

Costo de consumo en USD sintéticos, sin impuestos, mano de obra ni inventario. Cada transacción conserva su precio; no se multiplica al unir órdenes con fallas. Revisar abastecimiento y sustitución técnica, sin afirmar ahorro.

[Tabla completa](04_parts.csv)

## 05 · ¿Cuánta disponibilidad queda en los turnos?

Equipo 02 presenta la menor disponibilidad programada: 70.52%, con 212.27 h de parada en turno.

Tiempo programado menos unión de paradas que intersectan cada turno. Incluye paradas planificadas. Sin turnos, disponibilidad desconocida (no 100%). No es OEE: faltan rendimiento y calidad.

[Tabla completa](05_shifts.csv)

## Reproducibilidad y límites

Los CSV de data/ son generados; metrics.json registra versiones, período y tamaños. query_plans.json conserva EXPLAIN QUERY PLAN del entorno ejecutado, sin afirmar mejoras de velocidad. Los planes cambian según versión y datos. Una suma cero indica ausencia de paradas registradas, no prueba de ausencia de fallas ni cobertura de sensores.
