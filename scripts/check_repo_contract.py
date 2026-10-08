#!/usr/bin/env python3
"""Check the public research-concept contract without claiming study results."""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from jsonschema.validators import validator_for


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md",
    "ROADMAP.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "docs/research-plan.md",
    "docs/prior-art.md",
    "docs/experiment-01-authority-loss.md",
    "docs/claim-ledger.md",
    "docs/data-and-figures.md",
    "docs/decision-log.md",
    "docs/research-dependency-audit.md",
    "docs/research-dependency-graph.json",
    "protocols/configuration-manifest.schema.json",
    "protocols/example-configuration-manifest.json",
    "data/README.md",
    "results/README.md",
)
REQUIRED_MANIFEST_KEYS = {
    "manifest_version",
    "study_id",
    "run_id",
    "evidence_state",
    "autopilot",
    "firmware_identifier",
    "airframe_id",
    "configuration_hash",
    "recovery_intention",
    "test_environment",
    "authority_loss_event",
    "initial_condition",
    "recording",
}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HEADING = re.compile(r"(?m)^#{1,6}\s+(.+?)(?:\s+#+)?$")


def local_markdown_links(path: Path) -> list[tuple[Path, str]]:
    """(target path, fragment) for every local link; fragment is "" when absent."""
    links: list[tuple[Path, str]] = []
    for raw_target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
        target = raw_target.strip().split(" ", 1)[0]
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target, _, fragment = target.partition("#")
        target = unquote(target)
        if target:
            links.append(((path.parent / target).resolve(), unquote(fragment)))
    return links


def markdown_anchors(path: Path) -> set[str]:
    """GitHub-style heading anchors of a markdown file (duplicates get -1, -2, ...)."""
    text = re.sub(r"(?ms)^[ ]{0,3}(`{3,}|~{3,}).*?^\1[ \t]*$", "", path.read_text(encoding="utf-8"))
    anchors: set[str] = set(re.findall(r"(?:id|name)=[\"']([^\"']+)[\"']", text))
    seen: dict[str, int] = {}
    for heading in HEADING.findall(text):
        heading = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", heading)
        heading = re.sub(r"<[^>]*>", "", heading).lower()
        name = re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")
        count = seen.get(name, 0)
        seen[name] = count + 1
        anchors.add(name + (f"-{count}" if count else ""))
    return anchors


def manifest_errors(instance: object, schema: dict) -> list[str]:
    """Enforce the declared dialect and JSON's finite-number boundary."""
    validator_class = validator_for(schema)
    validator_class.check_schema(schema)
    errors = [
        "manifest " + ("/".join(map(str, error.absolute_path)) or "<root>") + ": " + error.message
        for error in validator_class(schema).iter_errors(instance)
    ]

    def finite_numbers(value: object, path: str = "<root>") -> None:
        if isinstance(value, float) and not math.isfinite(value):
            errors.append(f"manifest {path}: non-finite numbers are not JSON measurements")
        elif isinstance(value, dict):
            for key, child in value.items():
                finite_numbers(child, f"{path}/{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                finite_numbers(child, f"{path}/{index}")

    finite_numbers(instance)
    return sorted(errors)


def run_checks() -> list[str]:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    # Study A remains unexecuted. Development runs and public-log observations exist;
    # the repository must distinguish those from newly conducted flights.
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "No study result has been generated" not in readme:
        errors.append("README must state that no study result has been generated")
    if "No new flights were conducted" not in readme:
        errors.append("README must distinguish public logs from newly conducted flights")

    result_notice = (ROOT / "results/README.md").read_text(encoding="utf-8")
    if "No study result is available" not in result_notice:
        errors.append("results/README.md must preserve the no-study-result notice")
    if "never held-out confirmation and never a measured" not in result_notice:
        errors.append("results/README.md must say development runs are not results")

    schema = json.loads(
        (ROOT / "protocols/configuration-manifest.schema.json").read_text(encoding="utf-8")
    )
    example = json.loads(
        (ROOT / "protocols/example-configuration-manifest.json").read_text(encoding="utf-8")
    )
    errors.extend(manifest_errors(example, schema))
    if not isinstance(example, dict):
        example = {}
    schema_required = set(schema.get("required", []))
    if schema_required != REQUIRED_MANIFEST_KEYS:
        errors.append("configuration schema required keys differ from the repository contract")
    missing_example = REQUIRED_MANIFEST_KEYS - set(example)
    if missing_example:
        errors.append(f"example manifest missing keys: {sorted(missing_example)}")
    if example.get("evidence_state") != "planned-example":
        errors.append("example manifest must remain labeled planned-example")

    dependency_graph = json.loads(
        (ROOT / "docs/research-dependency-graph.json").read_text(encoding="utf-8")
    )
    if dependency_graph.get("directed") is not True:
        errors.append("research dependency graph must remain directed")
    if dependency_graph.get("generated_tasks_excluded") is not True:
        errors.append("generated task text must remain excluded from the dependency audit")
    token_usage = dependency_graph.get("token_usage", {})
    if token_usage.get("status") != "unavailable":
        errors.append("unmeasured Graphify usage must be labeled unavailable")
    if (
        token_usage.get("input_tokens") is not None
        or token_usage.get("output_tokens") is not None
    ):
        errors.append("unmeasured Graphify token counts must be null, not zero")
    nodes = dependency_graph.get("nodes", [])
    node_ids = [node.get("id") for node in nodes]
    if len(node_ids) != len(set(node_ids)) or any(
        not node_id for node_id in node_ids
    ):
        errors.append("research dependency graph node IDs must be unique and nonempty")
    known_nodes = set(node_ids)
    for node in nodes:
        source = node.get("source")
        if not source or not (ROOT / source).is_file():
            errors.append(f"research dependency node has missing source: {node.get('id')}")
    for edge in dependency_graph.get("edges", []):
        if not edge.get("source") or not edge.get("target"):
            errors.append("research dependency graph contains a missing endpoint")
        elif edge["source"] not in known_nodes or edge["target"] not in known_nodes:
            errors.append(
                "research dependency graph contains a dangling endpoint: "
                f"{edge['source']} -> {edge['target']}"
            )

    for markdown in ROOT.rglob("*.md"):
        if ".git" in markdown.parts:
            continue
        for target, fragment in local_markdown_links(markdown):
            if not target.exists():
                errors.append(f"broken local link in {markdown.relative_to(ROOT)}: {target}")
            elif fragment and target.suffix == ".md" and fragment not in markdown_anchors(target):
                errors.append(f"broken anchor in {markdown.relative_to(ROOT)}: {target.name}#{fragment}")

    return errors


def main() -> int:
    errors = run_checks()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Repository contract: PASS")
    print("Evidence state: research design; no study results")
    return 0


if __name__ == "__main__":
    sys.exit(main())
