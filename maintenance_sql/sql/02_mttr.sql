-- Cohort: failures starting in [start,end). Incomplete restoration is counted, not zero-filled.
SELECT a.asset_id,a.name,COUNT(f.failure_id) AS failures,
 SUM(CASE WHEN f.restored_at <= :end THEN 1 ELSE 0 END) AS restored,
 SUM(CASE WHEN f.failure_id IS NOT NULL AND (f.restored_at IS NULL OR f.restored_at > :end)
   THEN 1 ELSE 0 END) AS censored,
 ROUND(AVG(CASE WHEN f.restored_at <= :end
   THEN (unixepoch(f.restored_at)-unixepoch(f.started_at))/3600.0 END),2) AS mttr_hours
FROM assets a LEFT JOIN failures f ON f.asset_id=a.asset_id
 AND f.started_at >= :start AND f.started_at < :end
GROUP BY a.asset_id ORDER BY mttr_hours DESC,a.asset_id;
