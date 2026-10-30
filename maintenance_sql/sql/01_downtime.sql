-- All recorded stops (planned and unplanned), unioned and clipped to [start,end).
WITH totals AS (
 SELECT a.asset_id,a.name,COALESCE(SUM(
   unixepoch(MIN(d.end_at,:end))-unixepoch(MAX(d.start_at,:start))),0)/3600.0 AS stop_hours
 FROM assets a LEFT JOIN downtime_union d ON a.asset_id=d.asset_id
   AND d.start_at < :end AND d.end_at > :start
 GROUP BY a.asset_id
)
SELECT *, ROUND(100.0*stop_hours/NULLIF(SUM(stop_hours) OVER (),0),2) AS share_pct,
 ROUND(100.0*SUM(stop_hours) OVER (ORDER BY stop_hours DESC,asset_id ROWS UNBOUNDED PRECEDING)
   /NULLIF(SUM(stop_hours) OVER (),0),2) AS cumulative_pct
FROM totals ORDER BY stop_hours DESC,asset_id;
