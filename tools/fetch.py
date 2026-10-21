"""Fetch the eSquareSoft tools at the versions of tools.lock.yaml into .tools/ (configuration management).

  python tools/fetch.py                     required tools at the locked versions
  python tools/fetch.py --all               optional tools too (e2unit, escope, e2hil)
  python tools/fetch.py --only e2sim,e2unit
  python tools/fetch.py --next              default branch instead of the locked ref (CI voice "next")
  python tools/fetch.py --set e2sim=v1.2.0  one tool at another ref (check of a tool release)
  python tools/fetch.py --write-lock        write the refs resolved by the last fetch into tools.lock.yaml

Each fetch writes .tools/resolved.yaml (tool -> ref, commit): attached to the CI results, it says exactly
which versions were tested. A working copy can replace a tool: make E2SIM_ROOT=../e2Sim.
"""

import argparse
import fnmatch
import json
import re
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "tools.lock.yaml"
TOOLS = ROOT / ".tools"
RESOLVED = TOOLS / "resolved.yaml"


def git(*args, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def fetch_git(spec: dict, ref: str) -> str:
    dest = TOOLS / spec["dir"]
    if not (dest / ".git").exists():
        dest.mkdir(parents=True, exist_ok=True)
        git("init", "-q", cwd=dest)
        git("remote", "add", "origin", f"https://github.com/{spec['repo']}.git", cwd=dest)
    git("fetch", "-q", "--depth", "1", "origin", ref, cwd=dest)
    git("checkout", "-q", "--detach", "FETCH_HEAD", cwd=dest)
    return git("rev-parse", "HEAD", cwd=dest)


def github(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def fetch_release(spec: dict, ref: str) -> str:
    rel = github(f"https://api.github.com/repos/{spec['repo']}/releases/tags/{ref}")
    assets = [a for a in rel["assets"] if fnmatch.fnmatch(a["name"], spec["asset"])]
    if not assets:
        raise SystemExit(f"{spec['repo']} {ref}: no asset {spec['asset']}")
    dest = TOOLS / spec["dir"]
    dest.mkdir(parents=True, exist_ok=True)
    file = dest / assets[0]["name"]
    urllib.request.urlretrieve(assets[0]["browser_download_url"], file)
    if file.suffix == ".zip":
        with zipfile.ZipFile(file) as z:
            z.extractall(dest)
    return ref


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--next", action="store_true")
    ap.add_argument("--set", action="append", default=[], metavar="TOOL=REF")
    ap.add_argument("--write-lock", action="store_true")
    args = ap.parse_args()

    lock = yaml.safe_load(LOCK.read_text(encoding="utf-8"))
    tools = lock["tools"]
    if args.write_lock:
        return write_lock(tools)

    overrides = dict(s.split("=", 1) for s in args.set)
    only = set(filter(None, args.only.split(","))) | set(overrides)
    unknown = only - set(tools)
    if unknown:
        raise SystemExit(f"unknown tool(s): {', '.join(sorted(unknown))}")

    resolved = {}
    for name, spec in tools.items():
        selected = name in only if only else (args.all or not spec.get("optional"))
        if not selected or spec["fetch"] == "record":
            resolved[name] = {"ref": spec["ref"], "fetched": False}
            continue
        ref = overrides.get(name) or (spec.get("branch") if args.next and spec["fetch"] == "git" else spec["ref"])
        commit = fetch_git(spec, ref) if spec["fetch"] == "git" else fetch_release(spec, ref)
        resolved[name] = {"ref": ref, "commit": commit, "fetched": True}
        print(f"{name:8} {ref} -> {commit}")

    TOOLS.mkdir(exist_ok=True)
    RESOLVED.write_text(yaml.safe_dump({"suite": lock["suite"], "tools": resolved}, sort_keys=False), encoding="utf-8")
    return 0


def write_lock(tools: dict) -> int:
    """Lock the commits of the last fetch (git tools fetched on a branch): one line per tool, comments kept."""
    resolved = yaml.safe_load(RESOLVED.read_text(encoding="utf-8"))["tools"]
    text = LOCK.read_text(encoding="utf-8")
    for name, r in resolved.items():
        if not r.get("fetched"):
            continue
        new = r["commit"] if tools[name]["fetch"] == "git" and r["ref"] == tools[name].get("branch") else r["ref"]
        text = re.sub(rf"(^\s*{name}:.*?\bref: )[^,}}\s]+", rf"\g<1>{new}", text, flags=re.M)
    LOCK.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
