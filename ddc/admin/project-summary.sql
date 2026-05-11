-- Project cost summary
-- Runs in DuckDB WASM against public/data/lattice_bridge_ifc_ifc_elements.parquet
-- and (when seeded) public/data/lattice_bridge_marpa_projects.parquet.
--
-- One row per MARPA project; expects ifc_elements.project_id to join cleanly.

WITH elements AS (
  SELECT
    project_id,
    COUNT(*)                                       AS element_count,
    SUM(COALESCE(unit_cost, 0) * COALESCE(quantity, 1))  AS total_cost,
    COUNT(DISTINCT bis_subclass)                   AS distinct_subclasses,
    MAX(cost_last_updated)                         AS cost_last_updated
  FROM read_parquet('lattice_bridge_ifc_ifc_elements.parquet')
  GROUP BY project_id
),
projects AS (
  SELECT project_id, name, status, phase
  FROM read_parquet('lattice_bridge_marpa_projects.parquet')
)
SELECT
  p.project_id,
  p.name,
  p.status,
  p.phase,
  COALESCE(e.element_count, 0)        AS element_count,
  COALESCE(e.total_cost, 0)           AS total_cost_usd,
  COALESCE(e.distinct_subclasses, 0)  AS distinct_subclasses,
  e.cost_last_updated
FROM projects p
LEFT JOIN elements e USING (project_id)
ORDER BY p.status, p.name;
