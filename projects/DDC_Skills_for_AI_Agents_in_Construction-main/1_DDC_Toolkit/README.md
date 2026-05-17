# DDC_Toolkit

**Professional-grade tools and databases from DataDrivenConstruction.io**

Skills in this category are based on production-ready tools and databases developed by DDC team.

## Source Repositories

| Repository | Description | Stars |
|------------|-------------|-------|
| [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR) | Construction cost database with 55,719 work items | Open Source |
| [cad2data Pipeline](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto) | CAD/BIM conversion and validation tools | Open Source |
| [Revit-IFC-Creating-images](https://github.com/datadrivenconstruction/Revit-IFC-Creating-images) | noBIM visualization tool | Open Source |

## Additional Resources

### Kaggle Notebooks
- [5000 Projects IFC & RVT Analysis](https://www.kaggle.com/code/artemboiko/5000-projects-ifc-rvt-datadrivenconstruction-io) - Large-scale BIM data analysis
- [Comparison of Two Revit/IFC Projects](https://www.kaggle.com/code/artemboiko/comparison-of-two-revit-or-ifc-projects) - Project comparison methodology
- [Data Processing from Revit and IFC](https://www.kaggle.com/code/artemboiko/example-of-data-processing-from-revit-and-ifc) - ETL examples

### Database Releases
- [DDC CWICR v0.1.0](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR/releases) - 55,719 work items, 9 languages

## Skill Categories

### CWICR-Database
Cost estimation and semantic search using DDC CWICR database.

### CAD-Converters
File conversion tools: Revit, IFC, DWG, DGN → Excel, CSV, Parquet.

### Kaggle-Notebooks
Data analysis and visualization workflows from Kaggle examples.

### BIM-Visualization
Image and report generation from BIM models using noBIM tool.

## Key Capabilities

```
┌─────────────────────────────────────────────────────────────────┐
│                     DDC TOOLKIT CAPABILITIES                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [CWICR DATABASE]        [CAD CONVERTERS]       [NOTEBOOKS]     │
│  ┌─────────────┐        ┌─────────────┐        ┌──────────┐     │
│  │ 55,719      │        │ RvtExporter │        │ 5000     │     │
│  │ Work Items  │        │ IfcExporter │        │ Projects │     │
│  │ 9 Languages │        │ DwgExporter │        │ Analysis │     │
│  │ Qdrant DB   │        │ DgnExporter │        │          │     │
│  └─────────────┘        └─────────────┘        └──────────┘     │
│         │                      │                     │          │
│         ▼                      ▼                     ▼          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              CONSTRUCTION DATA PIPELINE                  │    │
│  │    Cost Estimation → QTO → Scheduling → Reporting       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Install dependencies
pip install pandas qdrant-client openai openpyxl

# Semantic search in CWICR
from qdrant_client import QdrantClient
client = QdrantClient("localhost", port=6333)
results = client.search(collection_name="ddc_cwicr_en", query_vector=embedding, limit=10)

# Convert Revit to Excel
RvtExporter.exe "project.rvt" complete bbox
```

## License

- **Database**: CC BY 4.0 (free commercial use with attribution)
- **Tools**: MIT License
