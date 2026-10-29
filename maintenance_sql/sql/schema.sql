PRAGMA foreign_keys = ON;
CREATE TABLE assets (
    asset_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    area TEXT NOT NULL,
    criticality INTEGER NOT NULL CHECK(criticality BETWEEN 1 AND 3)
) STRICT;
CREATE TABLE work_orders (
    order_id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets,
    kind TEXT NOT NULL CHECK(kind IN ('corrective','preventive')),
    priority INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 3),
    opened_at TEXT NOT NULL,
    due_at TEXT NOT NULL CHECK(due_at >= opened_at),
    completed_at TEXT CHECK(completed_at >= opened_at),
    cancelled_at TEXT CHECK(cancelled_at >= opened_at),
    CHECK(completed_at IS NULL OR cancelled_at IS NULL),
    UNIQUE(order_id, asset_id)
) STRICT;
CREATE TABLE failures (
    failure_id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets,
    order_id INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    restored_at TEXT CHECK(restored_at > started_at),
    mode TEXT NOT NULL,
    FOREIGN KEY(order_id,asset_id) REFERENCES work_orders(order_id,asset_id)
) STRICT;
CREATE TABLE downtime (
    event_id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets,
    start_at TEXT NOT NULL,
    end_at TEXT CHECK(end_at > start_at),
    reason TEXT NOT NULL CHECK(reason IN ('failure','planned','utility'))
) STRICT;
CREATE TABLE shifts (
    shift_id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets,
    start_at TEXT NOT NULL,
    end_at TEXT NOT NULL CHECK(end_at > start_at),
    UNIQUE(asset_id,start_at)
) STRICT;
CREATE TABLE parts (
    part_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
) STRICT;
CREATE TABLE part_usage (
    usage_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES work_orders,
    part_id INTEGER NOT NULL REFERENCES parts,
    used_at TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_cost_cents INTEGER NOT NULL CHECK(unit_cost_cents >= 0)
) STRICT;
CREATE INDEX idx_downtime_asset_start ON downtime(asset_id,start_at);
CREATE INDEX idx_shifts_asset_start ON shifts(asset_id,start_at);
CREATE INDEX idx_failure_start ON failures(started_at);
CREATE INDEX idx_order_open ON work_orders(opened_at);
CREATE INDEX idx_usage_date ON part_usage(used_at);

-- Running MAX handles nested intervals; a simple LAG(end) would not.
-- Open stops use an upper sentinel, subsequently clipped by each query.
CREATE VIEW downtime_union AS
WITH previous AS (
 SELECT *, MAX(COALESCE(end_at,'9999-12-31 23:59:59')) OVER (
   PARTITION BY asset_id ORDER BY start_at,event_id
   ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS previous_end
 FROM downtime
), marked AS (
 SELECT *, CASE WHEN previous_end IS NULL OR start_at > previous_end
   THEN 1 ELSE 0 END AS new_group FROM previous
), grouped AS (
 SELECT *, SUM(new_group) OVER (
   PARTITION BY asset_id ORDER BY start_at,event_id ROWS UNBOUNDED PRECEDING) AS island
 FROM marked
)
SELECT asset_id, MIN(start_at) AS start_at,
 MAX(COALESCE(end_at,'9999-12-31 23:59:59')) AS end_at
FROM grouped GROUP BY asset_id,island;
