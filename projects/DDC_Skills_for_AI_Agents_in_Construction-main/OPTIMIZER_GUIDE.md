# Optimizer Communication Guide

## How to Get Maximum Quality from DDC Skills

This guide defines the optimal communication patterns for working with Claude and the DDC Skills collection to achieve the best results in construction automation.

---

## Core Principles

### 1. Context is King

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT QUALITY PYRAMID                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                         ┌───────┐                               │
│                        /│RESULT │\                              │
│                       / │ Best  │ \                             │
│                      /  │Quality│  \                            │
│                     /   └───────┘   \                           │
│                    /                 \                          │
│                   /    ┌─────────┐    \                         │
│                  /     │EXAMPLES │     \                        │
│                 /      │ + Files │      \                       │
│                /       └─────────┘       \                      │
│               /                           \                     │
│              /        ┌─────────────┐      \                    │
│             /         │  CONSTRAINTS │      \                   │
│            /          │  + Standards │       \                  │
│           /           └─────────────┘         \                 │
│          /                                     \                │
│         /            ┌───────────────┐          \               │
│        /             │    PROJECT    │           \              │
│       /              │   CONTEXT     │            \             │
│      /               └───────────────┘             \            │
│     /                                               \           │
│    /                ┌─────────────────┐              \          │
│   /                 │ CLEAR OBJECTIVE │               \         │
│  /                  └─────────────────┘                \        │
│ ───────────────────────────────────────────────────────────     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Optimal Request Structure

```markdown
# Template for Maximum Quality Requests

## 1. OBJECTIVE (What do you need?)
[Clear, specific description of desired outcome]

## 2. CONTEXT (What's the situation?)
- Project: [Name, type, size]
- Phase: [Design/Preconstruction/Construction/Closeout]
- Constraints: [Budget, schedule, resources]
- Standards: [CSI, CWICR, regional codes]

## 3. INPUTS (What do you have?)
- Files: [List files with descriptions]
- Data sources: [ERP, BIM, spreadsheets]
- Previous work: [Reference past estimates/schedules]

## 4. OUTPUTS (What format do you need?)
- Format: [Excel, PDF, JSON]
- Structure: [Template reference if available]
- Level of detail: [Summary/Detailed/Line-item]

## 5. CONSTRAINTS (What are the limits?)
- Timeline: [When needed]
- Accuracy requirements: [Tolerance levels]
- Standards compliance: [Required certifications]

## 6. EXAMPLES (What does good look like?)
- Reference: [Similar past projects]
- Template: [Format to follow]
```

---

## Communication Patterns by Task Type

### Pattern 1: Cost Estimation Requests

```markdown
# OPTIMAL REQUEST

## Objective
Generate a detailed cost estimate for concrete foundation work.

## Context
- Project: 10-story office building in Munich, Germany
- Phase: Preconstruction (bid preparation)
- Trade: Division 03 - Concrete
- Regional factors: German labor rates, EU material costs

## Inputs
- IFC model: foundation_structural.ifc
- Specifications: 03_Concrete_Specs.pdf
- Geotechnical report: Soil_Report_2026.pdf

## Outputs
- Format: Excel with CWICR-mapped line items
- Structure: Following ÖNORM B 2061 format
- Level: Line-item with quantities and unit prices

## Constraints
- Must use DDC CWICR database for pricing
- 5% contingency required
- Exclude general conditions (handled separately)

## Examples
- Reference: Previous project estimate in /examples/foundation_estimate_sample.xlsx
```

```markdown
# SUB-OPTIMAL REQUEST (Avoid)

"Create an estimate for the foundation"

# Why this fails:
- No project context (location, size, type)
- No input files specified
- No format requirements
- No pricing basis defined
- No constraints specified
```

### Pattern 2: Schedule Optimization Requests

```markdown
# OPTIMAL REQUEST

## Objective
Optimize the MEP installation sequence to reduce critical path duration.

## Context
- Current schedule: 180 days for MEP rough-in
- Target: Reduce by 15% (to 153 days)
- Constraints: Only 2 crews available, no overtime

## Inputs
- Current schedule: MEP_Schedule_v3.mpp
- Space constraints: Floor plans showing shaft locations
- Resource data: Crew productivity rates

## Outputs
- Optimized schedule with resource leveling
- Comparison table (before/after)
- Risk analysis for accelerated sequence

## Constraints
- Cannot overlap electrical and plumbing in same zone
- Fire protection must precede ceiling closure
- Weekend work not permitted

## Analysis Required
- Identify parallel work opportunities
- Calculate resource conflicts
- Propose sequence changes with rationale
```

### Pattern 3: Document Processing Requests

```markdown
# OPTIMAL REQUEST

## Objective
Extract all RFIs from contractor correspondence and create a tracking log.

## Context
- Project: Healthcare facility renovation
- Communication period: Jan 2025 - Jan 2026
- Parties: Owner, Architect, 5 Trade Contractors

## Inputs
- Email archive: correspondence/emails_2025.pst
- Formal RFIs: correspondence/RFIs/*.pdf
- Meeting notes: meetings/*.docx

## Outputs
- Excel log with columns: RFI#, Date, From, Subject, Status, Response Date
- Summary statistics by trade and status
- Overdue RFI highlight report

## Extraction Rules
- Consider email subject with "RFI" or "Request for Information"
- Extract formal RFI number if present (format: RFI-XXXX)
- Identify response status from thread analysis
```

### Pattern 4: BIM Data Analysis Requests

```markdown
# OPTIMAL REQUEST

## Objective
Analyze BIM model for quantity takeoff accuracy vs. contractor bid quantities.

## Context
- BIM: Architect's design development model (LOD 300)
- Bid: Contractor's Excel QTO submission
- Discrepancy threshold: Flag if >5% variance

## Inputs
- IFC model: Architectural_DD_Model.ifc
- Contractor QTO: Bid_QTO_Contractor_A.xlsx
- Specification for measurement rules: QTO_Standards.pdf

## Outputs
- Comparison table: Element type, BIM qty, Bid qty, Variance %
- Discrepancy report with likely causes
- Visualization of major discrepancies

## Analysis Focus
- Concrete volumes (critical for cost)
- Steel tonnage (long lead time)
- Glazing area (specialty item)
- Drywall area (labor-intensive)
```

---

## Skill Invocation Best Practices

### 1. Explicit Skill Reference

```markdown
# GOOD - Explicit skill reference
"Use the semantic-search-cwicr skill to find matching work items
for the following scope description: ..."

# BETTER - Skill + parameters
"Use semantic-search-cwicr with:
- Language: German (DE)
- Category: 03 Concrete
- Limit: Top 20 matches
- Include: Unit prices and productivity rates"

# BEST - Skill + parameters + usage context
"Use semantic-search-cwicr to find matching CWICR items for
generating a cost estimate. I need:
- German language matches (DE)
- Category: 03 Concrete
- Top 20 matches with unit prices
- Purpose: Populating estimate template with regional pricing"
```

### 2. Skill Chaining

```markdown
# OPTIMAL - Explicit chain definition
"Execute the following skill chain:

1. EXTRACT: Use ifc-to-excel to extract quantities from model.ifc
2. CLASSIFY: Use semantic-search-cwicr to classify each element
3. PRICE: Apply CWICR unit prices to quantities
4. VALIDATE: Use verification-loop-construction to check output
5. FORMAT: Generate Excel output using xlsx-construction skill

Pass results between skills, preserving the element IDs for traceability."
```

### 3. Iterative Refinement

```markdown
# First pass - broad request
"Generate a cost estimate for the MEP scope"

# Second pass - refinement based on output
"The estimate looks good but:
- Electrical pricing seems low for German market
- Add 10% contingency to mechanical systems
- Break out fire protection as separate line item"

# Third pass - final adjustments
"Final adjustments:
- Update labor rates to 2026 tariffs
- Add escalation of 3% for 2027 construction start
- Format for client presentation (summary page first)"
```

---

## Context Optimization Techniques

### 1. Session Warm-Up

At the start of complex sessions, provide context upfront:

```markdown
# Session Context

## Project Overview
- Name: Berlin Central Station Renovation
- Type: Infrastructure / Transportation
- Value: €45M
- Duration: 24 months
- Current Phase: Detailed Design

## Standards & Requirements
- DIN 276 cost classification
- VOB/B contract terms
- German labor agreements (Bautarif)
- HOAI fee structure

## Key Files
- BIM Model: /models/BCSR_Architectural.ifc
- Specifications: /specs/01-35_Divisions.pdf
- Schedule: /schedule/Master_Schedule.mpp
- Budget: /budget/Budget_v5.xlsx

## Today's Tasks
1. Update cost estimate with latest design changes
2. Identify schedule impacts from architectural revisions
3. Prepare change order documentation

## Preferred Output Formats
- Estimates: Excel with DIN 276 structure
- Reports: PDF with company letterhead
- Data: JSON for API integration
```

### 2. Reference Previous Work

```markdown
"Similar to the estimate we created for Project ABC (see /previous/ABC_estimate.xlsx),
but with the following modifications:
- Different location (Munich vs. Berlin)
- Higher finish level (Class A vs. Class B office)
- Accelerated schedule (20% faster)"
```

### 3. Provide Anti-Examples

```markdown
"Generate an estimate, but:
- Do NOT include general conditions (they're handled separately)
- Do NOT use placeholder rates (use actual CWICR values)
- Do NOT summarize by CSI division (need line-item detail)
- Do NOT exceed €50/SF for finishes (budget constraint)"
```

---

## Error Recovery Patterns

### When Output Doesn't Match Expectations

```markdown
# Diagnostic request
"The output doesn't match what I expected. Let me clarify:

## Expected
- Line-item detail with quantities and unit prices
- German language descriptions
- €/unit pricing

## Received
- Summary level only
- English descriptions
- $/unit pricing

## Please Re-run With
- Use CWICR German database (DE)
- Output line-item level (not summarized)
- Convert all pricing to Euros
- Include quantity calculations"
```

### When Processing Fails

```markdown
# Debug request
"The IFC processing failed with error: [error message]

## Diagnostic Info
- File size: 450MB
- IFC version: 2x3
- Authoring tool: Revit 2024
- Elements: ~50,000

## Possible Issues
- File might be too large for memory
- Some elements might have invalid geometry
- Non-standard property sets

## Requested Action
- Try processing in chunks (by floor/level)
- Skip invalid geometries, log warnings
- Report which elements succeeded/failed"
```

---

## Quality Maximization Checklist

Before submitting any significant request:

### Context Completeness
- [ ] Project identified (name, type, location)
- [ ] Phase specified (design/construction/closeout)
- [ ] Standards identified (CSI, DIN, ÖNORM, etc.)
- [ ] Regional factors noted (labor rates, materials)

### Input Clarity
- [ ] All required files attached/referenced
- [ ] File formats and versions specified
- [ ] Data quality noted (clean/needs processing)
- [ ] Related context documents included

### Output Specification
- [ ] Format clearly defined (Excel, PDF, JSON)
- [ ] Structure specified (template reference)
- [ ] Detail level stated (summary/detailed)
- [ ] Validation requirements included

### Constraint Definition
- [ ] Accuracy requirements stated
- [ ] Exclusions clearly listed
- [ ] Timeline/urgency noted
- [ ] Budget/resource limits defined

### Success Criteria
- [ ] What "good" looks like defined
- [ ] Reference examples provided
- [ ] Validation steps specified
- [ ] Next steps after delivery clear

---

## Advanced Techniques

### 1. Multi-Agent Orchestration

```markdown
"For this complex task, orchestrate the following agents:

1. ESTIMATOR AGENT
   - Input: BIM model, specifications
   - Task: Generate QTO and initial pricing
   - Output: Preliminary estimate with CWICR mapping

2. VALIDATOR AGENT
   - Input: Preliminary estimate, historical data
   - Task: Validate quantities and pricing
   - Output: Validated estimate with confidence scores

3. SCHEDULER AGENT
   - Input: Validated estimate, production rates
   - Task: Generate resource-loaded schedule
   - Output: CPM schedule with resource histogram

4. REPORTER AGENT
   - Input: All above outputs
   - Task: Create integrated report
   - Output: Executive summary PDF

Coordinate agents sequentially, passing validated outputs between phases."
```

### 2. Verification Integration

```markdown
"After generating the estimate, automatically run verification:

1. Data Integrity: Check all formulas, totals, references
2. Business Logic: Validate markups, contingencies, escalation
3. Standards: Verify CWICR mappings, CSI codes
4. Cross-Reference: Compare to BIM quantities (allow 3% tolerance)
5. Output Quality: Check formatting, headers, print layout

If verification fails on any CRITICAL check, stop and report.
If WARNINGS only, include in output with recommendations."
```

### 3. Learning Integration

```markdown
"This is a new project type (data center construction) that we haven't
done before. As you process this estimate:

1. Note any new patterns discovered (cooling systems, power infrastructure)
2. Capture CWICR items that needed manual mapping
3. Record productivity assumptions for specialized work
4. Save decision rationales for future reference

At session end, export learnings to knowledge base for future data center projects."
```

---

## Quick Reference Card

```
┌──────────────────────────────────────────────────────────────────┐
│                    OPTIMIZER QUICK REFERENCE                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ✓ ALWAYS INCLUDE:                                               │
│    • Project context (type, location, phase)                     │
│    • Input files with descriptions                               │
│    • Desired output format                                       │
│    • Standards/constraints                                       │
│    • Success criteria                                            │
│                                                                   │
│  ✗ AVOID:                                                        │
│    • Vague requests ("make an estimate")                         │
│    • Missing context ("use appropriate rates")                   │
│    • Undefined outputs ("give me a report")                      │
│    • Implicit assumptions                                        │
│                                                                   │
│  SKILL INVOCATION:                                               │
│    /skill-name + parameters + context + expected output          │
│                                                                   │
│  ERROR RECOVERY:                                                 │
│    Expected vs. Received + Clarification + Retry Instructions    │
│                                                                   │
│  QUALITY ASSURANCE:                                              │
│    Always run /verify-construction before delivery               │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

*"The quality of output is directly proportional to the quality of input.
Invest time in request formulation to save time on iterations."*
