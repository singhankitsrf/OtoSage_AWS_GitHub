"""Publish an allowlisted Docker Space; credentials come from HF_TOKEN or hf auth login."""

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess  # nosec B404 - fixed git commands, no shell or user command text
import tempfile
from huggingface_hub import HfApi


def stage(root: Path, dest: Path):
    allowed_roots = {
        "src",
        "ml",
        "hf_space",
        "training",
        "scripts",
        "evaluation",
        "docs",
        "configs",
    }
    allowed_files = {"pyproject.toml", "LICENSE"}
    # Only tracked source files: never upload datasets, checkpoints, caches,
    # credentials, .git, or incidental workspace content.
    paths = (
        subprocess.check_output(  # nosec B603 - fixed read-only git command
            [shutil.which("git") or "/usr/bin/git", "ls-files", "-z"], cwd=root
        )
        .decode()
        .split("\0")
    )
    for name in filter(None, paths):
        p = Path(name)
        if (p.parts[0] in allowed_roots or name in allowed_files) and p.suffix not in {
            ".joblib",
            ".pt",
            ".pth",
            ".zip",
        }:
            source = root / p
            if source.is_symlink():
                raise ValueError("Symlinks are not allowed in Space deployment")
            target = dest / p
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    for name in ("README.md", "Dockerfile"):
        shutil.copyfile(root / "hf_space" / name, dest / name)
    sha = subprocess.check_output(  # nosec B603 - fixed read-only git command
        [shutil.which("git") or "/usr/bin/git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    (dest / "SOURCE_REVISION.json").write_text(json.dumps({"git_commit": sha}, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-id", required=True)
    ap.add_argument("--stage-only", type=Path)
    a = ap.parse_args()
    if not a.repo_id.startswith("singhankit491/"):
        raise ValueError("Destination must be in the requested singhankit491 account")
    root = Path(__file__).resolve().parents[1]
    if a.stage_only:
        a.stage_only.mkdir(parents=True, exist_ok=True)
        stage(root, a.stage_only)
        print("Staged source:", a.stage_only)
        return
    api = HfApi(token=os.getenv("HF_TOKEN"))
    if api.whoami()["name"] != "singhankit491":
        raise ValueError("Authenticated Hugging Face account does not match requested owner")
    with tempfile.TemporaryDirectory() as folder:
        stage(root, Path(folder))
        api.create_repo(
            a.repo_id, repo_type="space", space_sdk="docker", exist_ok=True, private=False
        )
        commit = api.upload_folder(
            repo_id=a.repo_id,
            repo_type="space",
            folder_path=folder,
            commit_message="Deploy validated GitHub portfolio source",
        )
        print(commit.commit_url)
        print("Runtime state:", api.get_space_runtime(a.repo_id).stage)
        print(
            "An uploaded commit is not proof of a healthy running Space; inspect its build and app."
        )


if __name__ == "__main__":
    main()
