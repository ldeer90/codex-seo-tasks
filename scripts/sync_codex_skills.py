"""Install repo-local LD SEO skills into ~/.codex/skills for native Codex discovery.

The repo remains canonical. Generated files are lightweight installed Codex
skill entrypoints that point back to this workspace so future Codex sessions can
trigger the LD SEO skills without routing through legacy Claude command files.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "agent" / "skills"
DEFAULT_TARGET_DIR = Path.home() / ".codex" / "skills"


def _read_frontmatter(skill_md: Path) -> tuple[dict[str, str], str]:
    text = skill_md.read_text()
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"{skill_md} has no YAML frontmatter")

    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip()
    if not frontmatter.get("name") or not frontmatter.get("description"):
        raise ValueError(f"{skill_md} frontmatter must contain name and description")
    return frontmatter, match.group(2).strip()


def _workflow_links(body: str) -> list[str]:
    links = sorted(set(re.findall(r"docs/agent/workflows/[A-Za-z0-9_.-]+\.md", body)))
    return links


def _wrapper(skill_md: Path) -> str:
    frontmatter, body = _read_frontmatter(skill_md)
    rel_skill = skill_md.relative_to(ROOT)
    links = _workflow_links(body)
    workflow_block = "\n".join(f"- `{ROOT / link}`" for link in links) or "- See canonical repo skill."

    return (
        "---\n"
        f"name: {frontmatter['name']}\n"
        f"description: {frontmatter['description']}\n"
        "---\n\n"
        f"# {frontmatter['name']}\n\n"
        "This installed Codex skill entrypoint is generated from the SEO Automation repo. "
        "The repo-local skill is canonical; read it before acting.\n\n"
        f"- Canonical skill: `{ROOT / rel_skill}`\n"
        f"- Skill index: `{ROOT / 'docs/agent/skills/_index.md'}`\n"
        f"- Workflow index: `{ROOT / 'docs/agent/workflows/_index.md'}`\n\n"
        "## Relevant Workflows\n\n"
        f"{workflow_block}\n\n"
        "## Operating Rule\n\n"
        "Follow the canonical repo skill and workflow. Validate sidecars, use cached exports "
        "before paid API calls, apply Codex judgement where expert interpretation is needed, "
        "read back client-facing outputs, and end deliverables with the required proof block.\n"
    )


def sync(*, target_dir: Path, dry_run: bool = False) -> list[Path]:
    written: list[Path] = []
    skills = sorted(p for p in SOURCE_DIR.glob("ld-seo-*/SKILL.md") if p.is_file())
    if not skills:
        raise FileNotFoundError(f"No ld-seo-* skills found in {SOURCE_DIR}")

    for skill_md in skills:
        name = skill_md.parent.name
        target = target_dir / name / "SKILL.md"
        content = _wrapper(skill_md)
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        written.append(target)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-dir", type=Path, default=DEFAULT_TARGET_DIR)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for path in sync(target_dir=args.target_dir, dry_run=args.dry_run):
        action = "would write" if args.dry_run else "wrote"
        print(f"{action}: {path}")


if __name__ == "__main__":
    main()
