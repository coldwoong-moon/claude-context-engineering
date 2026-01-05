#!/usr/bin/env node
/**
 * Claude Context Engineering - Cross-Platform Setup Script
 *
 * Usage:
 *   npx claude-context-engineering install    # Full installation
 *   npx claude-context-engineering hooks      # Install hooks only
 *   npx claude-context-engineering config     # Configure settings.json
 *   npx claude-context-engineering project    # Initialize current project
 *   npx claude-context-engineering doctor     # Verify installation
 *   npx claude-context-engineering uninstall  # Remove installation
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

// ═══════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════

const IS_WINDOWS = process.platform === 'win32';
const IS_MACOS = process.platform === 'darwin';
const IS_LINUX = process.platform === 'linux';

const HOME_DIR = os.homedir();
const CLAUDE_DIR = path.join(HOME_DIR, '.claude');
const HOOKS_DIR = path.join(CLAUDE_DIR, 'hooks');
const COMMANDS_DIR = path.join(CLAUDE_DIR, 'commands');
const SETTINGS_FILE = path.join(CLAUDE_DIR, 'settings.json');

const SCRIPT_DIR = __dirname;
const REPO_ROOT = path.dirname(SCRIPT_DIR);

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

// ═══════════════════════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

function log(message, color = '') {
  console.log(`${color}${message}${colors.reset}`);
}

function logSuccess(message) {
  log(`✓ ${message}`, colors.green);
}

function logError(message) {
  log(`✗ ${message}`, colors.red);
}

function logWarning(message) {
  log(`⚠ ${message}`, colors.yellow);
}

function logInfo(message) {
  log(`ℹ ${message}`, colors.blue);
}

function logStep(step, total, message) {
  log(`[${step}/${total}] ${message}`, colors.cyan);
}

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    return true;
  }
  return false;
}

function copyFile(src, dest) {
  fs.copyFileSync(src, dest);
}

function copyDir(src, dest) {
  ensureDir(dest);
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      copyFile(srcPath, destPath);
    }
  }
}

function fileExists(filePath) {
  return fs.existsSync(filePath);
}

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch {
    return null;
  }
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf-8');
}

function getPythonCommand() {
  // Try to find Python
  const commands = IS_WINDOWS
    ? ['python', 'python3', 'py -3']
    : ['python3', 'python'];

  for (const cmd of commands) {
    try {
      execSync(`${cmd} --version`, { stdio: 'pipe' });
      return cmd.split(' ')[0]; // Return just 'python' or 'python3'
    } catch {
      continue;
    }
  }
  return null;
}

function getHookCommand(hookName) {
  const pythonCmd = IS_WINDOWS ? 'python' : 'python';
  const hooksPath = IS_WINDOWS
    ? `%USERPROFILE%\\.claude\\hooks\\${hookName}.py`
    : `~/.claude/hooks/${hookName}.py`;

  if (IS_WINDOWS) {
    return `${pythonCmd} "${hooksPath}"`;
  }
  return `${pythonCmd} ${hooksPath}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// HOOKS CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

function generateHooksConfig() {
  const pythonCmd = 'python';
  const hooksPath = IS_WINDOWS ? '%USERPROFILE%\\.claude\\hooks' : '~/.claude/hooks';
  const envPrefix = IS_WINDOWS ? 'set ' : '';
  const envSuffix = IS_WINDOWS ? ' && ' : ' ';

  const quote = IS_WINDOWS ? '"' : '';
  const sep = IS_WINDOWS ? '\\' : '/';

  const hookPath = (name) => IS_WINDOWS
    ? `"${hooksPath}${sep}${name}.py"`
    : `${hooksPath}/${name}.py`;

  return {
    SessionStart: [
      {
        matcher: '',
        hooks: [
          {
            type: 'command',
            command: `${pythonCmd} ${hookPath('session-recovery')}`,
            timeout: 5
          },
          {
            type: 'command',
            command: `${pythonCmd} ${hookPath('session-start')}`,
            timeout: 10
          }
        ]
      }
    ],
    UserPromptSubmit: [
      {
        matcher: '',
        hooks: [
          {
            type: 'command',
            command: `${pythonCmd} ${hookPath('magic-keywords')}`,
            timeout: 3
          },
          {
            type: 'command',
            command: `${pythonCmd} ${hookPath('user-prompt-submit')}`,
            timeout: 5
          }
        ]
      }
    ],
    PreToolUse: [
      {
        matcher: 'Bash',
        hooks: [
          {
            type: 'command',
            command: `${pythonCmd} ${hookPath('pre-bash')}`
          }
        ]
      },
      {
        matcher: 'Edit|Write|MultiEdit',
        hooks: [
          {
            type: 'command',
            command: `${pythonCmd} ${hookPath('pre-edit')}`
          }
        ]
      }
    ],
    PostToolUse: [
      {
        matcher: 'Bash',
        hooks: [
          {
            type: 'command',
            command: `${pythonCmd} ${hookPath('post-bash')}`
          }
        ]
      },
      {
        matcher: 'Edit|Write|MultiEdit',
        hooks: [
          {
            type: 'command',
            command: `${pythonCmd} ${hookPath('post-edit')}`
          }
        ]
      }
    ],
    SubagentStop: [
      {
        matcher: '',
        hooks: [
          {
            type: 'command',
            command: `${pythonCmd} ${hookPath('subagent-stop')}`,
            timeout: 5
          },
          {
            type: 'command',
            command: IS_WINDOWS
              ? `set CLAUDE_HOOK_EVENT=SubagentStop && ${pythonCmd} ${hookPath('continuation-enforcer')}`
              : `CLAUDE_HOOK_EVENT=SubagentStop ${pythonCmd} ${hookPath('continuation-enforcer')}`,
            timeout: 5
          }
        ]
      }
    ],
    PreCompact: [
      {
        matcher: '',
        hooks: [
          {
            type: 'command',
            command: `${pythonCmd} ${hookPath('context-window-monitor')}`,
            timeout: 5
          },
          {
            type: 'command',
            command: `${pythonCmd} ${hookPath('pre-compact')}`,
            timeout: 10
          }
        ]
      }
    ],
    Stop: [
      {
        matcher: '',
        hooks: [
          {
            type: 'command',
            command: IS_WINDOWS
              ? `set CLAUDE_HOOK_EVENT=Stop && ${pythonCmd} ${hookPath('continuation-enforcer')}`
              : `CLAUDE_HOOK_EVENT=Stop ${pythonCmd} ${hookPath('continuation-enforcer')}`,
            timeout: 5
          },
          {
            type: 'command',
            command: `${pythonCmd} ${hookPath('stop')}`
          }
        ]
      }
    ]
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// COMMANDS
// ═══════════════════════════════════════════════════════════════════════════

async function installHooks() {
  log('\n📦 Installing hooks...', colors.bright);

  // Check for hooks source
  const sourceHooksDir = path.join(REPO_ROOT, 'hooks');
  const globalHooksSource = path.join(HOME_DIR, '.claude', 'hooks');

  let hooksSource = null;
  if (fileExists(sourceHooksDir)) {
    hooksSource = sourceHooksDir;
  } else if (fileExists(globalHooksSource)) {
    logInfo('Using existing hooks from ~/.claude/hooks');
    return true;
  }

  if (!hooksSource) {
    logWarning('No hooks source found. Creating minimal hooks structure...');
    ensureDir(HOOKS_DIR);

    // Create minimal utils.py
    const utilsContent = `#!/usr/bin/env python3
"""Claude Code Hooks - Utility module"""
import os
import json
import platform
from pathlib import Path

IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

def get_home_dir():
    return Path.home()

def get_claude_dir():
    return get_home_dir() / ".claude"

def get_project_dir():
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))

def output_context(context):
    print(json.dumps({"additionalContext": context}, ensure_ascii=False))
`;
    fs.writeFileSync(path.join(HOOKS_DIR, 'utils.py'), utilsContent);
    logSuccess('Created utils.py');
    return true;
  }

  // Copy hooks
  ensureDir(HOOKS_DIR);
  copyDir(hooksSource, HOOKS_DIR);
  logSuccess(`Copied hooks to ${HOOKS_DIR}`);

  return true;
}

async function installCommands() {
  log('\n📋 Installing commands...', colors.bright);

  const sourceCommandsDir = path.join(REPO_ROOT, 'commands');

  if (!fileExists(sourceCommandsDir)) {
    logWarning('No commands source found in repository.');
    return true;
  }

  // Copy commands
  ensureDir(COMMANDS_DIR);

  let commandCount = 0;
  const commandFiles = fs.readdirSync(sourceCommandsDir).filter(f => f.endsWith('.md'));

  for (const cmdFile of commandFiles) {
    const srcPath = path.join(sourceCommandsDir, cmdFile);
    const destPath = path.join(COMMANDS_DIR, cmdFile);
    copyFile(srcPath, destPath);
    // Ensure readable permissions (644)
    fs.chmodSync(destPath, 0o644);
    commandCount++;
  }

  logSuccess(`Installed ${commandCount} commands to ${COMMANDS_DIR}`);
  logInfo('Available commands:');

  for (const cmdFile of commandFiles) {
    const cmdName = path.basename(cmdFile, '.md');
    log(`  /${cmdName}`, colors.cyan);
  }

  return true;
}

async function configureSettings() {
  log('\n⚙️  Configuring settings.json...', colors.bright);

  ensureDir(CLAUDE_DIR);

  let settings = readJson(SETTINGS_FILE) || {};

  // Backup existing settings
  if (fileExists(SETTINGS_FILE)) {
    const backupPath = `${SETTINGS_FILE}.backup.${Date.now()}`;
    copyFile(SETTINGS_FILE, backupPath);
    logInfo(`Backed up existing settings to ${path.basename(backupPath)}`);
  }

  // Generate and merge hooks config
  const hooksConfig = generateHooksConfig();
  settings.hooks = hooksConfig;

  // Add schema if not present
  if (!settings.$schema) {
    settings.$schema = 'https://json.schemastore.org/claude-code-settings.json';
  }

  writeJson(SETTINGS_FILE, settings);
  logSuccess(`Updated ${SETTINGS_FILE}`);

  return true;
}

async function initProject() {
  log('\n📁 Initializing project...', colors.bright);

  const projectDir = process.cwd();
  const claudeDir = path.join(projectDir, '.claude');
  const knowledgeDir = path.join(claudeDir, 'knowledge');

  // Create directories
  ensureDir(claudeDir);
  ensureDir(knowledgeDir);
  logSuccess('Created .claude directory structure');

  // Create CLAUDE.md if not exists
  const claudeMdPath = path.join(claudeDir, 'CLAUDE.md');
  if (!fileExists(claudeMdPath)) {
    const projectName = path.basename(projectDir);
    const claudeMdContent = `# ${projectName}

## Overview
[Project description]

## Quick Start
\`\`\`bash
# Install dependencies
[package manager command]

# Run development server
[run command]

# Run tests
[test command]
\`\`\`

## Key Files
- \`src/\` - Main source code
- \`.claude/knowledge/\` - Project knowledge

## Context Engineering
@.claude/knowledge/context.md
@.claude/knowledge/decisions.md
@.claude/knowledge/patterns.md
`;
    fs.writeFileSync(claudeMdPath, claudeMdContent);
    logSuccess('Created CLAUDE.md');
  }

  // Create knowledge files
  const knowledgeFiles = {
    'context.md': `# Project Context

## Overview
[Project description]

## Tech Stack
- [Language/Framework]

## Key Directories
- \`src/\` - Source code
- \`tests/\` - Tests

## Recent Work
<!-- Auto-update area -->
`,
    'decisions.md': `# Architecture Decision Records (ADR)

## Template
### [YYYY-MM-DD] Title
- **Status**: Proposed | Accepted | Deprecated
- **Context**: Why is this decision needed?
- **Decision**: What was decided?
- **Consequences**: What are the implications?
`,
    'patterns.md': `# Code Patterns

## Project Conventions
[Code style, naming rules, etc.]

## Common Patterns
[Document recurring code patterns]
`,
    'errors.md': `# Known Errors and Solutions

## Known Solutions
| Error | Solution |
|-------|----------|
| ModuleNotFoundError | \`npm install\` or \`pip install -r requirements.txt\` |
| Connection refused | Check if service is running |
`
  };

  for (const [filename, content] of Object.entries(knowledgeFiles)) {
    const filePath = path.join(knowledgeDir, filename);
    if (!fileExists(filePath)) {
      fs.writeFileSync(filePath, content);
      logSuccess(`Created ${filename}`);
    }
  }

  return true;
}

async function runDoctor() {
  log('\n🔍 Running diagnostics...', colors.bright);

  let issues = 0;
  const checks = [];

  // Check Python
  const pythonCmd = getPythonCommand();
  if (pythonCmd) {
    checks.push({ name: 'Python', status: 'ok', detail: pythonCmd });
  } else {
    checks.push({ name: 'Python', status: 'error', detail: 'Not found' });
    issues++;
  }

  // Check Claude directory
  if (fileExists(CLAUDE_DIR)) {
    checks.push({ name: '~/.claude directory', status: 'ok' });
  } else {
    checks.push({ name: '~/.claude directory', status: 'error', detail: 'Not found' });
    issues++;
  }

  // Check hooks directory
  if (fileExists(HOOKS_DIR)) {
    const hookFiles = fs.readdirSync(HOOKS_DIR).filter(f => f.endsWith('.py'));
    checks.push({ name: 'Hooks directory', status: 'ok', detail: `${hookFiles.length} hooks` });
  } else {
    checks.push({ name: 'Hooks directory', status: 'warning', detail: 'Not found' });
  }

  // Check commands directory
  if (fileExists(COMMANDS_DIR)) {
    const cmdFiles = fs.readdirSync(COMMANDS_DIR).filter(f => f.endsWith('.md'));
    checks.push({ name: 'Commands directory', status: 'ok', detail: `${cmdFiles.length} commands` });
  } else {
    checks.push({ name: 'Commands directory', status: 'warning', detail: 'Not found' });
  }

  // Check settings.json
  if (fileExists(SETTINGS_FILE)) {
    const settings = readJson(SETTINGS_FILE);
    if (settings?.hooks) {
      checks.push({ name: 'settings.json', status: 'ok', detail: 'Hooks configured' });
    } else {
      checks.push({ name: 'settings.json', status: 'warning', detail: 'No hooks configured' });
    }
  } else {
    checks.push({ name: 'settings.json', status: 'warning', detail: 'Not found' });
  }

  // Check Claude Code CLI
  try {
    execSync('claude --version', { stdio: 'pipe' });
    checks.push({ name: 'Claude Code CLI', status: 'ok' });
  } catch {
    checks.push({ name: 'Claude Code CLI', status: 'warning', detail: 'Not found or not in PATH' });
  }

  // Print results
  log('\nDiagnostic Results:', colors.bright);
  log('─'.repeat(50));

  for (const check of checks) {
    const icon = check.status === 'ok' ? '✓' : check.status === 'warning' ? '⚠' : '✗';
    const color = check.status === 'ok' ? colors.green : check.status === 'warning' ? colors.yellow : colors.red;
    const detail = check.detail ? ` (${check.detail})` : '';
    log(`${icon} ${check.name}${detail}`, color);
  }

  log('─'.repeat(50));

  if (issues > 0) {
    logError(`Found ${issues} issue(s). Run 'npx claude-context-engineering install' to fix.`);
    return false;
  }

  logSuccess('All checks passed!');
  return true;
}

async function uninstall() {
  log('\n🗑️  Uninstalling...', colors.bright);

  // Remove hooks config from settings.json
  if (fileExists(SETTINGS_FILE)) {
    const settings = readJson(SETTINGS_FILE);
    if (settings) {
      delete settings.hooks;
      writeJson(SETTINGS_FILE, settings);
      logSuccess('Removed hooks configuration from settings.json');
    }
  }

  // Optionally remove hooks directory
  logWarning('Hooks directory preserved at ~/.claude/hooks');
  logInfo('To completely remove, manually delete ~/.claude/hooks');

  return true;
}

async function install() {
  log('\n🚀 Claude Context Engineering Setup', colors.bright + colors.cyan);
  log('═'.repeat(50));

  const steps = [
    { name: 'Installing hooks', fn: installHooks },
    { name: 'Installing commands', fn: installCommands },
    { name: 'Configuring settings', fn: configureSettings },
  ];

  const total = steps.length;

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    logStep(i + 1, total, step.name);

    try {
      await step.fn();
    } catch (err) {
      logError(`Failed: ${err.message}`);
      return false;
    }
  }

  log('\n' + '═'.repeat(50));
  logSuccess('Installation complete!');
  log('\nNext steps:', colors.bright);
  log('  1. Run "claude" to start Claude Code');
  log('  2. Run "npx claude-context-engineering project" in your project');
  log('  3. Use "ultrawork" keyword for full feature activation');

  return true;
}

async function update() {
  log('\n🔄 Claude Context Engineering Update', colors.bright + colors.cyan);
  log('═'.repeat(50));

  // Check if we're in a git repository
  const gitDir = path.join(REPO_ROOT, '.git');
  if (!fileExists(gitDir)) {
    logError('Not in a git repository. Cannot update.');
    logInfo('Please run "git clone" first or update manually.');
    return false;
  }

  // Pull latest changes
  log('\n📥 Pulling latest changes...', colors.bright);
  try {
    const result = execSync(`git -C "${REPO_ROOT}" pull --ff-only`, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe']
    });
    if (result.includes('Already up to date')) {
      logInfo('Already up to date.');
    } else {
      logSuccess('Pulled latest changes');
      log(result.trim(), colors.cyan);
    }
  } catch (err) {
    if (err.stderr) {
      logWarning('Git pull failed (may have local changes)');
      log(err.stderr.trim(), colors.yellow);
    } else {
      logWarning('Git not found. Skipping pull.');
    }
    logInfo('Continuing with local files...');
  }

  // Re-install hooks and commands
  const steps = [
    { name: 'Updating hooks', fn: installHooks },
    { name: 'Updating commands', fn: installCommands },
  ];

  const total = steps.length;

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    logStep(i + 1, total, step.name);

    try {
      await step.fn();
    } catch (err) {
      logError(`Failed: ${err.message}`);
      return false;
    }
  }

  log('\n' + '═'.repeat(50));
  logSuccess('Update complete!');
  logInfo('Settings.json preserved. Run "config" to update settings if needed.');
  logInfo('Restart Claude Code sessions to apply changes.');

  return true;
}

// ═══════════════════════════════════════════════════════════════════════════
// CLI
// ═══════════════════════════════════════════════════════════════════════════

function printHelp() {
  log(`
${colors.cyan}${colors.bright}Claude Context Engineering - Setup Tool${colors.reset}

${colors.bright}Usage:${colors.reset}
  npx claude-context-engineering <command>

${colors.bright}Commands:${colors.reset}
  install     Full installation (hooks + commands + config)
  update      Update hooks and commands from repository
  hooks       Install hooks only
  commands    Install commands only
  config      Configure settings.json only
  project     Initialize current directory as Claude project
  doctor      Verify installation and diagnose issues
  uninstall   Remove hooks configuration

${colors.bright}Examples:${colors.reset}
  npx claude-context-engineering install
  npx claude-context-engineering project
  npx claude-context-engineering doctor

${colors.bright}Platform:${colors.reset} ${process.platform} (${IS_WINDOWS ? 'Windows' : IS_MACOS ? 'macOS' : 'Linux'})
${colors.bright}Home:${colors.reset} ${HOME_DIR}
${colors.bright}Claude Dir:${colors.reset} ${CLAUDE_DIR}
`);
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'help';

  try {
    switch (command) {
      case 'install':
        await install();
        break;
      case 'update':
        await update();
        break;
      case 'hooks':
        await installHooks();
        break;
      case 'commands':
        await installCommands();
        break;
      case 'config':
        await configureSettings();
        break;
      case 'project':
      case 'init':
        await initProject();
        break;
      case 'doctor':
      case 'check':
        await runDoctor();
        break;
      case 'uninstall':
      case 'remove':
        await uninstall();
        break;
      case 'help':
      case '--help':
      case '-h':
      default:
        printHelp();
        break;
    }
  } catch (err) {
    logError(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
