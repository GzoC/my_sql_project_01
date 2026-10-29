-- Intersect already-unioned stops with nonoverlapping scheduled asset shifts.
WITH schedule AS (
 SELECT shift_id,asset_id,MAX(start_at,:start) AS start_at,MIN(end_at,:end) AS end_at
 FROM shifts WHERE start_at < :end AND end_at > :start
), per_shift AS (
 SELECT s.shift_id,s.asset_id,
 (unixepoch(s.end_at)-unixepoch(s.start_at))/3600.0 AS scheduled_hours,
 COALESCE(SUM(unixepoch(MIN(s.end_at,d.end_at))-unixepoch(MAX(s.start_at,d.start_at))),0)
 /3600.0 AS stop_hours
 FROM schedule s LEFT JOIN downtime_union d ON s.asset_id=d.asset_id
 AND d.start_at < s.end_at AND d.end_at > s.start_at GROUP BY s.shift_id
)
SELECT a.asset_id,a.name,COUNT(s.shift_id) AS shifts,
 ROUND(SUM(s.scheduled_hours),2) AS scheduled_hours,
 ROUND(SUM(s.stop_hours),2) AS stopped_in_shift_hours,
 ROUND(100.0*(SUM(s.scheduled_hours)-SUM(s.stop_hours))/NULLIF(SUM(s.scheduled_hours),0),2)
 AS scheduled_availability_pct
FROM assets a LEFT JOIN per_shift s USING(asset_id)
GROUP BY a.asset_id ORDER BY scheduled_availability_pct,a.asset_id;
