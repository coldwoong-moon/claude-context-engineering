#!/usr/bin/env python3
"""
Claude Context Engineering - Cross-Platform Setup Script (Python)

Usage:
    python scripts/setup.py install    # Full installation
    python scripts/setup.py hooks      # Install hooks only
    python scripts/setup.py config     # Configure settings.json
    python scripts/setup.py project    # Initialize current project
    python scripts/setup.py doctor     # Verify installation
    python scripts/setup.py uninstall  # Remove installation
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

HOME_DIR = Path.home()
CLAUDE_DIR = HOME_DIR / ".claude"
HOOKS_DIR = CLAUDE_DIR / "hooks"
COMMANDS_DIR = CLAUDE_DIR / "commands"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent


# ═══════════════════════════════════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════════════════════════════════

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

    @staticmethod
    def disable():
        """Disable colors for Windows CMD without ANSI support"""
        if IS_WINDOWS:
            try:
                os.system("")  # Enable ANSI on Windows 10+
            except Exception:
                Colors.RESET = ""
                Colors.BOLD = ""
                Colors.RED = ""
                Colors.GREEN = ""
                Colors.YELLOW = ""
                Colors.BLUE = ""
                Colors.MAGENTA = ""
                Colors.CYAN = ""


Colors.disable()


def log(message: str, color: str = ""):
    print(f"{color}{message}{Colors.RESET}")


def log_success(message: str):
    log(f"✓ {message}", Colors.GREEN)


def log_error(message: str):
    log(f"✗ {message}", Colors.RED)


def log_warning(message: str):
    log(f"⚠ {message}", Colors.YELLOW)


def log_info(message: str):
    log(f"ℹ {message}", Colors.BLUE)


def log_step(step: int, total: int, message: str):
    log(f"[{step}/{total}] {message}", Colors.CYAN)


# ═══════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def ensure_dir(dir_path: Path) -> bool:
    """Create directory if it doesn't exist"""
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
        return True
    return False


def copy_dir(src: Path, dest: Path):
    """Copy directory recursively"""
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def read_json(file_path: Path) -> dict | None:
    """Read JSON file"""
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_json(file_path: Path, data: dict):
    """Write JSON file"""
    file_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )


def get_python_command() -> str | None:
    """Find available Python command"""
    commands = ["python", "python3"] if IS_WINDOWS else ["python3", "python"]

    for cmd in commands:
        try:
            subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                check=True
            )
            return cmd
        except Exception:
            continue
    return None


def hook_path(name: str) -> str:
    """Generate hook path for settings.json"""
    if IS_WINDOWS:
        return f'"%USERPROFILE%\\.claude\\hooks\\{name}.py"'
    return f"~/.claude/hooks/{name}.py"


# ═══════════════════════════════════════════════════════════════════════════
# HOOKS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

def generate_hooks_config() -> dict:
    """Generate hooks configuration for settings.json"""
    python_cmd = "python"

    def env_cmd(var: str, value: str, cmd: str) -> str:
        if IS_WINDOWS:
            return f"set {var}={value} && {cmd}"
        return f"{var}={value} {cmd}"

    return {
        "SessionStart": [
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"{python_cmd} {hook_path('session-recovery')}",
                        "timeout": 5
                    },
                    {
                        "type": "command",
                        "command": f"{python_cmd} {hook_path('session-start')}",
                        "timeout": 10
                    }
                ]
            }
        ],
        "UserPromptSubmit": [
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"{python_cmd} {hook_path('magic-keywords')}",
                        "timeout": 3
                    },
                    {
                        "type": "command",
                        "command": f"{python_cmd} {hook_path('user-prompt-submit')}",
                        "timeout": 5
                    }
                ]
            }
        ],
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"{python_cmd} {hook_path('pre-bash')}"
                    }
                ]
            },
            {
                "matcher": "Edit|Write|MultiEdit",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"{python_cmd} {hook_path('pre-edit')}"
                    }
                ]
            }
        ],
        "PostToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"{python_cmd} {hook_path('post-bash')}"
                    }
                ]
            },
            {
                "matcher": "Edit|Write|MultiEdit",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"{python_cmd} {hook_path('post-edit')}"
                    }
                ]
            }
        ],
        "SubagentStop": [
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"{python_cmd} {hook_path('subagent-stop')}",
                        "timeout": 5
                    },
                    {
                        "type": "command",
                        "command": env_cmd(
                            "CLAUDE_HOOK_EVENT", "SubagentStop",
                            f"{python_cmd} {hook_path('continuation-enforcer')}"
                        ),
                        "timeout": 5
                    }
                ]
            }
        ],
        "PreCompact": [
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"{python_cmd} {hook_path('context-window-monitor')}",
                        "timeout": 5
                    },
                    {
                        "type": "command",
                        "command": f"{python_cmd} {hook_path('pre-compact')}",
                        "timeout": 10
                    }
                ]
            }
        ],
        "Stop": [
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": env_cmd(
                            "CLAUDE_HOOK_EVENT", "Stop",
                            f"{python_cmd} {hook_path('continuation-enforcer')}"
                        ),
                        "timeout": 5
                    },
                    {
                        "type": "command",
                        "command": f"{python_cmd} {hook_path('stop')}"
                    }
                ]
            }
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════
# COMMANDS
# ═══════════════════════════════════════════════════════════════════════════

def install_hooks() -> bool:
    """Install hooks to ~/.claude/hooks"""
    log("\n📦 Installing hooks...", Colors.BOLD)

    source_hooks_dir = REPO_ROOT / "claude" / "hooks"

    if not source_hooks_dir.exists():
        log_warning("No hooks source found in repository.")
        log_info("Creating minimal hooks structure...")
        ensure_dir(HOOKS_DIR)

        # Create minimal utils.py
        utils_content = '''#!/usr/bin/env python3
"""Claude Code Hooks - Utility module"""
import os
import json
import platform
from pathlib import Path

IS_WINDOWS = platform.system() == "Windows"

def get_home_dir():
    return Path.home()

def get_claude_dir():
    return get_home_dir() / ".claude"

def get_project_dir():
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))

def output_context(context):
    print(json.dumps({"additionalContext": context}, ensure_ascii=False))
'''
        (HOOKS_DIR / "utils.py").write_text(utils_content, encoding="utf-8")
        log_success("Created utils.py")
        return True

    # Copy hooks
    ensure_dir(HOOKS_DIR)
    copy_dir(source_hooks_dir, HOOKS_DIR)
    hook_count = len(list(HOOKS_DIR.glob("*.py")))
    log_success(f"Copied {hook_count} hooks to {HOOKS_DIR}")

    return True


def install_commands() -> bool:
    """Install commands to ~/.claude/commands"""
    log("\n📋 Installing commands...", Colors.BOLD)

    source_commands_dir = REPO_ROOT / "claude" / "commands"

    if not source_commands_dir.exists():
        log_warning("No commands source found in repository.")
        return True

    # Copy commands
    ensure_dir(COMMANDS_DIR)

    command_count = 0
    for cmd_file in source_commands_dir.glob("*.md"):
        dest_file = COMMANDS_DIR / cmd_file.name
        shutil.copy(cmd_file, dest_file)
        # Ensure readable permissions (644)
        dest_file.chmod(0o644)
        command_count += 1

    log_success(f"Installed {command_count} commands to {COMMANDS_DIR}")
    log_info("Available commands:")
    for cmd_file in COMMANDS_DIR.glob("*.md"):
        cmd_name = cmd_file.stem
        log(f"  /{cmd_name}", Colors.CYAN)

    return True


def configure_settings() -> bool:
    """Configure settings.json with hooks"""
    log("\n⚙️  Configuring settings.json...", Colors.BOLD)

    ensure_dir(CLAUDE_DIR)

    settings = read_json(SETTINGS_FILE) or {}

    # Backup existing settings
    if SETTINGS_FILE.exists():
        backup_path = SETTINGS_FILE.with_suffix(f".backup.{int(datetime.now().timestamp())}.json")
        shutil.copy(SETTINGS_FILE, backup_path)
        log_info(f"Backed up existing settings to {backup_path.name}")

    # Generate and merge hooks config
    settings["hooks"] = generate_hooks_config()

    # Add schema if not present
    if "$schema" not in settings:
        settings["$schema"] = "https://json.schemastore.org/claude-code-settings.json"

    write_json(SETTINGS_FILE, settings)
    log_success(f"Updated {SETTINGS_FILE}")

    return True


def init_project() -> bool:
    """Initialize current directory as Claude project"""
    log("\n📁 Initializing project...", Colors.BOLD)

    project_dir = Path.cwd()
    claude_dir = project_dir / ".claude"
    knowledge_dir = claude_dir / "knowledge"

    # Create directories
    ensure_dir(claude_dir)
    ensure_dir(knowledge_dir)
    log_success("Created .claude directory structure")

    # Create CLAUDE.md
    claude_md_path = claude_dir / "CLAUDE.md"
    if not claude_md_path.exists():
        project_name = project_dir.name
        claude_md_content = f"""# {project_name}

## Overview
[Project description]

## Quick Start
```bash
# Install dependencies
[package manager command]

# Run development server
[run command]

# Run tests
[test command]
```

## Key Files
- `src/` - Main source code
- `.claude/knowledge/` - Project knowledge

## Context Engineering
@.claude/knowledge/context.md
@.claude/knowledge/decisions.md
@.claude/knowledge/patterns.md
"""
        claude_md_path.write_text(claude_md_content, encoding="utf-8")
        log_success("Created CLAUDE.md")

    # Create knowledge files
    knowledge_files = {
        "context.md": """# Project Context

## Overview
[Project description]

## Tech Stack
- [Language/Framework]

## Key Directories
- `src/` - Source code
- `tests/` - Tests

## Recent Work
<!-- Auto-update area -->
""",
        "decisions.md": """# Architecture Decision Records (ADR)

## Template
### [YYYY-MM-DD] Title
- **Status**: Proposed | Accepted | Deprecated
- **Context**: Why is this decision needed?
- **Decision**: What was decided?
- **Consequences**: What are the implications?
""",
        "patterns.md": """# Code Patterns

## Project Conventions
[Code style, naming rules, etc.]

## Common Patterns
[Document recurring code patterns]
""",
        "errors.md": """# Known Errors and Solutions

## Known Solutions
| Error | Solution |
|-------|----------|
| ModuleNotFoundError | `npm install` or `pip install -r requirements.txt` |
| Connection refused | Check if service is running |
"""
    }

    for filename, content in knowledge_files.items():
        file_path = knowledge_dir / filename
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")
            log_success(f"Created {filename}")

    return True


def run_doctor() -> bool:
    """Run diagnostics"""
    log("\n🔍 Running diagnostics...", Colors.BOLD)

    issues = 0
    checks = []

    # Check Python
    python_cmd = get_python_command()
    if python_cmd:
        checks.append({"name": "Python", "status": "ok", "detail": python_cmd})
    else:
        checks.append({"name": "Python", "status": "error", "detail": "Not found"})
        issues += 1

    # Check Claude directory
    if CLAUDE_DIR.exists():
        checks.append({"name": "~/.claude directory", "status": "ok"})
    else:
        checks.append({"name": "~/.claude directory", "status": "error", "detail": "Not found"})
        issues += 1

    # Check hooks directory
    if HOOKS_DIR.exists():
        hook_files = list(HOOKS_DIR.glob("*.py"))
        checks.append({"name": "Hooks directory", "status": "ok", "detail": f"{len(hook_files)} hooks"})
    else:
        checks.append({"name": "Hooks directory", "status": "warning", "detail": "Not found"})

    # Check commands directory
    if COMMANDS_DIR.exists():
        cmd_files = list(COMMANDS_DIR.glob("*.md"))
        checks.append({"name": "Commands directory", "status": "ok", "detail": f"{len(cmd_files)} commands"})
    else:
        checks.append({"name": "Commands directory", "status": "warning", "detail": "Not found"})

    # Check settings.json
    if SETTINGS_FILE.exists():
        settings = read_json(SETTINGS_FILE)
        if settings and "hooks" in settings:
            checks.append({"name": "settings.json", "status": "ok", "detail": "Hooks configured"})
        else:
            checks.append({"name": "settings.json", "status": "warning", "detail": "No hooks configured"})
    else:
        checks.append({"name": "settings.json", "status": "warning", "detail": "Not found"})

    # Check Claude Code CLI
    try:
        subprocess.run(["claude", "--version"], capture_output=True, check=True)
        checks.append({"name": "Claude Code CLI", "status": "ok"})
    except Exception:
        checks.append({"name": "Claude Code CLI", "status": "warning", "detail": "Not found or not in PATH"})

    # Print results
    log("\nDiagnostic Results:", Colors.BOLD)
    log("─" * 50)

    for check in checks:
        icon = "✓" if check["status"] == "ok" else "⚠" if check["status"] == "warning" else "✗"
        color = Colors.GREEN if check["status"] == "ok" else Colors.YELLOW if check["status"] == "warning" else Colors.RED
        detail = f" ({check.get('detail', '')})" if check.get("detail") else ""
        log(f"{icon} {check['name']}{detail}", color)

    log("─" * 50)

    if issues > 0:
        log_error(f"Found {issues} issue(s). Run 'python scripts/setup.py install' to fix.")
        return False

    log_success("All checks passed!")
    return True


def uninstall() -> bool:
    """Remove hooks configuration"""
    log("\n🗑️  Uninstalling...", Colors.BOLD)

    if SETTINGS_FILE.exists():
        settings = read_json(SETTINGS_FILE)
        if settings and "hooks" in settings:
            del settings["hooks"]
            write_json(SETTINGS_FILE, settings)
            log_success("Removed hooks configuration from settings.json")

    log_warning("Hooks directory preserved at ~/.claude/hooks")
    log_info("To completely remove, manually delete ~/.claude/hooks")

    return True


def install() -> bool:
    """Full installation"""
    log("\n🚀 Claude Context Engineering Setup", Colors.BOLD + Colors.CYAN)
    log("═" * 50)

    steps = [
        ("Installing hooks", install_hooks),
        ("Installing commands", install_commands),
        ("Configuring settings", configure_settings),
    ]

    for i, (name, fn) in enumerate(steps, 1):
        log_step(i, len(steps), name)
        try:
            fn()
        except Exception as e:
            log_error(f"Failed: {e}")
            return False

    log("\n" + "═" * 50)
    log_success("Installation complete!")
    log("\nNext steps:", Colors.BOLD)
    log("  1. Run 'claude' to start Claude Code")
    log("  2. Run 'python scripts/setup.py project' in your project")
    log("  3. Use 'ultrawork' keyword for full feature activation")

    return True


def update() -> bool:
    """Update existing installation from repository"""
    log("\n🔄 Claude Context Engineering Update", Colors.BOLD + Colors.CYAN)
    log("═" * 50)

    # Check if we're in a git repository
    git_dir = REPO_ROOT / ".git"
    if not git_dir.exists():
        log_error("Not in a git repository. Cannot update.")
        log_info("Please run 'git clone' first or update manually.")
        return False

    # Pull latest changes
    log("\n📥 Pulling latest changes...", Colors.BOLD)
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "pull", "--ff-only"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            if "Already up to date" in result.stdout:
                log_info("Already up to date.")
            else:
                log_success("Pulled latest changes")
                log(result.stdout.strip(), Colors.CYAN)
        else:
            log_warning("Git pull failed (may have local changes)")
            log(result.stderr.strip(), Colors.YELLOW)
            log_info("Continuing with local files...")
    except FileNotFoundError:
        log_warning("Git not found. Skipping pull.")
        log_info("Continuing with local files...")

    # Re-install hooks and commands
    steps = [
        ("Updating hooks", install_hooks),
        ("Updating commands", install_commands),
    ]

    for i, (name, fn) in enumerate(steps, 1):
        log_step(i, len(steps), name)
        try:
            fn()
        except Exception as e:
            log_error(f"Failed: {e}")
            return False

    log("\n" + "═" * 50)
    log_success("Update complete!")
    log_info("Settings.json preserved. Run 'config' to update settings if needed.")
    log_info("Restart Claude Code sessions to apply changes.")

    return True


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def print_help():
    platform_name = "Windows" if IS_WINDOWS else "macOS" if IS_MACOS else "Linux"
    print(f"""
{Colors.CYAN}{Colors.BOLD}Claude Context Engineering - Setup Tool (Python){Colors.RESET}

{Colors.BOLD}Usage:{Colors.RESET}
  python scripts/setup.py <command>

{Colors.BOLD}Commands:{Colors.RESET}
  install     Full installation (hooks + commands + config)
  update      Update hooks and commands from repository
  hooks       Install hooks only
  commands    Install commands only
  config      Configure settings.json only
  project     Initialize current directory as Claude project
  doctor      Verify installation and diagnose issues
  uninstall   Remove hooks configuration

{Colors.BOLD}Examples:{Colors.RESET}
  python scripts/setup.py install
  python scripts/setup.py project
  python scripts/setup.py doctor

{Colors.BOLD}Platform:{Colors.RESET} {platform.system()} ({platform_name})
{Colors.BOLD}Home:{Colors.RESET} {HOME_DIR}
{Colors.BOLD}Claude Dir:{Colors.RESET} {CLAUDE_DIR}
""")


def main():
    args = sys.argv[1:]
    command = args[0] if args else "help"

    try:
        if command == "install":
            install()
        elif command == "update":
            update()
        elif command == "hooks":
            install_hooks()
        elif command == "commands":
            install_commands()
        elif command == "config":
            configure_settings()
        elif command in ("project", "init"):
            init_project()
        elif command in ("doctor", "check"):
            run_doctor()
        elif command in ("uninstall", "remove"):
            uninstall()
        else:
            print_help()
    except Exception as e:
        log_error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
