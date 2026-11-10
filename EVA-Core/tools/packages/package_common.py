#!/usr/bin/env python3
"""Deterministic ZIP and safe extraction helpers for the local EVA package pilot."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def canonical_json(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checksum_manifest(files: dict[str, bytes]) -> bytes:
    return ("".join(f"{sha256(files[name])}  {name}\n" for name in sorted(files))).encode("utf-8")


def write_zip(path: Path, files: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, files[name])


def safe_member(name: str) -> PurePosixPath:
    p = PurePosixPath(name)
    if p.is_absolute() or not p.parts or any(part in ("", ".", "..") for part in p.parts):
        raise ValueError(f"unsafe archive path: {name}")
    return p


def safe_extract(archive: Path, destination: Path) -> list[Path]:
    destination = destination.resolve()
    extracted = []
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            rel = safe_member(info.filename)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"symlink is not allowed: {info.filename}")
            target = destination.joinpath(*rel.parts).resolve()
            if destination != target and destination not in target.parents:
                raise ValueError(f"archive escapes destination: {info.filename}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(info))
            extracted.append(target)
    return extracted


def verify_checksums(archive: Path) -> dict:
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        check_names = [name for name in names if name.endswith("checksums.sha256")]
        if len(check_names) != 1:
            raise ValueError(f"{archive.name}: expected one checksums.sha256")
        manifest = zf.read(check_names[0]).decode("utf-8").splitlines()
        checked = []
        for line in manifest:
            digest, name = line.split("  ", 1)
            if name not in names:
                raise ValueError(f"{archive.name}: checksum target missing: {name}")
            actual = sha256(zf.read(name))
            if digest != actual:
                raise ValueError(f"{archive.name}: checksum mismatch: {name}")
            checked.append(name)
        expected = sorted(name for name in names if name != check_names[0])
        if sorted(checked) != expected:
            raise ValueError(f"{archive.name}: checksum manifest does not cover every payload file")
        return {"archive": archive.name, "files": len(checked), "sha256": sha256(archive.read_bytes())}
