import sqlite3
from datetime import datetime
from importlib.resources import files

TABLES = (
    "assets",
    "work_orders",
    "failures",
    "downtime",
    "shifts",
    "parts",
    "part_usage",
)
TIME_COLUMNS = {
    "work_orders": ("opened_at", "due_at", "completed_at", "cancelled_at"),
    "failures": ("started_at", "restored_at"),
    "downtime": ("start_at", "end_at"),
    "shifts": ("start_at", "end_at"),
    "part_usage": ("used_at",),
}
QUERIES = ("01_downtime", "02_mttr", "03_backlog", "04_parts", "05_shifts")


def timestamp(value):
    if not isinstance(value, str) or len(value) != 19:
        raise ValueError("Use YYYY-MM-DD HH:MM:SS in UTC")
    parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    if parsed.strftime("%Y-%m-%d %H:%M:%S") != value:
        raise ValueError("Noncanonical timestamp")
    return value


def sql(name):
    return (
        files("maintenance_sql")
        .joinpath("sql", name + ".sql")
        .read_text(encoding="utf-8")
    )


def connect():
    if sqlite3.sqlite_version_info < (3, 37):
        raise RuntimeError("SQLite 3.37+ required for STRICT tables")
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(sql("schema"))
    # Validate date syntax even for direct SQL inserts and updates on this connection.
    for table, columns in TIME_COLUMNS.items():
        condition = " OR ".join(
            f"(NEW.{c} IS NOT NULL AND strftime('%Y-%m-%d %H:%M:%S',NEW.{c},'+0 seconds') IS NOT NEW.{c})"
            for c in columns
        )
        for operation in ("INSERT", "UPDATE"):
            db.executescript(f"""CREATE TRIGGER validate_{table}_{operation} BEFORE {operation} ON {table}
            WHEN {condition} BEGIN SELECT RAISE(ABORT,'Invalid UTC timestamp'); END;""")
    for operation in ("INSERT", "UPDATE"):
        db.executescript(f"""CREATE TRIGGER shifts_overlap_{operation} BEFORE {operation} ON shifts
        WHEN EXISTS(SELECT 1 FROM shifts s WHERE s.asset_id=NEW.asset_id
        AND s.shift_id != NEW.shift_id AND s.start_at < NEW.end_at AND s.end_at > NEW.start_at)
        BEGIN SELECT RAISE(ABORT,'Overlapping asset shifts'); END;""")
    return db


def load(db, dataset):
    # All-or-nothing import. Constraints must not leave a partial scenario.
    with db:
        for table in TABLES:
            rows = dataset.get(table, [])
            if rows:
                placeholders = ",".join("?" for _ in rows[0])
                db.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Foreign key check failed")


def parameters(start, end):
    timestamp(start)
    timestamp(end)
    if start >= end:
        raise ValueError("Report start must precede end")
    return {"start": start, "end": end}


def query(db, name, start, end):
    if name not in QUERIES:
        raise ValueError("Unknown report query")
    return [dict(r) for r in db.execute(sql(name), parameters(start, end))]
