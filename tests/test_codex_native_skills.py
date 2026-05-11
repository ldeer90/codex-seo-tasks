"""Tests for Codex-native LD SEO skill routing and installed entrypoints."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import sync_codex_skills  # noqa: E402


SKILLS = ROOT / "docs" / "agent" / "skills"
WORKFLOWS = ROOT / "docs" / "agent" / "workflows"
CLIENTS = ROOT / "docs" / "agent" / "clients"
ROUTING_MANIFEST = ROOT / "docs" / "agent" / "routing-manifest.json"
SCRIPTS_INDEX = ROOT / "docs" / "agent" / "scripts-index.md"
PROOF_TEMPLATES = ROOT / "docs" / "agent" / "proof-block-templates.md"
ARCHITECTURE_DIAGRAMS = ROOT / "docs" / "agent" / "skill-architecture-diagrams.md"


CANONICAL_SKILLS = {
    "ld-seo-command-menu",
    "ld-seo-client-onboarding",
    "ld-seo-collection-seo",
    "ld-seo-content-briefs",
    "ld-seo-content-writing",
    "ld-seo-shopify-collection-writing",
    "ld-seo-shopify-blog-writing",
    "ld-seo-audits-reporting",
    "ld-seo-maintenance",
}

PRODUCTION_WORKFLOWS = [
    "blog-content-writing.md",
    "collection-content-writing.md",
    "collection-content-briefs.md",
    "collection-seo-full.md",
    "keyword-research-collections.md",
    "onpage-title-h1-suggestions.md",
    "competitor-keyword-research.md",
    "monthly-combined-report.md",
    "full-site-audit.md",
    "single-page-audit.md",
    "ga4-traffic-check.md",
    "gsc-opportunity-mining.md",
    "internal-linking-opportunities.md",
    "technical-site-audit-seranking.md",
    "ai-search-tracking.md",
    "seo-roadmap-prioritisation.md",
]


def _read(path: Path) -> str:
    return path.read_text()


def _frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert match, "missing frontmatter"
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def _manifest() -> dict:
    return json.loads(_read(ROUTING_MANIFEST))


def test_canonical_ld_seo_skills_exist_with_valid_frontmatter() -> None:
    for skill in CANONICAL_SKILLS:
        skill_md = SKILLS / skill / "SKILL.md"
        assert skill_md.exists(), f"missing {skill_md}"
        fields = _frontmatter(_read(skill_md))
        assert fields["name"] == skill
        assert fields["description"]


def test_codex_menu_routes_without_claude_command_dependency() -> None:
    text = _read(SKILLS / "ld-seo-command-menu" / "SKILL.md")
    assert "legacy reference only" in text
    assert ".claude/commands/" in text
    assert "Do not read `.claude/commands/` for normal operation" in text

    expected_routes = {
        "/ldseo-content": "docs/agent/workflows/collection-content-briefs.md",
        "/ldseo-metadata": "docs/agent/workflows/onpage-title-h1-suggestions.md",
        "/ldseo-hygiene": "docs/agent/workflows/se-ranking-hygiene.md",
        "/ldseo-monthly-report": "docs/agent/workflows/monthly-performance-comment.md",
        "Explicit Doc + Sheet report request": "docs/agent/workflows/monthly-combined-report.md",
        "Final collection copy": "docs/agent/workflows/collection-content-writing.md",
        "Final blog copy": "docs/agent/workflows/blog-content-writing.md",
    }
    for command, workflow in expected_routes.items():
        assert command in text
        assert workflow in text
        assert (ROOT / workflow).exists()


def test_skill_index_declares_repo_skills_canonical() -> None:
    text = _read(SKILLS / "_index.md")
    assert "Codex-native skills in this directory are the canonical" in text
    assert "routing-manifest.json" in text
    assert "scripts-index.md" in text
    assert "proof-block-templates.md" in text
    assert "skill-architecture-diagrams.md" in text
    assert "_routing-contract.md" in text
    assert "installed Codex skill entrypoints" in text
    assert ".claude/commands/` is legacy reference only" in text
    for skill in CANONICAL_SKILLS:
        assert f"{skill}/SKILL.md" in text


def test_routing_manifest_covers_canonical_skills_and_paths() -> None:
    manifest = _manifest()
    assert manifest["version"] == 1
    assert "low-token" in manifest["purpose"].lower()
    assert ".claude/commands" not in json.dumps(manifest)

    skills = manifest["skills"]
    assert set(skills) == CANONICAL_SKILLS

    for label, ref in manifest["canonical_sources"].items():
        path = ROOT / ref
        assert path.exists(), f"{label} points to missing path: {ref}"

    for skill, entry in skills.items():
        assert entry["commands_or_intents"], skill
        assert entry["skill_doc"] == f"docs/agent/skills/{skill}/SKILL.md"
        assert (ROOT / entry["skill_doc"]).exists(), skill
        assert entry["workflow_docs"], skill
        assert entry["required_preflight_reads"], skill
        assert isinstance(entry["client_memory_required"], bool), skill
        assert "proof_block_fields" in entry and entry["proof_block_fields"], skill
        assert "handoff_routes" in entry, skill

        for workflow in entry["workflow_docs"]:
            assert (ROOT / workflow).exists(), f"{skill} references missing {workflow}"
        for script in entry["scripts"] + entry["validators"]:
            assert script.startswith("scripts/"), f"{skill} has non-script path {script}"
            assert (ROOT / script).exists(), f"{skill} references missing {script}"


def test_routing_manifest_matches_menu_routes_and_production_gates() -> None:
    manifest = _manifest()
    menu = _read(SKILLS / "ld-seo-command-menu" / "SKILL.md")
    index = _read(SKILLS / "_index.md")

    expected_skill_workflows = {
        "ld-seo-client-onboarding": ["docs/agent/workflows/add-new-client.md"],
        "ld-seo-maintenance": [
            "docs/agent/workflows/se-ranking-hygiene.md",
            "docs/agent/workflows/troubleshoot-access.md",
        ],
        "ld-seo-collection-seo": [
            "docs/agent/workflows/collection-seo-full.md",
            "docs/agent/workflows/keyword-research-collections.md",
            "docs/agent/workflows/competitor-keyword-research.md",
            "docs/agent/workflows/onpage-title-h1-suggestions.md",
        ],
        "ld-seo-content-briefs": ["docs/agent/workflows/collection-content-briefs.md"],
        "ld-seo-shopify-collection-writing": [
            "docs/agent/workflows/collection-content-writing.md"
        ],
        "ld-seo-shopify-blog-writing": ["docs/agent/workflows/blog-content-writing.md"],
        "ld-seo-audits-reporting": [
            "docs/agent/workflows/single-page-audit.md",
            "docs/agent/workflows/full-site-audit.md",
            "docs/agent/workflows/monthly-performance-comment.md",
            "docs/agent/workflows/ga4-traffic-check.md",
            "docs/agent/workflows/monthly-combined-report.md",
        ],
    }

    for skill, workflows in expected_skill_workflows.items():
        actual = set(manifest["skills"][skill]["workflow_docs"])
        for workflow in workflows:
            assert workflow in actual, f"{skill} missing {workflow}"
            assert workflow in menu or workflow in index, workflow

    production_skills = set(expected_skill_workflows) - {"ld-seo-command-menu"}
    for skill in production_skills:
        entry = manifest["skills"][skill]
        assert entry["write_gates"], skill
        assert entry["readback_requirements"], skill
        assert entry["mcp_dependencies"] or skill.startswith("ld-seo-shopify"), skill
        if skill != "ld-seo-content-writing":
            assert entry["validators"], skill


def test_scripts_index_documents_all_scripts() -> None:
    text = _read(SCRIPTS_INDEX)
    assert "Do not run directly" in text
    assert "Mutates repo files?" in text
    assert "do not run when" in text.lower()

    for script in sorted(path.name for path in SCRIPTS.glob("*.py")):
        assert f"`scripts/{script}`" in text, f"{script} missing from scripts index"


def test_proof_templates_cover_production_workflows_and_architecture_link_exists() -> None:
    proof = _read(PROOF_TEMPLATES)
    manifest_text = _read(ROUTING_MANIFEST)
    scripts_index = _read(SCRIPTS_INDEX)
    skill_index = _read(SKILLS / "_index.md")
    command_menu = _read(SKILLS / "ld-seo-command-menu" / "SKILL.md")

    assert ARCHITECTURE_DIAGRAMS.exists()
    for text in (manifest_text, skill_index, command_menu):
        assert "skill-architecture-diagrams.md" in text
    assert "routing-manifest.json" in scripts_index

    for workflow in PRODUCTION_WORKFLOWS + [
        "add-new-client.md",
        "monthly-performance-comment.md",
        "regenerate-platform-reference.md",
        "report-filing.md",
        "se-ranking-hygiene.md",
        "troubleshoot-access.md",
    ]:
        assert f"`{workflow}`" in proof, f"{workflow} missing proof template mapping"

    for section in (
        "Onboarding",
        "Maintenance",
        "Collection SEO",
        "Content Briefs",
        "Collection HTML",
        "Blog HTML",
        "Audits And Reporting",
        "Monthly Performance Comment",
    ):
        assert f"## {section}" in proof


def test_shared_routing_contract_covers_dependency_graph() -> None:
    text = _read(SKILLS / "_routing-contract.md")
    required_routes = [
        "ld-seo-client-onboarding",
        "ld-seo-maintenance",
        "ld-seo-collection-seo",
        "collection-seo-qa",
        "ld-seo-content-briefs",
        "ld-seo-shopify-collection-writing",
        "ld-seo-shopify-blog-writing",
        "google-drive:google-docs",
    ]
    for route in required_routes:
        assert route in text
    for gate in ("Preflight", "Missing-Input Routing", "Write Gate", "Output Gate"):
        assert f"## {gate}" in text
    assert "docs/agent/client-memory.md" in text
    assert "<client>-timeline.md" in text
    assert "Append the client timeline" in text


def test_all_canonical_skills_reference_routing_contract_and_handoffs() -> None:
    for skill in CANONICAL_SKILLS:
        text = _read(SKILLS / skill / "SKILL.md")
        assert "docs/agent/skills/_routing-contract.md" in text
        assert "docs/agent/client-memory.md" in text, skill
        assert re.search(r"client timeline|<client>-timeline", text, flags=re.I), skill
        assert re.search(r"append (the )?(client )?timeline", text, flags=re.I), skill
        assert "## Preflight And Handoff" in text
        assert "Proof Block" in text
        assert re.search(r"validat|validator|zero blockers", text, flags=re.I), skill
        assert re.search(r"read back|Read back|Drive/Monday state verified", text), skill


def test_content_writing_router_points_to_dedicated_skills() -> None:
    text = _read(SKILLS / "ld-seo-content-writing" / "SKILL.md")
    assert "ld-seo-shopify-collection-writing" in text
    assert "ld-seo-shopify-blog-writing" in text
    assert "docs/agent/workflows/collection-content-writing.md" in text
    assert "docs/agent/workflows/blog-content-writing.md" in text


def test_blog_writing_has_preflight_and_dependency_routing() -> None:
    skill = _read(SKILLS / "ld-seo-shopify-blog-writing" / "SKILL.md")
    workflow = _read(WORKFLOWS / "blog-content-writing.md")

    assert "preflight gate" in skill
    assert "## Phase 0 - Access And Input Preflight" in workflow
    assert "### Missing-input routing" in workflow
    required_checks = [
        "Drive destination",
        "Monday board schema",
        "client writing style guide",
        "SE Ranking access",
        "Search Console",
    ]
    for check in required_checks:
        assert check in workflow

    dependent_skills = [
        "ld-seo-client-onboarding",
        "ld-seo-maintenance",
        "ld-seo-content-briefs",
        "ld-seo-shopify-collection-writing",
        "google-drive:google-docs",
    ]
    for dependent_skill in dependent_skills:
        assert dependent_skill in workflow


def test_new_workflows_are_indexed_and_include_quality_controls() -> None:
    index = _read(WORKFLOWS / "_index.md")
    workflows = [
        "blog-content-writing.md",
        "collection-content-writing.md",
        "gsc-opportunity-mining.md",
        "internal-linking-opportunities.md",
        "technical-site-audit-seranking.md",
        "ai-search-tracking.md",
        "seo-roadmap-prioritisation.md",
    ]
    for workflow in workflows:
        assert workflow in index
        text = _read(WORKFLOWS / workflow)
        assert "## Quality Gate" in text
        assert "## Proof Block" in text
        assert "Codex judgement" in text


def test_production_workflows_include_preflight_routing_and_qa() -> None:
    for workflow in PRODUCTION_WORKFLOWS:
        text = _read(WORKFLOWS / workflow)
        assert "Phase 0" in text or "## Pre-flight" in text, workflow
        assert "Missing-input routing" in text, workflow
        assert re.search(r"validat|Quality Gate|Read back|readback|read back", text, flags=re.I), workflow
        assert re.search(r"proof block", text, flags=re.I), workflow


def test_production_workflows_include_client_memory_timeline_rules() -> None:
    for workflow in PRODUCTION_WORKFLOWS:
        text = _read(WORKFLOWS / workflow)
        assert "docs/agent/client-memory.md" in text, workflow
        assert re.search(r"client timeline|<client>-timeline", text, flags=re.I), workflow
        assert re.search(r"append (the )?client timeline|Client timeline updated|client timeline update status", text, flags=re.I), workflow


def test_onboarding_and_monthly_reporting_use_client_timelines() -> None:
    onboarding = _read(WORKFLOWS / "add-new-client.md")
    monthly = _read(WORKFLOWS / "monthly-performance-comment.md")

    assert "CLIENT_TIMELINE_TEMPLATE.md" in onboarding
    assert "<slug>-timeline.md" in onboarding
    assert "Append the client timeline" in onboarding

    assert "docs/agent/client-memory.md" in monthly
    assert "<client>-timeline.md" in monthly
    assert "prior timeline entries" in monthly
    assert "Append the client timeline" in monthly


def test_common_missing_input_routes_are_documented() -> None:
    contract = _read(SKILLS / "_routing-contract.md")
    blog = _read(WORKFLOWS / "blog-content-writing.md")
    metadata = _read(WORKFLOWS / "onpage-title-h1-suggestions.md")
    keyword_research = _read(WORKFLOWS / "keyword-research-collections.md")

    assert "client sidecar" in contract and "ld-seo-client-onboarding" in contract
    assert "writing style guide" in blog and "ld-seo-content-briefs" in blog
    assert "stale sidecar" in metadata and "collection-seo-qa" in metadata
    assert "plan capacity" in keyword_research and "ld-seo-maintenance" in keyword_research
    assert "Google Doc, Sheet, or Drive editing" in contract and "after LD SEO validation" in contract


def test_codex_skill_sync_generates_installed_entrypoints(tmp_path: Path) -> None:
    written = sync_codex_skills.sync(target_dir=tmp_path)
    names = {path.parent.name for path in written}
    assert CANONICAL_SKILLS <= names
    for path in written:
        text = _read(path)
        fields = _frontmatter(text)
        assert fields["name"] == path.parent.name
        assert "Canonical skill:" in text
        assert "installed Codex skill entrypoint" in text
        assert "Operating Rule" in text


def test_client_timelines_exist_with_required_columns() -> None:
    template = CLIENTS / "CLIENT_TIMELINE_TEMPLATE.md"
    assert template.exists()

    required_columns = [
        "Date",
        "Task",
        "Request / source",
        "Evidence checked",
        "Outputs",
        "Decisions",
        "Caveats",
        "Next action",
        "Proof summary",
    ]

    excluded_briefs = {
        "_index.md",
        "CLIENT_TIMELINE_TEMPLATE.md",
        "little-shop-of-happiness-writing-style.md",
        "mrgadget.md",  # test-only sidecar; excluded from active client timeline requirement
    }
    briefs = [
        path for path in CLIENTS.glob("*.md")
        if path.name not in excluded_briefs and not path.name.endswith("-timeline.md")
    ]
    assert briefs

    for brief in briefs:
        timeline = CLIENTS / f"{brief.stem}-timeline.md"
        assert timeline.exists(), f"missing timeline for {brief.name}"
        text = _read(timeline)
        for column in required_columns:
            assert column in text, f"{timeline.name} missing {column}"
        assert "Baseline memory seed" in text, timeline.name
