-- Cost at consumption, integer cents. Does not multiply costs by joining to event-level tables.
WITH cost AS (
 SELECT p.part_id,p.name,SUM(u.quantity) AS units,
 SUM(u.quantity*u.unit_cost_cents) AS cost_cents
 FROM part_usage u JOIN parts p USING(part_id)
 WHERE u.used_at >= :start AND u.used_at < :end GROUP BY p.part_id
)
SELECT *,ROUND(cost_cents/100.0,2) AS cost_usd,
 ROUND(100.0*cost_cents/NULLIF(SUM(cost_cents) OVER (),0),2) AS share_pct,
 ROUND(100.0*SUM(cost_cents) OVER (ORDER BY cost_cents DESC,part_id ROWS UNBOUNDED PRECEDING)
 /NULLIF(SUM(cost_cents) OVER (),0),2) AS cumulative_pct
FROM cost ORDER BY cost_cents DESC,part_id;
