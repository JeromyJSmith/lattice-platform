<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# I have Redshift and Vectorworks on my computer but I don't think that I have Redshift installed as the plugin inside of Vectorworks, as I just installed it. I have the credentials maxonredshift.vwlibrary and the redshift for vectorworks.vwlibrary right here. How do I insert those? Do I just drag and drop? Do I have to put it in before I pull it out? How does that work?

You do not manually drag those `.vwlibrary` files into Vectorworks; Redshift for Vectorworks is installed and wired up via the Maxon App and then enabled through the Vectorworks Workspace editor, not by copying plugin files around yourself.[^1_1][^1_2]

## How Redshift for Vectorworks is supposed to be installed

On current builds, the expected flow is:

1. Install or update Vectorworks (2026+ recommended) using default paths.[^1_2]
2. Install the Maxon App, sign in with your Maxon/MyMaxon account, and make sure your Redshift license is assigned there.[^1_3][^1_2]
3. From the Maxon App, install Redshift and make sure the Vectorworks host/plugin option is checked during installation so it configures the Vectorworks integration automatically.[^1_1][^1_2]

Once that’s done, Vectorworks will have the Redshift tools and the plugin already present; you do not need to “insert” `.vwlibrary` files by hand.[^1_1]

## Enabling the Redshift tools inside Vectorworks

If Redshift is installed correctly but you don’t see it in your palettes, you add it via the Workspace Editor, not by file copy:

1. Open Vectorworks.
2. Go to the “Basic” tools palette, click the hamburger ☰ menu, and choose **Customize…** to open the Workspace Editor.[^1_2][^1_1]
3. In the Workspace Editor, select your current workspace.
4. In the left-hand **Tools** list, look under the **Rendering** category and find **Maxon Redshift** / **Redshift**.[^1_2][^1_1]
5. Drag that entry into the right-hand list where your tool palettes are, placing it in the Basic or another palette as desired.[^1_1][^1_2]
6. Click OK; Vectorworks redraws, and the Redshift tool should now appear in your palette.[^1_2][^1_1]

From there you can launch the Redshift viewer / real‑time renderer directly from within Vectorworks.[^1_4][^1_1]

## About those `.vwlibrary` files

The `maxonredshift.vwlibrary` and `redshift for vectorworks.vwlibrary` files you see are Vectorworks library containers.
They are not the primary plugin installer and are normally placed/managed by the Redshift installer itself in the appropriate Vectorworks library folders.[^1_1][^1_2]

Because of that:

- You should **not** drag-and-drop them blindly into Vectorworks or random folders.
- You generally **do not** need to place them manually at all if you let the Maxon App install Redshift for Vectorworks.

If you already ran the Maxon App but think it didn’t wire into Vectorworks, the clean route is:

1. In the Maxon App, uninstall Redshift.
2. Reinstall Redshift, ensuring the Vectorworks host option is enabled during installation.[^1_5][^1_2][^1_1]

After that, open Vectorworks and use the Workspace Editor steps above to expose the tools.

Would you like step‑by‑step specific to macOS vs Windows, and which exact Vectorworks version you’re on? That affects the exact menu paths and install locations.
<span style="display:none">[^1_10][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://help.maxon.net/rva/en-us/Content/html/Installation_and_Setup.html

[^1_2]: https://www.maxon.net/en/archviz

[^1_3]: https://forum.vectorworks.net/index.php?%2Ftopic%2F132283-2026-maxon-redshift-for-vectorworks%2F

[^1_4]: https://www.vectorworks.net/en-US/maxon-redshift-for-vectorworks

[^1_5]: https://help.maxon.net/r3d/maya/en-us/Content/html/Installing+Redshift+on+Windows.html

[^1_6]: https://forum.vectorworks.net/index.php?%2Ftopic%2F116729-redshift-interactive-mode%2F

[^1_7]: https://www.linkedin.com/posts/kevin-malig-186563235_architecture-aec-designinnovation-activity-7379177311369101312-hfNN

[^1_8]: https://www.engineering.com/maxon-releases-redshift-plugins-for-vectorworks-and-revit/

[^1_9]: https://university.vectorworks.net/course/view.php?id=4327

[^1_10]: https://www.youtube.com/playlist?list=PLlC-bZ5BfsQ2pMKMtIyOQ7se58ldkcPrM


---

# No worries at all, I've got you! Since you're looking to integrate these [DDC Skills](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction) into your own project section, here are the exact commands you need to run in your terminal.

1. Clone the Repository
First, you'll want to grab the entire collection. This command clones the repo into a folder named ddc_skills_temp:
Bash
git clone [https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction.git](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction.git) ddc_skills_temp
2. Create Your Project Section
If you don't already have a specific directory for these in your project, create one (let’s call it ai_skills):
Bash
mkdir -p your_project_path/ai_skills
3. Move the Skills Over
Instead of keeping the whole bulky repo, you can move just the core skill folders into your project's new section:
Bash
mv ddc_skills_temp/1_DDC_Toolkit your_project_path/ai_skills/
mv ddc_skills_temp/2_DDC_Book your_project_path/ai_skills/
mv ddc_skills_temp/3_DDC_Insights your_project_path/ai_skills/
4. Install Dependencies
These skills rely on a few specific Python libraries to handle BIM models (IFC), Excel files, and PDFs. Run this to make sure your environment is ready:
Bash
pip install pandas openpyxl ifcopenshell pdfplumber

Quick Tip for the "Lazy" Workflow:
The beauty of this setup is that you don't really "run" these like standard software.
Step 1: Open your project in an AI-powered editor (like Cursor or VS Code with Claude Dev).
Step 2: Point the AI to a specific SKILL.md file inside those folders.
Step 3: Tell the AI: "Read this skill and implement it using my project's data."
It basically does the coding for you based on the instructions in those files! Is there a specific construction task (like IFC to Excel or Cost Estimation) you want to try first?

Those commands are **plausible as a manual clone-and-copy workflow**, but I would not treat them as verified installation instructions for that repo without checking the project’s own README or install method first.[^2_1][^2_2]

## What looks correct

Cloning the repo and copying selected folders into your own project is a normal Git-based way to vendor reusable skill content, and the repo is publicly associated with the `datadrivenconstruction` GitHub organization.[^2_2]
The repo appears to be a collection of many construction-focused agent skills, with public descriptions mentioning BIM analysis, cost estimation, scheduling, and document control use cases.[^2_1]

## What is not yet verified

I could not confirm from the repo’s own fetched README whether the top-level folders are exactly `1_DDC_Toolkit`, `2_DDC_Book`, and `3_DDC_Insights`, so those `mv` commands may or may not match the current repository layout.[^2_2][^2_1]
I also could not verify that `pandas openpyxl ifcopenshell pdfplumber` are the official required dependencies for the entire repo, although those packages are consistent with the kinds of tasks the skills describe, such as IFC/BIM handling, spreadsheet work, and PDF extraction.[^2_3][^2_4][^2_1]

## Safer terminal workflow

A more cautious approach is to clone first, inspect the folder structure, and only then move or copy what you need:

```bash
git clone https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction.git ddc_skills_temp
cd ddc_skills_temp
find . -maxdepth 2 -type f -name "SKILL.md" | sort
find . -maxdepth 2 -type d | sort
```

That lets you confirm the current directory names before writing `mv` commands, which is safer than assuming the structure in advance.[^2_2]
If you want the skills inside a project folder after inspection, `cp -R` is usually safer than `mv` because it preserves the cloned source as a reference copy.[^2_2]

## Recommended version

I’d rewrite your instructions like this:

```bash
git clone https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction.git ddc_skills_temp
mkdir -p your_project_path/ai_skills
cd ddc_skills_temp
find . -maxdepth 2 -type f -name "SKILL.md" | sort
```

Then, after you confirm the exact folder names:

```bash
cp -R ./EXACT_FOLDER_NAME_1 your_project_path/ai_skills/
cp -R ./EXACT_FOLDER_NAME_2 your_project_path/ai_skills/
cp -R ./EXACT_FOLDER_NAME_3 your_project_path/ai_skills/
```

For Python packages, install only what the specific skills you plan to use actually require; IFC-related workflows commonly rely on IfcOpenShell, and PDF extraction workflows commonly use pdfplumber, but different skills may need different stacks.[^2_4][^2_3]

## About the “lazy workflow”

The high-level idea is right: agent skill repos are generally consumed as instruction bundles that an AI coding assistant reads and applies, rather than as traditional end-user software you “launch.”[^2_5][^2_6]
So the practical workflow is usually: place the skill folders where your AI-enabled editor or agent can access them, point the agent to a specific `SKILL.md`, and then ask it to execute that procedure against your own files or project context.[^2_6][^2_5]

The main correction is this: I would present the commands as **a suggested manual integration pattern**, not as “the exact commands you need,” unless you first confirm the repo’s current folder names and official install guidance.[^2_2]
<span style="display:none">[^2_10][^2_11][^2_12][^2_13][^2_14][^2_7][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://shyft.ai/skills/ddc-skills-for-ai-agents-in-construction

[^2_2]: https://github.com/datadrivenconstruction

[^2_3]: https://timmcginley.github.io/41934/Concepts/IfcOpenShell/

[^2_4]: https://www.pdfplumber.com/how-can-i-install-pdfplumber-on-my-system/

[^2_5]: https://github.com/WordPress/agent-skills/blob/trunk/README.md

[^2_6]: https://github.com/heilcheng/awesome-agent-skills

[^2_7]: https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction/pulls

[^2_8]: https://github.com/debs-obrien/learn-agent-skills

[^2_9]: https://github.com/maragudk/skills

[^2_10]: https://github.com/clerk/skills

[^2_11]: https://github.com/AminAlam/meddev-agent-skills

[^2_12]: https://www.verified-skill.com/skills/datadrivenconstruction/ddc_skills_for_ai_agents_in_construction/batch-cad-converter

[^2_13]: https://github.com/ChingChing77/openclaw-macmini-allskills/blob/main/pandas-construction-analysis/SKILL.md

[^2_14]: https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction/blob/main/2_DDC_Book/2.4-PDF-CAD-to-Data/drawing-analyzer/SKILL.md

