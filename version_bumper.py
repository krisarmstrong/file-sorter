#!/usr/bin/env python3
"""
Project Title: VersionBumper

Manages semantic versioning for Python projects, updating __version__ and CHANGELOG.md.

Author: Kris Armstrong
"""
import argparse
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Optional

__version__ = "1.0.1"

def setup_logging(verbose: bool) -> None:
    """Configure logging output.

    Args:
        verbose: Enable DEBUG level logging if True.
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

def find_files(root: str, exclude_dirs: list[str]) -> list[str]:
    """Yield Python files under root, skipping exclude_dirs.

    Args:
        root: Project root directory.
        exclude_dirs: Directories to exclude.

    Returns:
        List of Python file paths.
    """
    python_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for f in filenames:
            if f.endswith(".py"):
                python_files.append(os.path.join(dirpath, f))
    return python_files

def bump_version_in_file(path: str, pattern: str, bump_type: str, dry_run: bool) -> Optional[str]:
    """Bump version in file and return new version if changed.

    Args:
        path: File path.
        pattern: Regex to find version string.
        bump_type: Type of bump (major, minor, patch).
        dry_run: Show changes without writing.

    Returns:
        New version string or None if unchanged.
    """
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    match = re.search(pattern, text)
    if not match:
        return None
    old_ver = match.group(1)
    major, minor, patch = map(int, old_ver.split("."))
    if bump_type == "major":
        major += 1
        minor = patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    new_ver = f"{major}.{minor}.{patch}"
    new_text = re.sub(pattern, f'__version__ = "{new_ver}"', text)
    if new_text != text:
        logging.info("Bumping %s: %s -> %s", path, old_ver, new_ver)
        if not dry_run:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_text)
        return new_ver
    return None

def update_changelog(project: str, new_version: str, bump_type: str, dry_run: bool) -> None:
    """Update CHANGELOG.md with new version entry.

    Args:
        project: Project root directory.
        new_version: New version string.
        bump_type: Type of bump.
        dry_run: Show changes without writing.
    """
    changelog_path = os.path.join(project, "CHANGELOG.md")
    if not os.path.exists(changelog_path):
        logging.warning("CHANGELOG.md not found")
        return
    with open(changelog_path, "r", encoding="utf-8") as f:
        content = f.read()
    today = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n## [{new_version}] - {today}\n\n### {bump_type.capitalize()}\n- Updated version with type annotations.\n"
    new_content = content + entry
    logging.info("Updating CHANGELOG.md with %s", new_version)
    if not dry_run:
        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write(new_content)

def git_commit_and_tag(project: str, version: str, message: str, dry_run: bool) -> None:
    """Git add, commit, and tag the new version.

    Args:
        project: Project root directory.
        version: New version string.
        message: Commit message.
        dry_run: Show changes without executing.
    """
    cmds = [
        ["git", "add", "."],
        ["git", "commit", "-m", message.format(version=version)],
        ["git", "tag", "-a", f"v{version}", "-m", message.format(version=version)],
    ]
    for cmd in cmds:
        logging.debug("Running %s", cmd)
        if not dry_run:
            subprocess.run(cmd, cwd=project, check=True)

def main() -> None:
    """Main entry point for VersionBumper."""
    parser = argparse.ArgumentParser(description="Bump project version.")
    parser.add_argument(
        "-p", "--project",
        default=os.getcwd(),
        help="Path to project root",
    )
    parser.add_argument(
        "-t", "--type",
        choices=["major", "minor", "patch"],
        default="patch",
        help="Version segment to bump",
    )
    parser.add_argument(
        "-f", "--find-pattern",
        default=r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']',
        help="Regex to locate version string",
    )
    parser.add_argument(
        "-c", "--commit",
        action="store_true",
        help="Commit bump to Git",
    )
    parser.add_argument(
        "-g", "--git-tag",
        action="store_true",
        help="Create Git tag",
    )
    parser.add_argument(
        "-m", "--message",
        default="chore: bump version to {version}",
        help="Commit/tag message format",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without writing",
    )
    parser.add_argument(
        "--exclude",
        default=".git,env,venv,.venv,.env,.idea,.vscode",
        help="Comma-separated dirs to skip",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()
    setup_logging(args.verbose)

    exclude_dirs = args.exclude.split(",")
    new_version = None
    for file in find_files(args.project, exclude_dirs):
        result = bump_version_in_file(file, args.find_pattern, args.type, args.dry_run)
        if result:
            new_version = result

    if new_version:
        logging.info("New version: %s", new_version)
        update_changelog(args.project, new_version, args.type, args.dry_run)
        if args.commit or args.git_tag:
            git_commit_and_tag(args.project, new_version, args.message, args.dry_run)
    else:
        logging.info("No version string found or no change needed.")

if __name__ == "__main__":
    main()