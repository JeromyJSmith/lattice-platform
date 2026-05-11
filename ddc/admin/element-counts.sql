-- Element counts grouped by BIS class / subclass
-- Powers the "Element count by type" admin panel.

SELECT
  bis_class,
  bis_subclass,
  COUNT(*)                              AS count,
  SUM(COALESCE(unit_cost, 0) * COALESCE(quantity, 1))  AS subtotal_cost_usd,
  AVG(unit_cost)                        AS avg_unit_cost,
  COUNT(*) FILTER (WHERE unit_cost IS NULL OR unit_cost = 0) AS missing_cost_count
FROM read_parquet('lattice_bridge_ifc_ifc_elements.parquet')
GROUP BY bis_class, bis_subclass
ORDER BY count DESC;
