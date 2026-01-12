# Sophia Tools Setup Guide

## Quick Start

1. **Install Node dependencies:**
   ```bash
   cd sophia-tools
   npm install
   ```

2. **Compile TypeScript:**
   ```bash
   npm run compile
   ```

3. **Test Python bridges directly (optional):**
   ```bash
   # Test awaken
   python3 python/awaken_bridge.py /home/burkettdaniel927/projects/isopgem
   
   # Test remember
   python3 python/remember_bridge.py /home/burkettdaniel927/projects/isopgem "Ghost Layer" 5
   
   # Test consult
   python3 python/consult_bridge.py /home/burkettdaniel927/projects/isopgem "pillar sovereignty" covenant
   ```

4. **Run in VS Code Extension Development Host:**
   - Open the `sophia-tools` folder in VS Code
   - Press `F5` to launch the Extension Development Host
   - In the new window, open the IsopGem workspace
   - The tools will be registered and available to AI models

5. **Or package and install:**
   ```bash
   npm install -g @vscode/vsce
   vsce package
   code --install-extension sophia-tools-0.1.0.vsix
   ```

## Tool Usage (AI Invocation)

Once the extension is active, language models can invoke tools:

### sophia_awaken
```json
{
  "workspace_root": "/home/burkettdaniel927/projects/isopgem"
}
```
Returns session context, memory, notes, and crash recovery data.

### sophia_remember
```json
{
  "query": "Ghost Layer implementation",
  "workspace_root": "/home/burkettdaniel927/projects/isopgem",
  "max_results": 5
}
```
Returns relevant memory entries.

### sophia_dream
```json
{
  "insight": "Consider implementing AST-based covenant verification",
  "category": "architecture",
  "workspace_root": "/home/burkettdaniel927/projects/isopgem"
}
```
Records creative insight to DREAMS.md.

### sophia_slumber
```json
{
  "chronicle": "Today we created the Sophia Tools extension...",
  "wisdom": ["TypeScript tool registration requires precise JSON schemas"],
  "skills": ["VS Code Language Model Tools API"],
  "workspace_root": "/home/burkettdaniel927/projects/isopgem"
}
```
Archives session state and increments counter.

### sophia_consult
```json
{
  "query": "UI purity requirements",
  "scope": "covenant",
  "workspace_root": "/home/burkettdaniel927/projects/isopgem"
}
```
Returns relevant covenant/wiki sections.

### sophia_verify
```json
{
  "check_type": "pillar_sovereignty",
  "workspace_root": "/home/burkettdaniel927/projects/isopgem"
}
```
Checks architectural rules and returns violations.

## Development

- **Watch mode**: `npm run watch` (auto-recompile on changes)
- **Reload extension**: In Extension Development Host, press `Ctrl+R` to reload
- **View logs**: Open Developer Tools in Extension Development Host

## Troubleshooting

- **Tools not appearing**: Check VS Code version (needs 1.95.0+)
- **Python errors**: Ensure Python 3.8+ is available as `python3`
- **Path issues**: All paths must be absolute (workspace_root)
