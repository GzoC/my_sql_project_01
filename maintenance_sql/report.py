import csv
import hashlib
import html
import json
import platform
import sqlite3
from pathlib import Path

from .core import QUERIES, TABLES, connect, load, parameters, query, sql
from .synthetic import generate

TITLES = {
    "01_downtime": "01 · ¿Qué activos concentran las paradas?",
    "02_mttr": "02 · ¿Cómo varía el tiempo de restauración por activo?",
    "03_backlog": "03 · ¿Qué órdenes siguen abiertas al corte?",
    "04_parts": "04 · ¿Qué repuestos concentran el costo?",
    "05_shifts": "05 · ¿Cuánta disponibilidad queda en los turnos?",
}
NOTES = {
    "01_downtime": "Horas calendario de todas las paradas registradas, planificadas o no. Se unen solapamientos antes de sumar. Revisar causas del activo líder; no equivale a pérdida de producción.",
    "02_mttr": "MTTR = promedio de tiempo hasta restauración de fallas iniciadas en el período y restauradas al corte. Las censuradas se cuentan aparte; no se asigna cero. No mide horas efectivas de trabajo ni elimina sesgo por exclusión de fallas abiertas.",
    "03_backlog": "Estado reconstruido con fechas al corte, incluso si una orden se cerró después. Prioridad 1 es más urgente; age_rank_in_asset ordena antigüedad dentro del activo. Revisar vencidas y carga del equipo; no es una orden automática de ejecución.",
    "04_parts": "Costo de consumo en USD sintéticos, sin impuestos, mano de obra ni inventario. Cada transacción conserva su precio; no se multiplica al unir órdenes con fallas. Revisar abastecimiento y sustitución técnica, sin afirmar ahorro.",
    "05_shifts": "Tiempo programado menos unión de paradas que intersectan cada turno. Incluye paradas planificadas. Sin turnos, disponibilidad desconocida (no 100%). No es OEE: faltan rendimiento y calidad.",
}


def write_csv(path, rows, columns):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def display(value):
    if value is None:
        return "Sin dato"
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)


def run(
    output,
    start="2025-01-01 00:00:00",
    end="2025-04-01 00:00:00",
    seed=42,
    database=None,
):
    params = parameters(start, end)
    if database is not None and Path(database).exists():
        raise FileExistsError("Database exists; choose a new path to preserve it")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "data").mkdir(exist_ok=True)
    dataset = generate(seed)
    db = connect()
    try:
        load(db, dataset)
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        results = {name: query(db, name, start, end) for name in QUERIES}
        plans = {
            name: [
                dict(r) for r in db.execute("EXPLAIN QUERY PLAN " + sql(name), params)
            ]
            for name in QUERIES
        }
        for table in TABLES:
            columns = [r[1] for r in db.execute(f"PRAGMA table_info({table})")]
            write_csv(output / "data" / (table + ".csv"), dataset[table], columns)
        for name in QUERIES:
            columns = [d[0] for d in db.execute(sql(name), params).description]
            write_csv(
                output / (name + ".csv"), [r.values() for r in results[name]], columns
            )
        if database is not None:
            destination = Path(database)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(destination) as saved:
                db.backup(saved)
        lead = results["01_downtime"][0]
        part = results["04_parts"][0] if results["04_parts"] else None
        backlog = results["03_backlog"]
        censored = sum(r["censored"] for r in results["02_mttr"])
        slowest = next(
            (r for r in results["02_mttr"] if r["mttr_hours"] is not None), None
        )
        lowest = next(
            (
                r
                for r in results["05_shifts"]
                if r["scheduled_availability_pct"] is not None
            ),
            None,
        )
        summaries = {
            "01_downtime": f"{lead['name']} concentra {lead['stop_hours']:.2f} h ({display(lead['share_pct'])}%) de parada en el escenario.",
            "02_mttr": (
                f"{slowest['name']} tiene el mayor MTTR observado: {slowest['mttr_hours']} h. "
                if slowest
                else "Sin restauraciones observadas. "
            )
            + f"{censored} fallas están censuradas al corte y no entran al promedio.",
            "03_backlog": f"{len(backlog)} órdenes abiertas; {sum(r['overdue'] for r in backlog)} vencidas al corte.",
            "04_parts": f"{part['name']}: USD {part['cost_usd']:,.2f}, {part['share_pct']}% del costo de consumo."
            if part
            else "Sin consumos en este período.",
            "05_shifts": f"{lowest['name']} presenta la menor disponibilidad programada: {lowest['scheduled_availability_pct']}%, con {lowest['stopped_in_shift_hours']} h de parada en turno."
            if lowest
            else "Sin turnos programados; disponibilidad desconocida.",
        }
        provenance = {
            "synthetic": True,
            "seed": seed,
            "period": params,
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
            "rows": {k: len(v) for k, v in dataset.items()},
            "integrity_check": "ok",
            "foreign_key_violations": 0,
        }
        (output / "metrics.json").write_text(
            json.dumps(
                {"provenance": provenance, "results": results},
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (output / "query_plans.json").write_text(
            json.dumps(plans, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        md = [
            "# Cinco decisiones de mantenimiento con SQL",
            "",
            "**Datos 100% sintéticos. No describen una planta real ni acreditan ahorros.**",
            "",
            f"Período UTC: [{start}, {end}). Semilla {seed}.",
            "",
        ]
        sections = []
        for name in QUERIES:
            rows = results[name]
            md += [
                "## " + TITLES[name],
                "",
                summaries[name],
                "",
                NOTES[name],
                "",
                f"[Tabla completa]({name}.csv)",
                "",
            ]
            headings = list(rows[0]) if rows else []
            header = "".join(f"<th scope='col'>{html.escape(c)}</th>" for c in headings)
            body = "".join(
                "<tr>"
                + "".join(f"<td>{html.escape(display(v))}</td>" for v in r.values())
                + "</tr>"
                for r in rows
            )
            table = (
                f"<div class='table-scroll' tabindex='0' role='region' aria-label='{html.escape(TITLES[name])}'><table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table></div>"
                if rows
                else "<p>Sin registros para este corte.</p>"
            )
            sections.append(
                f"<section id='{name}'><h2>{html.escape(TITLES[name])}</h2><p class='finding'>{html.escape(summaries[name])}</p><p>{html.escape(NOTES[name])}</p>{table}<a download href='{name}.csv'>Descargar CSV · {len(rows)} filas</a></section>"
            )
        md += [
            "## Reproducibilidad y límites",
            "",
            "Los CSV de data/ son generados; metrics.json registra versiones, período y tamaños. query_plans.json conserva EXPLAIN QUERY PLAN del entorno ejecutado, sin afirmar mejoras de velocidad. Los planes cambian según versión y datos. Una suma cero indica ausencia de paradas registradas, no prueba de ausencia de fallas ni cobertura de sensores.",
            "",
        ]
        (output / "RESULTS.md").write_text(
            "\n".join(md), encoding="utf-8", newline="\n"
        )
        nav = "".join(
            f"<a href='#{q}'>{i + 1:02d} {html.escape(TITLES[q].split('· ')[1])}</a>"
            for i, q in enumerate(QUERIES)
        )
        page = """<!doctype html><html lang='es'><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Mantenimiento · SQL para decidir</title><style>
        :root{color-scheme:light;font-family:system-ui,sans-serif;color:#173039;background:#f3f5f1}*{box-sizing:border-box}body{margin:0}header{background:#173b39;color:#fff;padding:60px max(24px,calc((100vw - 1120px)/2)) 40px}header p{color:#d3e9e1}h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.08;max-width:850px;margin:20px 0}h2{font-size:1.4rem}a{color:#075c58;text-underline-offset:4px}nav{display:flex;flex-wrap:wrap;gap:12px;padding:22px 0}nav a{font-size:.85rem;background:#fff;border:1px solid #b9ceca;border-radius:6px;padding:10px}main{max-width:1168px;margin:auto;padding:0 24px 48px}.badge{display:inline-block;border:1px solid #91bbb0;border-radius:30px;padding:6px 12px;font-size:.8rem;letter-spacing:.06em}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:24px 0}.card,section{background:white;border:1px solid #cfdbd6;border-radius:12px;padding:24px}.card strong{display:block;font-size:2rem;margin-top:10px}.card span{color:#52676e}section{margin-bottom:20px;scroll-margin-top:16px}.finding{font-size:1.2rem;color:#075c58;font-weight:600}p{line-height:1.65}.table-scroll{overflow:auto;margin:24px 0;max-height:440px}table{border-collapse:collapse;width:100%;font-size:.85rem}th,td{text-align:left;border-bottom:1px solid #e0e8e4;padding:10px;white-space:nowrap}th{background:#edf3ef;position:sticky;top:0}footer{padding:24px 0;color:#52676e}:focus-visible{outline:3px solid #d28b16;outline-offset:3px}@media(max-width:600px){.cards{grid-template-columns:1fr}header{padding:36px 20px}main{padding:0 16px}section{padding:18px}}
        </style><header><span class='badge'>PORTAFOLIO · DATOS SINTÉTICOS · SQLITE</span><h1>De registros de mantenimiento a decisiones verificables.</h1><p>Cinco preguntas, consultas SQL abiertas y resultados que puedes reproducir.</p>"""
        page += f"<p>{html.escape(start)} → {html.escape(end)} · UTC · semilla {seed}</p></header><main><div class='cards'><div class='card'><span>Activos del escenario</span><strong>{len(dataset['assets'])}</strong></div><div class='card'><span>Órdenes registradas</span><strong>{len(dataset['work_orders'])}</strong></div><div class='card'><span>Órdenes abiertas al corte</span><strong>{len(backlog)}</strong></div></div><nav aria-label='Preguntas del informe'>{nav}</nav>"
        page += (
            "".join(sections)
            + "<footer><strong>Alcance:</strong> escenario inventado de 90 días. No acredita datos de campo, ahorros, OEE ni productividad. Las horas son UTC y los intervalos semiabiertos. Tablas desplazables con teclado. <a href='RESULTS.md'>Informe Markdown</a> · <a href='metrics.json'>Resultados y versiones</a> · <a href='query_plans.json'>Planes SQL</a></footer></main></html>"
        )
        (output / "index.html").write_text(page, encoding="utf-8", newline="\n")
        hashes = {
            p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*"))
            if p.is_file() and p.name != "manifest.json"
        }
        (output / "manifest.json").write_text(
            json.dumps(hashes, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        return provenance
    finally:
        db.close()
