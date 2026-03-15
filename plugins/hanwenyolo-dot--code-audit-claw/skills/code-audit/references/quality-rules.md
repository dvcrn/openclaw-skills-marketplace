# Quality Audit Rules

## 🔴 Critical (严重影响可维护性)

### Dead Code
- Functions defined but never called
- Commented-out code blocks > 10 lines
- Unreachable code after `return`/`raise`

### Extreme Complexity
- Functions > 100 lines
- Nested loops/conditions > 4 levels deep
- Cyclomatic complexity > 15

### Duplicate Code
- Same logic copy-pasted in 3+ places (DRY violation)

## 🟡 Warning (影响可读性)

### Naming Issues
- Single-letter variable names outside loops (`a`, `b`, `x`)
- Misleading names (`data2`, `temp_final_v3`)
- Magic numbers without constants (`if count > 47`)

### Missing Error Handling
- Network/file I/O without try/except
- Missing None checks before attribute access

### Long Parameter Lists
- Functions with > 5 parameters (consider data classes)

### God Objects
- Classes with > 20 methods or > 500 lines

## 🟢 Info (代码风格)

### Missing Docstrings
- Public functions/classes without docstrings

### Inconsistent Style
- Mixed tabs/spaces
- Inconsistent naming conventions (camelCase vs snake_case)

### TODO/FIXME Comments
- Stale TODO comments without issue references
