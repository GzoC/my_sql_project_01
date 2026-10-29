-- Snapshot as of :end, across ALL earlier opening dates (not only the report period).
SELECT w.order_id,a.name,w.kind,w.priority,w.opened_at,w.due_at,
 ROUND((unixepoch(:end)-unixepoch(w.opened_at))/86400.0,2) AS age_days,
 CASE WHEN w.due_at < :end THEN 1 ELSE 0 END AS overdue,
 ROW_NUMBER() OVER (PARTITION BY a.asset_id ORDER BY w.opened_at,w.order_id) AS age_rank_in_asset
FROM work_orders w JOIN assets a USING(asset_id)
WHERE w.opened_at < :end
 AND (w.completed_at IS NULL OR w.completed_at > :end)
 AND (w.cancelled_at IS NULL OR w.cancelled_at > :end)
ORDER BY w.priority,w.opened_at,w.order_id;
