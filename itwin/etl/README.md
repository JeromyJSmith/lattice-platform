# iModel ETL (extract / transform / load)

Patterns for extracting subsets from collaborator-provided iModels and merging them into LATTICE's Pixeltable bridge tables.

LATTICE doesn't run iModels long-term — collaborators may, and we accept their `.bim` files at the boundary. Use [`@itwin/imodel-transformer`](https://github.com/iTwin/imodel-transformer) (see [`meta/ITWIN_MAPPING.md`](../../meta/ITWIN_MAPPING.md) Tier 1) for:

- **Extract** a landscape-element subset from a large multi-discipline iModel
- **Merge** two collaborator iModels into one combined extract
- **Transform** coordinates / units / property names before LATTICE consumes the rows

Scripts go here as `.ts` files runnable with `bun etl/<name>.ts`. Each script must be idempotent and write evidence rows to `lattice/execution/evidence` so re-runs are auditable.
