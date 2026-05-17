"""
Update all remaining SKILL.md files to ClawHub February 2026 format.
Adds: homepage, metadata fields to SKILL.md frontmatter.
Creates: claw.json, instructions.md for each skill.
"""
import os
import re
import json
from pathlib import Path

BASE = Path(r"C:\Users\Artem Boiko\Documents\GitHub\DDC_Skills_for_AI_Agents_in_Construction")
HOMEPAGE = "https://datadrivenconstruction.io"
AUTHOR = "datadrivenconstruction"

# Emoji mapping by category/subcategory
EMOJI_MAP = {
    # 1_DDC_Toolkit
    "Analytics": "📊",
    "BIM-Analysis": "🔍",
    "BIM-Visualization": "🖼️",
    "CAD-Converters": "📄",
    "Closeout": "✅",
    "Cost-Management": "💰",
    "CWICR-Database": "🗄️",
    "Document-Control": "📋",
    "Field-Operations": "🏗️",
    "Kaggle-Notebooks": "📓",
    "Procurement": "🛒",
    "Project-Closeout": "✅",
    "Resource-Management": "👷",
    "Schedule-Integration": "📅",
    "Schedule-Management": "📅",
    "Sustainability": "🌱",
    # 2_DDC_Book
    "1.1-Data-Evolution": "📚",
    "1.2-Data-Silos-Integration": "🔗",
    "2.1-Data-Types-Classification": "🏷️",
    "2.2-Open-Data-Standards": "🌐",
    "2.3-Pandas-LLM-Analysis": "🐼",
    "2.4-PDF-CAD-to-Data": "📑",
    "2.5-Data-Modeling-Standards": "📐",
    "2.6-Data-Quality-Validation": "✔️",
    "3.1-Cost-Estimation": "🧮",
    "3.2-QTO-Auto-Estimates": "⚡",
    "3.3-4D-BIM-CO2-Simulation": "🎬",
    "3.4-ERP-Integration": "🔄",
    "3.5-Interoperability": "🔀",
    "4.1-Analytics-KPI-Dashboard": "📈",
    "4.2-ETL-Automation": "⚙️",
    "4.3-BIM-Validation-Pipeline": "🔎",
    "4.4-Vector-Search-BigData": "🔢",
    "4.5-ML-Cost-Prediction": "🤖",
    "5.1-Digital-Maturity-Strategy": "🎯",
    # 3_DDC_Insights
    "AI-Agents": "🤖",
    "Automation-Workflows": "🔧",
    "Field-Automation": "📱",
    "Open-Data-Transparency": "🌍",
    "Safety-Quality": "🦺",
    "Schedule-Optimization": "⏱️",
    # 4_DDC_Curated
    "Contract-Legal": "📝",
    "Data-Validation": "✔️",
    "Document-Generation": "📄",
    "Financial-Management": "💵",
    "Prompt-Engineering": "💡",
    "Quality-Assurance": "🛡️",
    # 5_DDC_Innovative (top-level)
    "5_DDC_Innovative": "🚀",
}

# Keywords that indicate Windows-only
WIN32_KEYWORDS = [
    "RvtExporter", "DwgExporter", "DgnExporter", "RVT2IFCconverter",
    "Revit", ".rvt", "AutoCAD", "MicroStation", ".dgn",
    "revit_", "pyrevit",
]

# Keywords that indicate network permission needed
NETWORK_KEYWORDS = [
    "requests.get", "requests.post", "urllib", "httpx",
    "API_KEY", "api_key", "OPENAI_API", "QDRANT",
    "webhook", "REST API", "GraphQL", "endpoint",
    "telegram", "slack", "n8n",
]

# Keywords for specific binary requirements
BIN_REQUIREMENTS = {
    "python3": ["import ", "python", "pip install", "pandas", "numpy"],
    "tesseract": ["tesseract", "pytesseract", "OCR"],
    "ifcopenshell": ["ifcopenshell", "IfcOpenShell"],
    "IfcConvert": ["IfcConvert"],
}

# Keywords for env requirements
ENV_REQUIREMENTS = {
    "OPENAI_API_KEY": ["OPENAI_API_KEY", "openai.api_key", "OpenAI("],
    "QDRANT_URL": ["QDRANT_URL", "QdrantClient", "qdrant"],
}


def parse_frontmatter(content: str):
    """Parse YAML frontmatter from SKILL.md."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None, content

    fm_text = match.group(1)
    body = content[match.end():]

    # Parse simple YAML fields
    fm = {}
    for line in fm_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            fm[key] = value

    return fm, body


def get_subcategory(skill_path: Path) -> str:
    """Get the subcategory folder name."""
    rel = skill_path.relative_to(BASE)
    parts = list(rel.parts)
    # Structure: Category/Subcategory/skill-name/SKILL.md
    # or: Category/skill-name/SKILL.md (for 5_DDC_Innovative)
    if len(parts) >= 3:
        return parts[1]  # Subcategory
    return parts[0]  # Top-level category


def get_top_category(skill_path: Path) -> str:
    """Get the top-level category."""
    rel = skill_path.relative_to(BASE)
    return list(rel.parts)[0]


def determine_emoji(skill_path: Path, name: str) -> str:
    """Determine appropriate emoji for the skill."""
    subcat = get_subcategory(skill_path)
    topcat = get_top_category(skill_path)

    # Check subcategory first, then top category
    if subcat in EMOJI_MAP:
        return EMOJI_MAP[subcat]
    if topcat in EMOJI_MAP:
        return EMOJI_MAP[topcat]

    # Fallback based on name keywords
    if any(k in name for k in ["cost", "estimat", "budget", "price", "payment"]):
        return "💰"
    if any(k in name for k in ["schedule", "gantt", "4d", "timeline"]):
        return "📅"
    if any(k in name for k in ["safety", "inspection", "compliance"]):
        return "🦺"
    if any(k in name for k in ["report", "document", "pdf", "docx"]):
        return "📄"
    if any(k in name for k in ["bim", "ifc", "revit"]):
        return "🏗️"
    if any(k in name for k in ["ml", "predict", "ai", "neural"]):
        return "🤖"
    if any(k in name for k in ["data", "etl", "pipeline"]):
        return "📊"

    return "🔧"


def determine_os(content: str) -> list:
    """Determine OS compatibility."""
    for kw in WIN32_KEYWORDS:
        if kw in content:
            return ["win32"]
    return ["darwin", "linux", "win32"]


def determine_requires(content: str) -> dict:
    """Determine binary and env requirements."""
    requires = {}

    bins = []
    if any(kw in content for kw in BIN_REQUIREMENTS["python3"]):
        bins.append("python3")

    any_bins = []
    for bin_name, keywords in BIN_REQUIREMENTS.items():
        if bin_name == "python3":
            continue
        if any(kw in content for kw in keywords):
            any_bins.append(bin_name)

    env = []
    primary_env = None
    for env_name, keywords in ENV_REQUIREMENTS.items():
        if any(kw in content for kw in keywords):
            env.append(env_name)
            if not primary_env:
                primary_env = env_name

    if bins:
        requires["bins"] = bins
    if any_bins:
        requires["anyBins"] = any_bins
    if env:
        requires["env"] = env

    result = {"requires": requires}
    if primary_env:
        result["primaryEnv"] = primary_env

    return result


def determine_permissions(content: str) -> list:
    """Determine required permissions."""
    perms = ["filesystem"]
    if any(kw in content for kw in NETWORK_KEYWORDS):
        perms.append("network")
    return perms


def determine_tags(name: str, description: str, subcat: str, topcat: str) -> list:
    """Generate tags for the skill."""
    tags = ["construction"]

    tag_keywords = {
        "estimation": ["estimat", "cost", "price", "budget"],
        "BIM": ["bim", "ifc", "revit", "rvt"],
        "cost-management": ["cost", "budget", "payment", "invoice"],
        "scheduling": ["schedule", "gantt", "4d", "critical-path", "delay"],
        "data-processing": ["data", "etl", "pipeline", "csv", "json", "xml"],
        "safety": ["safety", "inspection", "compliance", "incident"],
        "reporting": ["report", "dashboard", "kpi", "analytics"],
        "machine-learning": ["ml", "predict", "neural", "model", "forecast"],
        "document-management": ["document", "pdf", "docx", "rfi", "submittal"],
        "quality": ["quality", "validation", "check", "verify"],
        "procurement": ["procurement", "bid", "material", "subcontractor"],
        "sustainability": ["carbon", "co2", "energy", "green", "lifecycle"],
        "automation": ["automat", "workflow", "n8n", "etl"],
        "CWICR": ["cwicr"],
        "GIS": ["gis", "coordinate", "spatial", "geo"],
        "CAD": ["cad", "dwg", "dgn", "drawing"],
    }

    combined = f"{name} {description} {subcat}".lower()
    for tag, keywords in tag_keywords.items():
        if any(kw in combined for kw in keywords):
            tags.append(tag)

    # Limit to 5 tags
    return tags[:5]


def generate_instructions(name: str, description: str, content: str) -> str:
    """Generate instructions.md for the skill."""
    # Extract the main action verb from description
    desc_lower = description.lower()

    if "convert" in desc_lower or "extract" in desc_lower:
        action = "convert or extract data"
    elif "estimat" in desc_lower or "cost" in desc_lower:
        action = "create cost estimates or analyze costs"
    elif "analyz" in desc_lower or "analysis" in desc_lower:
        action = "analyze data and generate insights"
    elif "generat" in desc_lower or "creat" in desc_lower:
        action = "generate documents or reports"
    elif "manag" in desc_lower or "track" in desc_lower:
        action = "manage and track project data"
    elif "validat" in desc_lower or "check" in desc_lower:
        action = "validate data quality and compliance"
    elif "predict" in desc_lower or "forecast" in desc_lower:
        action = "predict outcomes using data models"
    elif "schedul" in desc_lower:
        action = "manage schedules and timelines"
    elif "search" in desc_lower or "query" in desc_lower:
        action = "search and query data"
    else:
        action = "assist with construction project tasks"

    # Determine domain
    if "cwicr" in name:
        domain = "construction cost data using CWICR (Construction Work Item Cost Resource) database"
    elif "bim" in name or "ifc" in name or "rvt" in name:
        domain = "BIM (Building Information Modeling) data processing"
    elif "schedule" in name or "4d" in name or "gantt" in name:
        domain = "construction project scheduling"
    elif "safety" in name or "inspection" in name:
        domain = "construction safety and compliance"
    elif "cost" in name or "estimat" in name or "price" in name or "budget" in name:
        domain = "construction cost estimation and management"
    elif "report" in name or "document" in name or "pdf" in name:
        domain = "construction document management and reporting"
    elif "data" in name or "etl" in name or "pipeline" in name:
        domain = "construction data processing and analytics"
    elif "ml" in name or "predict" in name:
        domain = "machine learning for construction"
    elif "n8n" in name or "workflow" in name or "automat" in name:
        domain = "construction workflow automation"
    elif "material" in name or "procurement" in name:
        domain = "construction procurement and materials management"
    else:
        domain = "construction project management"

    instructions = f"""You are a construction industry assistant specializing in {domain}.

{description}

When the user asks to {action}:
1. Gather the required input data from the user
2. Process the data using the methods described in SKILL.md
3. Present results in a clear, structured format
4. Offer follow-up analysis or export options

## Input Format
- The user provides project data, file paths, or parameters as described in SKILL.md
- Accept data in common formats: CSV, Excel, JSON, or direct input

## Output Format
- Present results in structured tables when applicable
- Include summary statistics and key findings
- Offer export to Excel/CSV/JSON when relevant

## Key Reference
- See SKILL.md for detailed implementation code, classes, and methods
- Follow the patterns and APIs defined in the skill documentation

## Constraints
- Only use data provided by the user or referenced in the skill
- Validate inputs before processing
- Report errors clearly with suggested fixes
- Follow construction industry standards and best practices
"""
    return instructions


def build_metadata(emoji: str, os_list: list, homepage: str, requires_info: dict) -> str:
    """Build metadata JSON string."""
    metadata = {
        "openclaw": {
            "emoji": emoji,
            "os": os_list,
            "homepage": homepage,
            "requires": requires_info.get("requires", {})
        }
    }
    if "primaryEnv" in requires_info:
        metadata["openclaw"]["primaryEnv"] = requires_info["primaryEnv"]

    # Return as single-line JSON
    return json.dumps(metadata, ensure_ascii=False)


def build_claw_json(name: str, description: str, permissions: list, tags: list) -> dict:
    """Build claw.json content."""
    return {
        "name": name,
        "version": "2.0.0",
        "description": description,
        "author": AUTHOR,
        "license": "MIT",
        "permissions": permissions,
        "entry": "instructions.md",
        "tags": tags,
        "models": ["claude-*", "gpt-*"],
        "minOpenClawVersion": "0.8.0"
    }


def process_skill(skill_dir: Path):
    """Process a single skill directory."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None

    content = skill_md.read_text(encoding='utf-8')
    fm, body = parse_frontmatter(content)

    if not fm:
        return f"SKIP (no frontmatter): {skill_dir.name}"

    # Check if already updated
    if "homepage" in fm:
        return f"SKIP (already updated): {skill_dir.name}"

    # Get name (from 'name' or 'slug' field)
    name = fm.get("name", fm.get("slug", skill_dir.name))
    description = fm.get("description", "")

    # Remove display_name if present
    # Determine properties
    subcat = get_subcategory(skill_dir)
    topcat = get_top_category(skill_dir)
    emoji = determine_emoji(skill_dir, name)
    os_list = determine_os(content)
    requires_info = determine_requires(content)
    permissions = determine_permissions(content)
    tags = determine_tags(name, description, subcat, topcat)

    # Build metadata string
    metadata_str = build_metadata(emoji, os_list, HOMEPAGE, requires_info)

    # --- Update SKILL.md ---
    # Build new frontmatter
    new_fm_lines = [
        '---',
        f'name: "{name}"',
        f'description: "{description}"',
        f'homepage: "{HOMEPAGE}"',
        f'metadata: {metadata_str}',
        '---',
    ]
    new_content = '\n'.join(new_fm_lines) + '\n' + body
    skill_md.write_text(new_content, encoding='utf-8')

    # --- Create claw.json ---
    claw_json_path = skill_dir / "claw.json"
    if not claw_json_path.exists():
        claw_data = build_claw_json(name, description, permissions, tags)
        claw_json_path.write_text(
            json.dumps(claw_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    # --- Create instructions.md ---
    instructions_path = skill_dir / "instructions.md"
    if not instructions_path.exists():
        instructions = generate_instructions(name, description, content)
        instructions_path.write_text(instructions, encoding='utf-8')

    return f"OK: {name}"


def main():
    """Process all skills."""
    updated = 0
    skipped = 0
    errors = 0

    # Find all SKILL.md files
    skill_dirs = []
    for skill_md in BASE.rglob("SKILL.md"):
        skill_dirs.append(skill_md.parent)

    print(f"Found {len(skill_dirs)} skills total")
    print("=" * 60)

    for skill_dir in sorted(skill_dirs):
        try:
            result = process_skill(skill_dir)
            if result:
                print(result)
                if result.startswith("OK"):
                    updated += 1
                elif result.startswith("SKIP"):
                    skipped += 1
        except Exception as e:
            print(f"ERROR: {skill_dir.name} - {e}")
            errors += 1

    print("=" * 60)
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Errors:  {errors}")
    print(f"Total:   {updated + skipped + errors}")


if __name__ == "__main__":
    main()
