-- BOQ completion by phase
-- Powers the "BOQ status" admin panel.
--
-- An element is "BOQ-attached" once it has a non-null erp_item_id and unit_cost.
-- Phase completion is the ratio of attached / total per phase.

SELECT
  project_id,
  COALESCE(boq_phase, '(unphased)')      AS boq_phase,
  COUNT(*)                                AS total_elements,
  COUNT(*) FILTER (
    WHERE erp_item_id IS NOT NULL AND unit_cost IS NOT NULL
  )                                       AS attached_elements,
  ROUND(
    100.0 * COUNT(*) FILTER (
      WHERE erp_item_id IS NOT NULL AND unit_cost IS NOT NULL
    ) / NULLIF(COUNT(*), 0),
    1
  )                                       AS pct_complete
FROM read_parquet('lattice_bridge_ifc_ifc_elements.parquet')
GROUP BY project_id, boq_phase
ORDER BY project_id, boq_phase;
