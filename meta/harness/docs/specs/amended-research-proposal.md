---
title: "Amended Research Proposal — VW / iTwin / MARPA Bridge"
type: "spec"
status: "reference"
historical_only: true
source: "Vectorworks_Bentley_iTwin_MARPA_Research_20260508/Dev_Stack/amended_research_proposal.md"
---
# Amended Research Proposal: AI Automation and Digital Twins for Landscape Architecture

This amendment expands the prior research proposal to focus on how data-driven AI tools and digital twins are reshaping landscape architecture beyond construction, with emphasis on Claude Code integration, Bentley AI site design workflows, and practical AEC coding-agent adoption pathways.[cite:8][cite:12][cite:18][cite:22][cite:23]

## Expanded research objective

The updated objective is to evaluate how construction-oriented AI and automation systems can be adapted into a landscape architecture stack centered on Vectorworks, Bentley iTwin, and a web visualization layer using vis.gl, Three.js, and React Three Fiber.[cite:19][cite:22][cite:23] This includes studying agentic workflows, digital twins for living and changing sites, and practical methods for connecting open automation assets such as the DataDrivenConstruction skills ecosystem into Claude Code-based project operations.[cite:8][cite:9][cite:18]

## New research themes

### 1. Data-driven AI and digital twins beyond construction

Data-driven AI and digital twins are increasingly relevant to landscape architecture because landscapes are dynamic systems shaped by vegetation change, water, maintenance cycles, climate, and human use, which makes static CAD or BIM deliverables insufficient for long-term decision support.[cite:12][cite:18][cite:31] ASLA describes digital twin scenarios in landscape architecture such as drone- or camera-mediated site monitoring, where AI interprets visual data to detect invasive species or planting changes over time.[cite:18]

A 2026 study on renewable energy landscape planning proposes a digital twin-based planning and design method that integrates multisource data, feature matching between real and simulated scenes, and heterogeneous data assimilation to improve model accuracy and reliability.[cite:12] This is especially relevant to landscape practice because it frames digital twins not as a construction handoff artifact, but as a live planning environment for evolving terrain and ecological conditions.[cite:12]

### 2. Real-world cases and adoption challenges

The practical promise is clear, but adoption remains difficult because landscape digital twins require high-quality real-time data, sensor coverage across complex terrain, and efficient pipelines that can synchronize multimodal data with simulation and design models.[cite:12][cite:31] Urban landscape digital twin research also highlights implementation barriers around interoperability, model governance, and the complexity of maintaining live virtual counterparts of changing environments.[cite:31]

Useful case directions for deeper research include renewable energy landscape planning with digital twins, AI-assisted environmental monitoring, and infrastructure-adjacent landscape operations where site grading, drainage, and maintenance data can be continuously updated in a twin model.[cite:12][cite:18][cite:22] These use cases matter for landscape architecture firms because they align design, monitoring, and operations into one feedback loop instead of isolated project phases.[cite:18][cite:31]

### 3. Integrating the DDC Skills library into Claude Code for landscape projects

The DataDrivenConstruction ecosystem publishes an AI agents overview and a public GitHub profile, including a DDC Skills repository described as a large open skills library for construction tasks such as BIM analysis, cost estimation, and document workflows.[cite:8][cite:9] For landscape projects, the most relevant amendment is not to use the library unchanged, but to treat it as a starting skillpack that can be forked and reorganized into landscape-specific agent capabilities such as grading checks, planting schedule parsing, irrigation scope extraction, IFC/DWG normalization, and digital twin QA.[cite:8][cite:9]

A practical Claude Code integration path would include: storing selected DDC skills in a versioned project skill directory; rewriting prompts and instructions around landscape deliverables; binding those skills to local tools for IFC, DWG, GIS, point cloud, and tabular ETL; and adding project-level instructions so agents understand model authority, naming standards, and the target outputs required by the landscape pipeline.[cite:9][cite:28][cite:30] This direction aligns well with a Claude Code multi-agent harness for LATTICE, where specialized agents can own ingestion, schema normalization, site analysis, and visualization promotion across the spatial stack.[cite:34][cite:36][cite:38][cite:40][cite:41]

### 4. Digital twin applications in landscape architecture using construction AI

Construction AI can be repurposed for landscape architecture when the problem is framed around site state, change detection, optimization, and automated documentation rather than only vertical building workflows.[cite:18][cite:22][cite:23] Candidate applications include grading and drainage option generation, change detection from drone or site-camera imagery, planting health monitoring, erosion or invasive-species detection, field-to-model synchronization, and AI-assisted drawing or annotation generation for construction sets and maintenance packages.[cite:18][cite:22][cite:23]

This is particularly powerful when a digital twin acts as the shared context between authoring tools and web visualization. In that pattern, Vectorworks or CAD/BIM systems remain the source for authored geometry, Bentley iTwin or a similar twin layer manages federated context and reality alignment, and the web visualization stack becomes the analysis and user interaction surface.[cite:19][cite:22][cite:23][cite:34][cite:39][cite:40]

### 5. Bentley Systems AI agents for site design and grading optimization

Bentley has publicly positioned OpenSite+ as an AI-powered site design application with automated drawing production, grading optimization, and natural-language copilot capabilities for civil site design.[cite:22][cite:23] Bentley states that OpenSite+ can automate annotations, plan production, and grading optimization, and its announcement describes a design layout agent that evaluates thousands of layout options and supports one-click earthwork optimization.[cite:22][cite:23]

This matters directly to landscape architecture because site grading, drainage, circulation, pads, and pond geometry sit very close to civil site engineering workflows.[cite:23][cite:24] Bentley’s broader AI direction also points toward an ecosystem of specialized agents for site-grading optimization, hydraulic calculations, drawing automation, coding assistance, and data discovery within iTwin-native applications.[cite:13] The research amendment should therefore evaluate whether Bentley’s civil AI can be adapted for landscape grading studies, constructability checks, and sustainability-oriented earthwork balancing in site and campus-scale projects.[cite:13][cite:22][cite:23]

### 6. Tutorials and enablement for Cursor and Copilot in AEC automation

A practical AEC automation program also needs developer enablement. LinkedIn Learning offers a course on AI coding agents with GitHub Copilot and Cursor that covers agent mode, scope, command-line prompting, and custom instructions in both tools.[cite:28][cite:30] Cursor-focused guidance also exists for its Automations feature, where repository-watching agents can run background workflows triggered by file changes, test failures, schedules, or pull requests.[cite:26]

For AEC teams, the most valuable tutorial topics are likely to be custom instruction files, repository-scoped coding rules, automation triggers for repetitive ETL or validation tasks, and safe patterns for letting agents operate on BIM/GIS pipelines without breaking authoritative data.[cite:26][cite:28][cite:30] Research should therefore include not only product features but repeatable training materials and governance patterns for human review, branch protection, and prompt versioning.[cite:26][cite:30]

## Amendment to proposed research questions

1. How can data-driven AI and digital twins support landscape architecture workflows after design handoff, including maintenance, monitoring, ecological change detection, and adaptive site operations?[cite:12][cite:18][cite:31]
2. Which real-world digital twin case studies best demonstrate value in landscape planning, environmental monitoring, and infrastructure-adjacent site management, and what technical barriers slowed adoption?[cite:12][cite:18][cite:31]
3. What is the best method to integrate the DDC Skills repository into Claude Code as a landscape-specific skillpack for BIM, GIS, grading, planting, and digital twin workflows?[cite:8][cite:9][cite:28][cite:30]
4. How can Bentley OpenSite+ and iTwin-native AI features be used or adapted for grading optimization, drainage studies, site layout generation, and automated landscape documentation?[cite:13][cite:22][cite:23][cite:24]
5. What tutorial and workflow patterns for Cursor and GitHub Copilot are most effective for AEC automation teams working with CAD, BIM, GIS, and web visualization repositories?[cite:26][cite:28][cite:30]

## Recommended research links

### DataDrivenConstruction and DDC skills

- Main site: [datadrivenconstruction.io](https://datadrivenconstruction.io) [cite:1]
- AI agents overview: [AI Agents for Construction](https://datadrivenconstruction.io/ai-agents-for-construction/) [cite:8]
- GitHub profile: [github.com/datadrivenconstruction](https://github.com/datadrivenconstruction) [cite:3]
- DDC Skills repository: [DDC Skills for AI Agents in Construction](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction) [cite:9]

### Bentley AI and digital twins

- Bentley AI strategy overview: [Bentley Systems shapes its AI future](https://aecmag.com/ai/bentley-systems-shapes-its-ai-future/) [cite:13]
- Bentley OpenSite+: [AI-Powered Site Design Software](https://www.bentley.com/software/opensite-plus/) [cite:22]
- Bentley OpenSite+ announcement: [Generative AI game-changer for civil site design](https://www.bentley.com/news/bentley-systems-announces-generative-ai-game-changer-for-civil-site-design-2/) [cite:23]
- OpenSite Designer: [Site Design Software](https://www.bentley.com/software/opensite-designer/) [cite:24]

### Landscape digital twins and adoption

- Research paper: [Digital twin for renewable energy landscape planning and design](https://academic.oup.com/ijlct/article/doi/10.1093/ijlct/ctaf147/8487606) [cite:12]
- ASLA article: [Digital Twins and the Future of Landscape Architecture](https://www.asla.org/news-insights/the-field/looking-over-the-horizon-digital-twins-and-the-future-of-landscape-architecture) [cite:18]
- Adoption challenges: [Urban Landscape Digital Twin Implementation Challenges](https://juniperpublishers.com/ecoa/ECOA.MS.ID.555622.php) [cite:31]

### Cursor and Copilot tutorials

- LinkedIn Learning overview: [AI Coding Agents with GitHub Copilot and Cursor](https://www.linkedin.com/learning/ai-coding-agents-with-github-copilot-and-cursor/coding-with-agents) [cite:30]
- Cursor custom instructions lesson: [Adding custom instructions for Cursor](https://www.linkedin.com/learning/ai-coding-agents-with-github-copilot-and-cursor/adding-custom-instructions-for-cursor) [cite:28]
- Cursor automations guide: [Cursor Automations](https://www.digitalapplied.com/blog/cursor-automations-always-on-agentic-coding-agents-guide) [cite:26]

## Recommended implementation framing

The strongest framing for further research is to position landscape architecture as a next-wave beneficiary of construction AI rather than a downstream niche.[cite:12][cite:18][cite:23] In that framing, data-driven twins become continuous site intelligence systems, Bentley provides a powerful model for grading and site-design automation, the DDC Skills library becomes a reusable agent substrate for Claude Code, and the web visualization stack becomes the operational interface for analysis, coordination, and client-facing interaction.[cite:8][cite:9][cite:13][cite:22][cite:23][cite:34][cite:39][cite:40][cite:41]
