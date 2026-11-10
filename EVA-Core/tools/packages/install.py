#!/usr/bin/env python3
"""Install, list and uninstall local EVA Registry pilot packages in an isolated root."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from package_common import safe_extract, verify_checksums


def guarded_root(path: Path) -> Path:
    root = path.resolve()
    if root == Path(root.anchor) or len(root.parts) < 4:
        raise ValueError(f"refusing broad install root: {root}")
    root.mkdir(parents=True, exist_ok=True)
    return root


def install(root: Path, archive: Path, expected_prefix: str) -> list[Path]:
    verify_checksums(archive)
    import zipfile
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        if not names or any(not name.startswith(expected_prefix) for name in names):
            raise ValueError(f"{archive.name}: unexpected package root; expected {expected_prefix}")
    return safe_extract(archive, root)


def inventory(root: Path) -> dict:
    core = root / "EVA-Core/core.json"
    templates = []
    for metadata in sorted((root / "templates").glob("T??/*/template.json")) if (root / "templates").exists() else []:
        data = json.loads(metadata.read_text(encoding="utf-8"))
        templates.append({"id": data["id"], "version": data["version"], "path": str(metadata.parent)})
    return {
        "core": json.loads(core.read_text(encoding="utf-8")) if core.is_file() else None,
        "templates": templates,
    }


def uninstall(root: Path, template_id: str, version: str) -> None:
    if not template_id.startswith("T") or len(template_id) != 3 or not version.replace(".", "").isdigit():
        raise ValueError("invalid template ID/version")
    target = (root / "templates" / template_id / version).resolve()
    templates_root = (root / "templates").resolve()
    if templates_root not in target.parents or not target.is_dir():
        raise ValueError(f"installed template not found: {template_id}@{version}")
    shutil.rmtree(target)
    parent = target.parent
    if parent.is_dir() and not any(parent.iterdir()):
        parent.rmdir()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    sp = ap.add_subparsers(dest="command", required=True)
    p = sp.add_parser("install-core"); p.add_argument("archive", type=Path)
    p = sp.add_parser("install-template"); p.add_argument("archive", type=Path); p.add_argument("--id", required=True); p.add_argument("--version", required=True)
    sp.add_parser("list")
    p = sp.add_parser("uninstall"); p.add_argument("--id", required=True); p.add_argument("--version", required=True)
    args = ap.parse_args()
    root = guarded_root(args.root)
    if args.command == "install-core":
        install(root, args.archive, "EVA-Core/")
    elif args.command == "install-template":
        install(root, args.archive, f"templates/{args.id}/{args.version}/")
    elif args.command == "uninstall":
        uninstall(root, args.id, args.version)
    print(json.dumps(inventory(root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
