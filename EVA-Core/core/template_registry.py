#!/usr/bin/env python3
"""Discover and validate independently installed EVA template packages."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


CORE_VERSION = "1.0.1"
ENGINE_API = "legacy-1"
PLAN_SCHEMA = "legacy-v1"
TEMPLATE_ID = re.compile(r"^T\d{2}$")


class RegistryError(ValueError):
    pass


def _version(value: str) -> tuple[int, int, int]:
    try:
        bits = tuple(int(x) for x in value.split("."))
    except (AttributeError, ValueError) as exc:
        raise RegistryError(f"invalid semantic version: {value!r}") from exc
    if len(bits) != 3:
        raise RegistryError(f"invalid semantic version: {value!r}")
    return bits


def _compatible(version: str, requirement: str) -> bool:
    actual = _version(version)
    for term in requirement.split():
        match = re.fullmatch(r"(>=|<=|>|<|==)(\d+\.\d+\.\d+)", term)
        if not match:
            raise RegistryError(f"unsupported compatibility expression: {requirement!r}")
        op, wanted = match.group(1), _version(match.group(2))
        if {">=": actual >= wanted, "<=": actual <= wanted, ">": actual > wanted,
            "<": actual < wanted, "==": actual == wanted}[op] is False:
            return False
    return True


@dataclass(frozen=True)
class InstalledTemplate:
    id: str
    version: str
    root: Path
    metadata: dict
    skin: dict

    @property
    def auto_skin(self) -> Path:
        return self.root / "runtime/auto-skin.js"

    @property
    def runtime_lib(self) -> Path | None:
        """Optional template-owned runtime library, loaded before auto-skin.js."""
        path = self.root / "runtime/lib.js"
        return path if path.is_file() else None

    @property
    def needs_cutout(self) -> bool:
        return "presenter-cutout" in self.metadata.get("dependencies", {}).get("media", [])


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"cannot read {path}: {exc}") from exc


def discover(install_root: str | Path) -> dict[str, InstalledTemplate]:
    """Return one validated installed version per template ID.

    Multiple installed versions are rejected deliberately: a plan must never silently
    switch implementations between preview and final render.
    """
    root = Path(install_root).resolve()
    core = root / "EVA-Core/core.json"
    if not core.is_file():
        raise RegistryError(f"EVA Core is not installed under {root}")
    core_data = _load(core)
    if core_data.get("version") != CORE_VERSION or core_data.get("engine_api") != ENGINE_API:
        raise RegistryError(
            f"unsupported Core identity: {core_data.get('version')} / {core_data.get('engine_api')}"
        )

    found: dict[str, InstalledTemplate] = {}
    template_root = root / "templates"
    for metadata_path in sorted(template_root.glob("T??/*/template.json")) if template_root.exists() else []:
        data = _load(metadata_path)
        template_id, version = data.get("id"), data.get("version")
        package_root = metadata_path.parent
        if not TEMPLATE_ID.fullmatch(str(template_id)) or package_root.parent.name != template_id:
            raise RegistryError(f"template identity/path mismatch: {metadata_path}")
        if package_root.name != version:
            raise RegistryError(f"template version/path mismatch: {metadata_path}")
        if template_id in found:
            raise RegistryError(f"multiple installed versions of {template_id}; uninstall one before rendering")
        # A quarantined/source-only package may be installed for manual inspection
        # without poisoning discovery of otherwise valid templates. It remains
        # invisible to Planner/Renderer selection and resolve() reports it clearly
        # when explicitly requested.
        if data.get("render_status") != "renderable" or data.get("identity_status") != "confirmed":
            continue
        compatibility = data.get("compatibility", {})
        if compatibility.get("engine_api") != ENGINE_API:
            raise RegistryError(f"{template_id}@{version} requires engine API {compatibility.get('engine_api')}")
        if PLAN_SCHEMA not in compatibility.get("plan_schemas", []):
            raise RegistryError(f"{template_id}@{version} does not support plan schema {PLAN_SCHEMA}")
        if not _compatible(CORE_VERSION, compatibility.get("core", "")):
            raise RegistryError(f"{template_id}@{version} is incompatible with Core {CORE_VERSION}")
        if not data.get("capabilities", {}).get("studio_auto"):
            raise RegistryError(f"{template_id}@{version} has no automatic-edit runtime")
        auto_skin = package_root / "runtime/auto-skin.js"
        skin_path = package_root / "config/skin.json"
        if not auto_skin.is_file() or not skin_path.is_file():
            raise RegistryError(f"{template_id}@{version} is missing runtime/auto-skin.js or config/skin.json")
        skin = _load(skin_path)
        if skin.get("id") != template_id or not isinstance(skin.get("window"), dict):
            raise RegistryError(f"{template_id}@{version} has an invalid skin config")
        found[template_id] = InstalledTemplate(template_id, version, package_root, data, skin)
    return found


def resolve(install_root: str | Path, template_ids: list[str], aspect: str) -> list[InstalledTemplate]:
    if aspect not in ("16:9", "9:16"):
        raise RegistryError(f"unsupported aspect: {aspect}")
    if not template_ids:
        raise RegistryError("at least one template ID is required")
    if len(set(template_ids)) != len(template_ids):
        raise RegistryError("template IDs must be unique")
    installed = discover(install_root)
    selected = []
    for template_id in template_ids:
        if template_id not in installed:
            candidates = sorted((Path(install_root).resolve() / "templates" / template_id).glob("*/template.json"))
            if candidates:
                data = _load(candidates[0])
                raise RegistryError(
                    f"{template_id}@{data.get('version')} is installed but not a confirmed renderable template "
                    f"({data.get('render_status')}/{data.get('identity_status')})"
                )
            raise RegistryError(f"{template_id} is not installed")
        item = installed[template_id]
        if aspect not in item.metadata.get("aspects", []):
            raise RegistryError(f"{template_id}@{item.version} does not support {aspect}")
        selected.append(item)
    return selected


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("install_root", type=Path)
    parser.add_argument("--templates", required=True)
    parser.add_argument("--aspect", default="9:16")
    args = parser.parse_args()
    items = resolve(args.install_root, [x.strip() for x in args.templates.split(",") if x.strip()], args.aspect)
    print(json.dumps([{"id": x.id, "version": x.version, "path": str(x.root)} for x in items], indent=2))
