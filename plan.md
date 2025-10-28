# Integration Plan: Add `logfire init` Command to Logfire CLI

## Executive Summary

This plan outlines the integration of `logfire-setup` functionality into the official logfire CLI as a `logfire init` command. The integration will maintain backward compatibility with the standalone `uvx logfire-setup` package while providing a more discoverable and unified CLI experience.

---

## Rationale

### Why Integrate?

1. **Discoverability**: Users will find the init functionality through `logfire --help`
2. **Consistency**: Follows industry patterns (`npm init`, `cargo init`, `poetry init`)
3. **Unified Experience**: Single installation for all logfire tools
4. **Code Reuse**: Share auth, API client, and detection logic with existing commands
5. **Maintenance**: Single codebase reduces duplication

### Why Keep Both?

- Backward compatibility for existing users of `uvx logfire-setup`
- Allows gradual migration path
- Standalone package can serve as development/testing ground for new features

---

## Research Findings

### 1. Logfire CLI Architecture

**Command Registration Pattern** (`logfire/_internal/cli/__init__.py`):
- Uses `argparse` with subparsers
- Each command has `parse_<command>` function
- Complex commands live in separate modules (`auth.py`, `run.py`, `prompt.py`)
- Commands registered around line 315+

**Existing Commands**:
- `auth` - Authentication flow
- `clean` - Remove Logfire data
- `inspect` - Inspect packages and recommend instrumentations
- `whoami` - Show authentication status
- `projects` (list/new/use) - Project management
- `read-tokens create` - Token management
- `prompt` - Agent verification
- `info` - Version information
- `run` - Run scripts with instrumentation

### 2. HTTP Client Discovery

**Key Finding**: Logfire uses `requests`, NOT `httpx`

Evidence:
- `logfire/_internal/auth.py:13` imports `requests`
- `logfire/_internal/cli/__init__.py:16` imports `requests`
- `logfire/_internal/client.py:6` imports `Session` from `requests`
- CLI creates `requests.Session()` at line 415

**Existing API Client**:
- Location: `logfire/_internal/client.py`
- Class: `LogfireClient`
- Method: `get_user_projects()` calls `/v1/writable-projects/`
- Pattern: Uses `requests.Session` with header management

**Implication**: Replace httpx with requests in logfire-setup code to match logfire's architecture.

### 3. Dependency Analysis

**Current logfire dependencies**:
```python
dependencies = [
    "opentelemetry-sdk >= 1.35.0, < 1.39.0",
    "opentelemetry-exporter-otlp-proto-http >= 1.35.0, < 1.39.0",
    "opentelemetry-instrumentation >= 0.41b0",
    "rich >= 13.4.2",           # ← Already included
    "protobuf >= 4.23.4",
    "typing-extensions >= 4.1.0",
    "tomli >= 2.0.1; python_version < '3.11'",  # ← Already included
    "executing >= 2.0.1",
]
```

**Current logfire-setup dependencies**:
```python
dependencies = [
    "httpx>=0.28.1",           # ← Replace with requests (already in logfire)
    "questionary>=2.1.1",      # ← NEW (only dependency to add)
    "rich>=14.2.0",            # ← Already in logfire
    "tomli>=2.3.0",            # ← Already in logfire
]
```

**New Dependencies Needed**:
- **questionary** (~50KB) + **prompt_toolkit** (~500KB) = ~550KB total
- **requests**: Already in logfire (used extensively)

**Strategy**: Make questionary optional via `[init]` extra to keep base logfire lean.

### 4. Code Reuse Opportunities

**Can reuse from logfire**:
- `LogfireClient.get_user_projects()` - API call to `/v1/writable-projects/`
- Authentication patterns from `logfire/_internal/auth.py`
- `UserTokenCollection` for reading `~/.logfire/default.toml`
- Project selection logic from `projects use` command

**Cannot directly import**:
- `LogfireClient` is in `_internal` (not public API)
- Would need to copy patterns, not import classes

**Recommendation**: Port the patterns and logic rather than trying to import internal modules.

---

## Architecture Decisions

### Decision 1: Optional Dependencies

**Choice**: Use `[init]` extra for questionary

```toml
[project.optional-dependencies]
init = ["questionary >= 2.1.1"]
```

**Rationale**:
- Keeps base logfire lean
- Users who don't need interactive setup don't pay the cost
- Allows graceful degradation with helpful error messages

### Decision 2: Replace httpx with requests

**Choice**: Port api_client.py to use requests and follow LogfireClient patterns

**Rationale**:
- Consistency with logfire's existing architecture
- Removes unnecessary dependency (httpx)
- Can reuse existing session management patterns

### Decision 3: Code Organization

**Choice**: Create `logfire/_internal/cli/init/` directory

```
logfire/_internal/cli/init/
├── __init__.py         # Main parse_init function, imports other modules
├── categories.py       # Integration definitions (from logfire-setup)
├── detector.py         # Dependency detection (from logfire-setup)
├── installer.py        # Installation logic (from logfire-setup)
├── auth_checker.py     # Auth status checks (adapted to use logfire auth)
├── mcp_checker.py      # MCP configuration (from logfire-setup)
├── instructions.py     # Documentation generation (from logfire-setup)
└── agents_md.py        # AGENTS.md/CLAUDE.md handling (from logfire-setup)
```

**Rationale**:
- Follows existing pattern for complex commands (auth.py, run.py, prompt.py)
- Isolates init functionality
- Makes code easy to find and maintain

### Decision 4: Direct Function Calls vs Subprocess

**Choice**: Replace subprocess calls with direct function calls

**Examples**:
- Instead of `subprocess.run(["logfire", "projects", "use", ...])`, call the function directly
- Instead of shelling out for auth check, use existing auth module

**Rationale**:
- Faster execution
- Better error handling
- Reduces dependencies on external commands

### Decision 5: Backward Compatibility

**Choice**: Keep logfire-setup as standalone package

**Rationale**:
- Existing users rely on `uvx logfire-setup`
- Gradual migration path
- Can deprecate later if needed

---

## Implementation Plan

### Phase 1: Prepare Logfire Repository

**Task 1.1**: Add optional dependency to `../logfire/pyproject.toml`

```toml
[project.optional-dependencies]
init = ["questionary >= 2.1.1"]
```

**Task 1.2**: Create directory structure

```bash
mkdir -p ../logfire/logfire/_internal/cli/init
```

### Phase 2: Port Core Modules

**Task 2.1**: Port `categories.py` (minimal changes)
- Copy from logfire-setup/logfire_setup/categories.py
- To: ../logfire/logfire/_internal/cli/init/categories.py
- Changes: None needed (pure data structure)

**Task 2.2**: Port `detector.py` (minimal changes)
- Copy from logfire-setup/logfire_setup/detector.py
- To: ../logfire/logfire/_internal/cli/init/detector.py
- Changes: Update imports to use local modules

**Task 2.3**: Port `mcp_checker.py` (minimal changes)
- Copy from logfire-setup/logfire_setup/mcp_checker.py
- To: ../logfire/logfire/_internal/cli/init/mcp_checker.py
- Changes: Update imports

**Task 2.4**: Port `installer.py` (minimal changes)
- Copy from logfire-setup/logfire_setup/installer.py
- To: ../logfire/logfire/_internal/cli/init/installer.py
- Changes: Update imports

**Task 2.5**: Port `instructions.py` (minimal changes)
- Copy from logfire-setup/logfire_setup/instructions.py
- To: ../logfire/logfire/_internal/cli/init/instructions.py
- Changes: Update imports

**Task 2.6**: Port `agents_md.py` (minimal changes)
- Copy from logfire-setup/logfire_setup/agents_md.py
- To: ../logfire/logfire/_internal/cli/init/agents_md.py
- Changes: Update imports

### Phase 3: Adapt Authentication and API

**Task 3.1**: Adapt `auth_checker.py`
- Copy from logfire-setup/logfire_setup/auth_checker.py
- To: ../logfire/logfire/_internal/cli/init/auth_checker.py
- Changes:
  - Reuse `UserTokenCollection` from `logfire/_internal/auth.py`
  - Use logfire's existing auth validation logic
  - Remove redundant token parsing code

**Task 3.2**: Replace API client with requests-based version
- Remove: api_client.py (httpx-based)
- Solution: Use `LogfireClient.get_user_projects()` directly in main init flow
- OR: Create minimal wrapper in `init/__init__.py` using requests

### Phase 4: Create Main Init Entry Point

**Task 4.1**: Create `../logfire/logfire/_internal/cli/init/__init__.py`

This file will:
1. Import all ported modules
2. Define `parse_init(args: argparse.Namespace) -> None` function
3. Handle lazy imports of questionary with graceful error
4. Implement the main flow (currently in logfire-setup/logfire_setup/main.py)
5. Replace subprocess calls with direct function calls

**Key changes from logfire-setup/main.py**:
- Convert `main()` to `parse_init(args)`
- Lazy import questionary with try/except
- Use `args._session` (requests.Session) for API calls
- Call logfire functions directly instead of subprocess
- Handle `--skip-auth`, `--skip-mcp` flags from args

### Phase 5: Register Command

**Task 5.1**: Register init command in `../logfire/logfire/_internal/cli/__init__.py`

Add around line 375 (after `cmd_info`):

```python
from .init import parse_init  # Will handle lazy imports internally

# ... existing code ...

cmd_init = subparsers.add_parser(
    'init',
    help='Interactive setup for Logfire with optional dependencies',
    description='Guide you through setting up Logfire in your project with framework-specific integrations'
)
cmd_init.add_argument(
    '--skip-auth',
    action='store_true',
    help='Skip authentication check'
)
cmd_init.add_argument(
    '--skip-mcp',
    action='store_true',
    help='Skip MCP configuration check'
)
cmd_init.set_defaults(func=parse_init)
```

### Phase 6: Update Documentation

**Task 6.1**: Update logfire-setup README

Add section:
```markdown
## Recommended: Use `logfire init`

The functionality of `logfire-setup` is now available as `logfire init` in the main logfire CLI:

```bash
# Install logfire with init support
pip install logfire[init]

# Run interactive setup
logfire init
```

Alternatively, continue using the standalone package:

```bash
uvx logfire-setup
```
```

---

## Implementation Details

### Handling Lazy Imports

Pattern for questionary in `init/__init__.py`:

```python
def parse_init(args: argparse.Namespace) -> None:
    """Interactive setup for Logfire with optional dependencies."""
    try:
        import questionary
    except ImportError:
        console.print(
            "[red]Error:[/red] The init command requires additional dependencies.\n"
            "Install with: [bold]pip install logfire[init][/bold] or [bold]uv add logfire[init][/bold]"
        )
        sys.exit(1)

    # Continue with init logic...
```

### Replacing Subprocess Calls

**Before (logfire-setup)**:
```python
subprocess.run(
    ["logfire", "projects", "use", project_name],
    check=False
)
```

**After (logfire init)**:
```python
from ...auth import UserTokenCollection  # logfire internal
from ...client import LogfireClient

# Get authenticated client
session = args._session
client = LogfireClient(session=session, base_url=LOGFIRE_BASE_URL)

# Call directly
projects = client.get_user_projects()
# ... handle project selection ...
# ... call project use logic directly ...
```

### Reusing LogfireClient

**Pattern for API calls in init/__init__.py**:

```python
def parse_init(args: argparse.Namespace) -> None:
    # ... questionary import ...

    from ...client import LogfireClient
    from ...config import LOGFIRE_BASE_URL

    # Create client with session from args
    client = LogfireClient(session=args._session, base_url=LOGFIRE_BASE_URL)

    # Fetch projects
    try:
        projects = client.get_user_projects()
    except Exception as e:
        console.print(f"[red]Error fetching projects:[/red] {e}")
        sys.exit(1)

    # ... rest of init flow ...
```

---

## Testing Strategy

### Test 1: Without Optional Dependencies

```bash
cd ../logfire
pip install -e .  # Without [init]
logfire init
# Expected: Graceful error message about missing dependencies
```

Expected output:
```
Error: The init command requires additional dependencies.
Install with: pip install logfire[init] or uv add logfire[init]
```

### Test 2: With Optional Dependencies

```bash
cd ../logfire
pip install -e .[init]
logfire init
# Expected: Full interactive flow works
```

Should:
1. Check authentication
2. Show project selection with arrow keys
3. Detect existing dependencies
4. Show checkbox prompts for integrations
5. Install logfire with selected extras
6. Check MCP configuration
7. Generate documentation

### Test 3: Backward Compatibility

```bash
cd ../logfire-setup
uvx logfire-setup
# Expected: Still works independently
```

### Test 4: Integration Tests

Create test script:

```python
# ../logfire/tests/test_init_command.py

def test_init_lazy_import():
    """Test that init command fails gracefully without questionary."""
    # ... test logic ...

def test_init_full_flow():
    """Test complete init flow with mocked API calls."""
    # ... test logic ...

def test_detector_integration():
    """Test that detector correctly identifies dependencies."""
    # ... test logic ...
```

---

## Migration Path

### For New Users

```bash
# Recommended approach
pip install logfire[init]
logfire init
```

### For Existing logfire-setup Users

```bash
# Continue using standalone (works as before)
uvx logfire-setup

# Or migrate to integrated version
pip install logfire[init]
logfire init
```

### Documentation Updates

**logfire README**:
- Add init command to CLI commands list
- Show example usage

**logfire-setup README**:
- Note that logfire init is now preferred
- Keep installation instructions for backward compat
- Add migration note

---

## Risks and Mitigations

### Risk 1: Dependency Bloat

**Risk**: Adding questionary increases package size

**Mitigation**:
- Use optional dependencies `[init]`
- Base logfire remains lean
- Clear documentation about when to use [init]

### Risk 2: Breaking Changes in logfire

**Risk**: Changes to internal APIs could break init command

**Mitigation**:
- Minimize reliance on internal APIs
- Use stable patterns (requests.Session, argparse.Namespace)
- Test suite catches breakages

### Risk 3: Confusion Between Two Packages

**Risk**: Users unsure which to use (logfire-setup vs logfire init)

**Mitigation**:
- Clear documentation
- Deprecation warnings in logfire-setup (future)
- Consistent messaging

### Risk 4: Code Duplication

**Risk**: Maintaining similar code in two places

**Mitigation**:
- Short term: Keep both during transition
- Long term: Deprecate logfire-setup or make it a thin wrapper
- Document which is canonical

---

## Success Criteria

1. ✅ `logfire init` command works with `pip install logfire[init]`
2. ✅ Graceful error without [init] extra
3. ✅ Reuses logfire's requests-based HTTP client
4. ✅ No httpx dependency added to logfire
5. ✅ `uvx logfire-setup` continues to work
6. ✅ All tests pass
7. ✅ Documentation updated

---

## Timeline Estimate

- **Phase 1**: 30 minutes (dependencies, directory)
- **Phase 2**: 1 hour (port 6 modules with imports)
- **Phase 3**: 45 minutes (adapt auth and API)
- **Phase 4**: 1 hour (create main init entry point)
- **Phase 5**: 15 minutes (register command)
- **Phase 6**: 30 minutes (documentation)
- **Testing**: 1 hour (comprehensive testing)

**Total**: ~5 hours

---

## Future Enhancements

1. **Merge with inspect command**: `logfire inspect` and `logfire init` have overlapping detection logic
2. **Share instrumentation mappings**: Use same Integration definitions in `run`, `inspect`, and `init`
3. **Deprecate logfire-setup**: Once stable, consider deprecating standalone package
4. **Enhanced detection**: Use AST parsing to detect framework usage, not just dependencies
5. **Template generation**: Generate starter code for detected frameworks

---

## References

- Logfire CLI: `../logfire/logfire/_internal/cli/__init__.py`
- Logfire Client: `../logfire/logfire/_internal/client.py`
- Logfire Auth: `../logfire/logfire/_internal/auth.py`
- logfire-setup: `./logfire_setup/`

---

## Appendix: File Mapping

| logfire-setup File | logfire File | Changes Needed |
|-------------------|--------------|----------------|
| `logfire_setup/main.py` | `logfire/_internal/cli/init/__init__.py` | Convert main() to parse_init(args), lazy imports, direct calls |
| `logfire_setup/categories.py` | `logfire/_internal/cli/init/categories.py` | Update imports only |
| `logfire_setup/detector.py` | `logfire/_internal/cli/init/detector.py` | Update imports only |
| `logfire_setup/installer.py` | `logfire/_internal/cli/init/installer.py` | Update imports only |
| `logfire_setup/auth_checker.py` | `logfire/_internal/cli/init/auth_checker.py` | Reuse logfire auth module |
| `logfire_setup/mcp_checker.py` | `logfire/_internal/cli/init/mcp_checker.py` | Update imports only |
| `logfire_setup/instructions.py` | `logfire/_internal/cli/init/instructions.py` | Update imports only |
| `logfire_setup/agents_md.py` | `logfire/_internal/cli/init/agents_md.py` | Update imports only |
| `logfire_setup/api_client.py` | ~~Removed~~ | Use LogfireClient.get_user_projects() directly |

---

**Plan Status**: Ready for implementation
**Estimated Completion**: 5 hours
**Risk Level**: Low (isolated changes, optional dependencies)
