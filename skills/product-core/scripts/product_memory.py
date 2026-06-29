#!/usr/bin/env python3
"""Portable Git-backed memory and validation CLI for Product Copilot."""

from __future__ import annotations

import argparse
import math
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import uuid
import zipfile
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(os.environ.get("PRODUCT_COPILOT_ROOT", Path(__file__).resolve().parents[3])).resolve()
CONFIG_PATH = ROOT / "config" / "product-copilot.json"
FACT_FIELDS = ("id", "kind", "statement", "source", "updated_at", "confidence", "status")
TOKEN_RE = re.compile(r"[\wÀ-ỹ.-]+", re.UNICODE)


class CopilotError(Exception):
    pass


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CopilotError(f"Cannot read {path}: {exc}") from exc


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise CopilotError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return records


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")
    if not normalized:
        raise CopilotError("Project must contain letters or digits.")
    return normalized


def project_dir(project: str) -> Path:
    return ROOT / "knowledge" / "projects" / slug(project)


def init_project(project: str) -> Path:
    target = project_dir(project)
    if target.exists():
        return target
    shutil.copytree(ROOT / "knowledge" / "projects" / "_template", target)
    append_jsonl(
        ROOT / "knowledge" / "audit" / "events.jsonl",
        {"event": "project_initialized", "project": slug(project), "at": now()},
    )
    return target


def scope_dir(project: str | None, scope: str) -> Path:
    if scope == "global":
        return ROOT / "knowledge" / "global"
    if not project:
        raise CopilotError("--project is required for project scope.")
    return init_project(project)


def normalize(text: str) -> str:
    return " ".join(TOKEN_RE.findall(text.lower()))


def source_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt", ".json", ".yaml", ".yml", ".csv"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".docx":
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
        root = ElementTree.fromstring(xml)
        return "\n".join(node.text or "" for node in root.iter() if node.tag.endswith("}t"))
    if suffix == ".pdf":
        try:
            import pypdf  # type: ignore
        except ImportError as exc:
            raise CopilotError("PDF ingestion requires pypdf (`python3 -m pip install pypdf`).") from exc
        reader = pypdf.PdfReader(str(path))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    raise CopilotError(f"Unsupported document type: {suffix or '[none]'}")


def chunks(text: str, size: int = 1800, overlap: int = 180) -> list[str]:
    cleaned = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not cleaned:
        return []
    result = []
    start = 0
    while start < len(cleaned):
        end = min(start + size, len(cleaned))
        if end < len(cleaned):
            boundary = max(cleaned.rfind("\n", start, end), cleaned.rfind(". ", start, end))
            if boundary > start + size // 2:
                end = boundary + 1
        result.append(cleaned[start:end].strip())
        if end >= len(cleaned):
            break
        start = max(start + 1, end - overlap)
    return [item for item in result if item]


def ingest(project: str, text: str, source: str, title: str | None = None) -> dict:
    target = init_project(project) / "chunks.jsonl"
    existing_hashes = {item.get("hash") for item in read_jsonl(target)}
    added = 0
    skipped = 0
    for position, content in enumerate(chunks(text), 1):
        digest = hashlib.sha256(normalize(content).encode()).hexdigest()
        if digest in existing_hashes:
            skipped += 1
            continue
        append_jsonl(
            target,
            {
                "id": f"chunk-{digest[:12]}",
                "source": source,
                "title": title or Path(source).name,
                "position": position,
                "text": content,
                "hash": digest,
                "ingested_at": now(),
                "status": "active",
            },
        )
        existing_hashes.add(digest)
        added += 1
    event = {
        "event": "document_ingested",
        "project": slug(project),
        "source": source,
        "chunks_added": added,
        "duplicates_skipped": skipped,
        "at": now(),
    }
    append_jsonl(ROOT / "knowledge" / "audit" / "events.jsonl", event)
    return event


def sensitive(statement: str, config: dict) -> str | None:
    lowered = statement.lower()
    return next((marker for marker in config["sensitive_markers"] if marker.lower() in lowered), None)


def learn(args: argparse.Namespace, config: dict) -> dict:
    marker = sensitive(args.statement, config)
    if marker:
        raise CopilotError(f"Refusing to store content matching sensitive marker: {marker}")
    if args.kind in config["governed_kinds"] or args.kind not in config["safe_auto_learning_kinds"]:
        raise CopilotError(f"Kind '{args.kind}' requires `propose`, not automatic learning.")
    target = scope_dir(args.project, args.scope) / "facts.jsonl"
    normalized = normalize(args.statement)
    for item in read_jsonl(target):
        if item.get("status") == "active" and normalize(item.get("statement", "")) == normalized:
            return {"status": "duplicate", "id": item["id"]}
    record = {
        "id": f"fact-{uuid.uuid4().hex[:12]}",
        "kind": args.kind,
        "statement": args.statement.strip(),
        "source": args.source,
        "updated_at": now(),
        "confidence": args.confidence,
        "status": "active",
    }
    append_jsonl(target, record)
    append_jsonl(
        ROOT / "knowledge" / "audit" / "events.jsonl",
        {"event": "fact_learned", "project": args.project, "scope": args.scope, "fact_id": record["id"], "at": now()},
    )
    return record


def propose(args: argparse.Namespace, config: dict) -> dict:
    marker = sensitive(args.statement, config)
    if marker:
        raise CopilotError(f"Refusing to propose content matching sensitive marker: {marker}")
    proposal_id = f"proposal-{dt.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
    record = {
        "id": proposal_id,
        "project": slug(args.project) if args.project else None,
        "scope": args.scope,
        "kind": args.kind,
        "statement": args.statement.strip(),
        "source": args.source,
        "confidence": args.confidence,
        "status": "pending",
        "created_at": now(),
    }
    path = ROOT / "knowledge" / "proposals" / f"{proposal_id}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    append_jsonl(
        ROOT / "knowledge" / "audit" / "events.jsonl",
        {"event": "learning_proposed", "proposal_id": proposal_id, "project": record["project"], "at": now()},
    )
    return {"proposal": str(path.relative_to(ROOT)), **record}


def score(query: str, text: str) -> float:
    query_terms = set(TOKEN_RE.findall(query.lower()))
    text_terms = set(TOKEN_RE.findall(text.lower()))
    if not query_terms:
        return 0
    overlap = len(query_terms & text_terms) / len(query_terms)
    phrase = 0.5 if normalize(query) and normalize(query) in normalize(text) else 0
    return overlap + phrase


def recall(project: str, query: str, budget: int, max_results: int) -> str:
    candidates: list[tuple[float, str]] = []
    sources = [
        ("global", ROOT / "knowledge" / "global"),
        ("project", project_dir(project)),
    ]
    if not project_dir(project).exists():
        raise CopilotError(f"Unknown project '{slug(project)}'. Run init-project first.")
    for scope_name, base in sources:
        index = base / "index.md"
        if index.exists():
            text = index.read_text(encoding="utf-8").strip()
            if text:
                candidates.append((score(query, text) + 0.05, f"[summary:{scope_name}]\n{text}"))
        for fact in read_jsonl(base / "facts.jsonl"):
            if fact.get("status") != "active":
                continue
            body = fact.get("statement", "")
            bonus = 0.08 if scope_name == "project" else 0
            rendered = f"[fact:{fact.get('id')} source={fact.get('source')} confidence={fact.get('confidence')}]\n{body}"
            candidates.append((score(query, body) + bonus, rendered))
    for item in read_jsonl(project_dir(project) / "chunks.jsonl"):
        if item.get("status") != "active":
            continue
        body = item.get("text", "")
        rendered = f"[chunk:{item.get('id')} source={item.get('source')}]\n{body}"
        candidates.append((score(query, body), rendered))
    ranked = sorted((item for item in candidates if item[0] > 0), key=lambda item: item[0], reverse=True)
    output = [f"# Recalled context\nProject: {slug(project)}\nQuery: {query}\n"]
    used = len(output[0])
    for _, rendered in ranked[:max_results]:
        addition = "\n" + rendered + "\n"
        if used + len(addition) > budget:
            continue
        output.append(addition)
        used += len(addition)
    if len(output) == 1:
        output.append("\nNo relevant active context found.\n")
    output.append(f"\nContext characters used: {used}/{budget}\n")
    output.append(f"Estimated context tokens: {math.ceil(used / 4)}\n")
    return "".join(output)


def template_manifest(kind: str) -> tuple[Path, dict]:
    path = ROOT / "templates" / kind / "template.json"
    if kind not in {"ticket", "prd"}:
        raise CopilotError("Template type must be ticket or prd.")
    return path, load_json(path)


def install_template(kind: str, template: Path, headings: list[str], version: str) -> dict:
    if not template.exists():
        raise CopilotError(f"Template not found: {template}")
    target_dir = ROOT / "templates" / kind
    target = target_dir / template.name
    if template.resolve() != target.resolve():
        shutil.copy2(template, target)
    manifest = {
        "type": kind,
        "installed": True,
        "version": version,
        "template_file": target.name,
        "required_headings": headings,
    }
    (target_dir / "template.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    append_jsonl(
        ROOT / "knowledge" / "audit" / "events.jsonl",
        {"event": "template_installed", "type": kind, "version": version, "at": now()},
    )
    return manifest


def deprecate_by_source(project: str, source_prefix: str) -> dict:
    target = project_dir(project) / "chunks.jsonl"
    records = read_jsonl(target)
    timestamp = now()
    updated = 0
    rewritten = []
    for record in records:
        if record.get("source", "").startswith(source_prefix) and record.get("status") == "active":
            record = {**record, "status": "deprecated", "deprecated_at": timestamp}
            updated += 1
        rewritten.append(record)
    target.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rewritten) + "\n",
        encoding="utf-8",
    )
    append_jsonl(
        ROOT / "knowledge" / "audit" / "events.jsonl",
        {"event": "chunks_deprecated", "project": slug(project), "source_prefix": source_prefix,
         "count": updated, "at": timestamp},
    )
    return {"deprecated": updated, "source_prefix": source_prefix}


def validate_artifact(kind: str, path: Path) -> dict:
    if not path.exists():
        raise CopilotError(f"Artifact not found: {path}")
    text = path.read_text(encoding="utf-8")
    errors = []
    warnings = []
    for field in ("project", "sources", "assumptions", "generated_at", "trace_id"):
        if not re.search(rf"(?im)^\s*(?:[-*]\s*)?{re.escape(field)}\s*:", text):
            errors.append(f"Missing metadata field: {field}")
    if kind in {"ticket", "prd"}:
        _, manifest = template_manifest(kind)
        if not manifest.get("installed"):
            errors.append(f"{kind} template is not installed")
        for heading in manifest.get("required_headings", []):
            # Match both Markdown (## Heading) and Jira wiki (h3. Heading) formats.
            if not re.search(rf"(?im)(?:^#+\s+|^h\d\.\s+){re.escape(heading)}\s*$", text):
                errors.append(f"Missing required heading: {heading}")
        if kind == "ticket" and manifest.get("exactly_one_requirement_variant"):
            variants = manifest.get("requirement_variants", [])
            selected = [
                variant
                for variant in variants
                if re.search(rf"(?im)(?:^##+\s+|\*){re.escape(variant)}\*?\s*$", text)
            ]
            if len(selected) != 1:
                errors.append(
                    "Ticket must contain exactly one Requirement variant; "
                    f"found {len(selected)} ({', '.join(selected) or 'none'})"
                )
    elif kind == "sequence":
        for required in ("```mermaid", "sequenceDiagram", "autonumber"):
            if required not in text:
                errors.append(f"Missing Mermaid element: {required}")
        declared = set(re.findall(r"(?m)^\s*(?:participant|actor)\s+([A-Za-z0-9_]+)", text))
        used = set(re.findall(r"(?m)^\s*([A-Za-z0-9_]+)\s*-{1,2}>+([A-Za-z0-9_]+)", text))
        for left, right in used:
            for actor in (left, right):
                if actor not in declared:
                    errors.append(f"Undeclared participant: {actor}")
    else:
        raise CopilotError("Artifact type must be ticket, prd, or sequence.")
    if not re.search(r"\bREQ-\d{3,}\b", text) and kind in {"prd", "sequence"}:
        warnings.append("No stable REQ identifier found")
    return {"valid": not errors, "errors": sorted(set(errors)), "warnings": sorted(set(warnings))}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init-project")
    init.add_argument("--project", required=True)

    ingest_file = sub.add_parser("ingest")
    ingest_file.add_argument("--project", required=True)
    ingest_file.add_argument("--source", required=True, type=Path)
    ingest_file.add_argument("--title")

    ingest_stdin = sub.add_parser("ingest-text")
    ingest_stdin.add_argument("--project", required=True)
    ingest_stdin.add_argument("--source", required=True, help="URL or stable source identifier")
    ingest_stdin.add_argument("--title")

    recall_cmd = sub.add_parser("recall")
    recall_cmd.add_argument("--project", required=True)
    recall_cmd.add_argument("--query", required=True)
    recall_cmd.add_argument("--budget", type=int)
    recall_cmd.add_argument("--max-results", type=int)

    for name in ("learn", "propose"):
        command = sub.add_parser(name)
        command.add_argument("--project")
        command.add_argument("--scope", choices=("global", "project"), default="project")
        command.add_argument("--kind", required=True)
        command.add_argument("--statement", required=True)
        command.add_argument("--source", required=True)
        command.add_argument("--confidence", type=float, default=1.0)

    dep_src = sub.add_parser("deprecate-by-source")
    dep_src.add_argument("--project", required=True)
    dep_src.add_argument("--source-prefix", required=True,
                         help="Prefix to match, e.g. 'confluence://ZPPROM/pages/213903658'")

    status = sub.add_parser("template-status")
    status.add_argument("--type", required=True, choices=("ticket", "prd"))

    install = sub.add_parser("install-template")
    install.add_argument("--type", required=True, choices=("ticket", "prd"))
    install.add_argument("--file", required=True, type=Path)
    install.add_argument("--version", required=True)
    install.add_argument("--heading", action="append", default=[])

    validate = sub.add_parser("validate-artifact")
    validate.add_argument("--type", required=True, choices=("ticket", "prd", "sequence"))
    validate.add_argument("--file", required=True, type=Path)
    return result


def main() -> int:
    args = parser().parse_args()
    config = load_json(CONFIG_PATH)
    try:
        if args.command == "init-project":
            result = {"project": slug(args.project), "path": str(init_project(args.project).relative_to(ROOT))}
        elif args.command == "ingest":
            result = ingest(args.project, source_text(args.source), str(args.source), args.title)
        elif args.command == "ingest-text":
            result = ingest(args.project, sys.stdin.read(), args.source, args.title)
        elif args.command == "recall":
            budget = args.budget or config["retrieval"]["default_budget_chars"]
            maximum = args.max_results or config["retrieval"]["max_results"]
            if budget < 200:
                raise CopilotError("Budget must be at least 200 characters.")
            print(recall(args.project, args.query, budget, maximum))
            return 0
        elif args.command == "deprecate-by-source":
            result = deprecate_by_source(args.project, args.source_prefix)
        elif args.command == "learn":
            result = learn(args, config)
        elif args.command == "propose":
            result = propose(args, config)
        elif args.command == "template-status":
            _, result = template_manifest(args.type)
        elif args.command == "install-template":
            result = install_template(args.type, args.file, args.heading, args.version)
        elif args.command == "validate-artifact":
            result = validate_artifact(args.type, args.file)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["valid"] else 2
        else:
            raise CopilotError(f"Unsupported command: {args.command}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except CopilotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
