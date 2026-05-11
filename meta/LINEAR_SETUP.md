# Linear setup for LATTICE

End-state: Linear is the planning surface, GitHub Issues are the implementation surface, and changes in either direction sync automatically. `.github/workflows/linear-sync.yml` already forwards GitHub issue events to a Linear webhook — you just need to give it the webhook URL.

## 1. Create the Linear workspace

1. Sign in at https://linear.app/.
2. Create a workspace called **LATTICE** (or reuse an existing one and create a Team called LATTICE).
3. Inside the team, create one project per LATTICE area:
   - VW Bridge
   - 3D Viewer
   - Analytics Layer
   - Data Layer
   - Plant Geometry
   - Point Cloud
   - Agent Runtime
   - DevEx
4. Set the **Workflow states** to: `Backlog → Agent Ready → In Progress → In Review → Done → Canceled`.

## 2. Install the GitHub integration (bidirectional sync)

1. Linear → Settings → Integrations → GitHub → **Connect**.
2. Authorise the `JeromyJSmith/lattice-platform` repo.
3. In Linear, enable:
   - ☑ Create Linear issues from GitHub issues
   - ☑ Update GitHub issues when Linear issues change
   - ☑ Link PRs to Linear issues via branch name (`agent/123-slug` → issue 123)

## 3. Label → status mapping

In Linear → Settings → Integrations → GitHub → **Label sync**, map:

| GitHub label    | Linear status   |
|-----------------|-----------------|
| `agent-ready`   | Agent Ready     |
| `in-progress`   | In Progress     |
| `needs-review`  | In Review       |
| `blocked`       | Blocked (add)   |

LATTICE *area* labels (`vw-bridge`, `3d-viewer`, etc.) should be mapped to **projects**, not statuses.

## 4. Webhook for outbound sync (GitHub → Linear)

Linear's native GitHub integration handles most flows, but we also relay GitHub-side events to an additional Linear-hosted endpoint so we can fan out to other systems later.

1. Linear → Settings → API → **Personal API keys** → create a key called `lattice-ci`.
2. Linear → Settings → API → **Webhooks** → create a webhook:
   - Target URL: copy this — you'll paste it into GitHub
   - Resource types: ☑ Issue, ☑ Comment
3. Copy the webhook URL.

## 5. Add the webhook URL as a GitHub secret

```bash
gh secret set LINEAR_WEBHOOK_URL --body "<paste webhook URL here>"
```

Once that secret exists, `linear-sync.yml` will start forwarding `issue` events to Linear on every open/close/label.

## 6. Verify

1. Open an issue on GitHub.
2. Within ~10 seconds it should appear in Linear under the appropriate project.
3. Change the Linear status to "In Progress" — the GitHub issue should pick up the `in-progress` label.
4. Close the Linear issue — the GitHub issue should close.

If anything is one-way only, double-check the bidirectional toggles in step 2 and that the webhook URL secret is exactly the one Linear gave you (no trailing slash, no `?token=` cropped).
