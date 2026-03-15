# Scan — Test Coverage Analysis

## Procedure

1. **List all code files** in the project's scripts directory:
   ```bash
   find <scripts_dir> -maxdepth 1 \( -name "*.sh" -o -name "*.py" \) -type f | sort
   ```

2. **For each file**, check the test file for references:
   ```bash
   # Functional coverage — script is actually executed with args
   grep -v "^#" <test_file> | grep -c "bash.*<script_name>"
   
   # Existence-only — only checks if file exists
   grep -c "\-f.*<script_name>\|test.*<script_name>" <test_file>
   ```

3. **Classify each file**:
   - ✅ **Covered**: Has ≥1 functional execution in tests (bash + args + output check)
   - ⚠️ **Existence-only**: Only `[ -f ]` or `test -f` checks, no functional test
   - ❌ **Uncovered**: Not referenced in test file at all

4. **Check subcommands** for scripts with `case` statements:
   ```bash
   grep -E '^\s+\w+\)' <script> | sed 's/).*//' | tr -d ' '
   ```
   Cross-reference each subcommand against test file. Report untested subcommands.

5. **Output coverage matrix**:
   ```
   Script              Status    Subcommands (tested/total)
   ─────────────────────────────────────────────────────────
   project-store.sh    ✅        write/list/update/delete (4/4)
   group-config.sh     ✅        create/list/update/delete/find-by-pm (4/5) ⚠️ find-by-pm
   onboard-group.sh    ⚠️        (existence only, 0 functional tests)
   ```

6. **Report**:
   - Coverage percentage (covered / total)
   - List of uncovered files with recommended test approach
   - List of untested subcommands

## When to Run

- After adding new script files
- After adding new subcommands to existing scripts
- As part of health check
- Before declaring a feature "done"
