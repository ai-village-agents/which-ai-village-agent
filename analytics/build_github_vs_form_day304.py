#!/usr/bin/env python3
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
analytics = ROOT / "analytics"

GITHUB_PATH = analytics / "latest_share_url_summary.json"
FORM_PATH = analytics / "form_responses_day304.json"
OUT_JSON = analytics / "github_vs_form_day304.json"
OUT_MD = analytics / "github_vs_form_day304.md"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    gh = load_json(GITHUB_PATH)
    form = load_json(FORM_PATH)

    gh_totals = gh["totals"]
    gh_agents = gh["agents"]
    gh_dims = gh["dimension_means"]

    form_dims = form["dimension_means"]
    form_comp = form["computed_agent_counts"]
    form_dd = form["dropdown_counts"]

    # Build unified agent list
    agent_ids = sorted(set(gh_agents) | set(form_comp) | set(form_dd))

    alignment_agents = []
    for aid in agent_ids:
        alignment_agents.append(
            {
                "agent_id": aid,
                "form_computed": int(form_comp.get(aid, 0)),
                "form_dropdown": int(form_dd.get(aid, 0)),
                "github_valid_vectors": int(gh_agents.get(aid, 0)),
            }
        )

    alignment_dims = []
    for dim in sorted(form_dims.keys()):
        f_mean = float(form_dims[dim])
        g_mean = float(gh_dims.get(dim, 0.0))
        alignment_dims.append(
            {
                "dimension": dim,
                "form_mean": f_mean,
                "github_mean": g_mean,
                "github_minus_form": g_mean - f_mean,
            }
        )

    snapshot = {
        "alignment": {
            "agents": alignment_agents,
            "dimensions": alignment_dims,
        },
        "form_summary_path": str(FORM_PATH.relative_to(ROOT)),
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "github_issue": {
            "agent_counts": gh_agents,
            "authors_with_share_urls": gh_totals["authors_with_share_urls"],
            "authors_with_valid_vectors": gh_totals["authors_with_valid_vectors"],
            "comments": gh_totals["comments"],
            "dimension_means": gh_dims,
            "issue": gh["issue"],
            "share_urls_processed": gh_totals["share_urls_processed"],
            "unique_commenters": gh_totals["unique_commenters"],
            "valid_vectors": gh_totals["valid_vectors"],
        },
        "github_issue_summary_path": str(GITHUB_PATH.relative_to(ROOT)),
        "google_form": {
            "computed_agent_counts": form_comp,
            "dimension_means": form_dims,
            "dropdown_counts": form_dd,
            "total_responses": form["total_responses"],
            "valid_vectors": form["valid_vectors"],
        },
    }

    OUT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=False), encoding="utf-8")

    # Lightweight Markdown view
    lines = []
    lines.append("# GitHub vs Google Form Snapshot (Day 304, updated)\n")
    lines.append("")
    lines.append("## Overview\n")
    lines.append(
        f"- GitHub Issue #36: {gh_totals['comments']} comments, "
        f"{gh_totals['unique_commenters']} unique commenters, "
        f"{gh_totals['valid_vectors']} valid vectors ({gh_totals['authors_with_valid_vectors']} authors)"
    )
    lines.append(
        f"- Google Form: {form['total_responses']} responses, {form['valid_vectors']} valid vectors"
    )
    lines.append("")

    lines.append("## Agent alignment\n")
    lines.append("\n| Agent | GitHub valid vectors | Form (computed) | Form (dropdown) |\n|---|---:|---:|---:|")
    for a in alignment_agents:
        lines.append(
            f"| {a['agent_id']} | {a['github_valid_vectors']} | {a['form_computed']} | {a['form_dropdown']} |"
        )
    lines.append("")

    lines.append("## Dimension means (GitHub − Form)\n")
    lines.append(
        "\n| Dimension | GitHub mean | Form mean | GitHub − Form |\n|---|---:|---:|---:|"
    )
    for d in alignment_dims:
        lines.append(
            f"| {d['dimension']} | {d['github_mean']:.3f} | {d['form_mean']:.3f} | {d['github_minus_form']:.3f} |"
        )
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
