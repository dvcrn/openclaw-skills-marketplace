---
name: Regex
description: "Write correct, efficient regular expressions across different engines."
---

## Greedy vs Lazy

- `.*` is greedy—matches as much as possible; `.*?` is lazy—matches minimum
- Greedy often overshoots: `<.*>` on `<a>b</a>` matches entire string, not `<a>`
- Default quantifiers `+ * {n,}` are greedy—add `?` for lazy: `+?` `*?` `{n,}?`

## Escaping

- Metacharacters need escape: `\. \* \+ \? \[ \] \( \) \{ \} \| \\ \^ \$`
- Inside character class `[]`: only `]`, `\`, `^`, `-` need escape (and `^` only at start, `-` only mid)
- Literal backslash: `\\` in regex, but in strings often need `\\\\` (double escape)

## Anchors

- `^` start, `$` end—but behavior changes with multiline flag
- Multiline mode: `^` `$` match line starts/ends; without, only string start/end
- `\A` always string start, `\Z` always string end (not all engines)
- Word boundary `\b` matches position, not character—`\bword\b` for whole words

## Character Classes

- `[abc]` matches one of a, b, c; `[^abc]` matches anything except a, b, c
- Ranges: `[a-z]` `[0-9]`—but `[a-Z]` is invalid (ASCII order matters)
- Shorthand: `\d` digit, `\w` word char, `\s` whitespace; uppercase negates: `\D` `\W` `\S`
- `.` matches any char except newline—use `[\s\S]` for truly any, or `s` flag if available

## Groups

- Capturing `()` vs non-capturing `(?:)`—use `(?:)` when you don't need backreference
- Named groups: `(?<name>...)` or `(?P<name>...)` depending on engine
- Backreferences: `\1` `\2` refer to captured groups in same pattern
- Groups also establish scope for alternation: `cat|dog` vs `ca(t|d)og`

## Lookahead & Lookbehind

- Positive lookahead `(?=...)`: assert what follows, don't consume
- Negative lookahead `(?!...)`: assert what doesn't follow
- Positive lookbehind `(?<=...)`: assert what precedes
- Negative lookbehind `(?<!...)`: assert what doesn't precede
- Lookbehinds must be fixed-width in most engines—no `*` or `+` inside

## Flags

- `i` case-insensitive, `m` multiline (^$ match lines), `g` global (find all)
- `s` (dotall): `.` matches newline—not supported everywhere
- `u` unicode: enables `\p{}` properties, proper surrogate handling
- Flags syntax varies: `/pattern/flags` (JS), `(?flags)` inline, or function arg (Python `re.I`)

## Engine Differences

- JavaScript: no lookbehind until ES2018; no `\A` `\Z`; no possessive quantifiers
- Python `re`: uses `(?P<name>)` for named groups; no `\p{}` without `regex` module
- PCRE (PHP, grep -P): full features; possessive `++` `*+`; recursive patterns
- Go: RE2 engine, no backreferences, no lookahead—guaranteed linear time

## Performance

- Catastrophic backtracking: `(a+)+` against `aaaaaaaaaab` is exponential—avoid nested quantifiers
- Possessive quantifiers `++` `*+` prevent backtracking—use when backtracking pointless
- Atomic groups `(?>...)` don't give back chars—similar to possessive
- Anchor patterns when possible—`^prefix` is O(1), unanchored `prefix` is O(n)

## Common Mistakes

- Email validation: RFC-compliant regex is 6000+ chars—use simple check or library
- URL matching: edge cases are endless—use URL parser, regex for quick extraction only
- Don't use regex for HTML/XML—use a parser; regex can't handle nesting
- Forgetting to escape user input—regex injection is real; use literal escaping functions

## Testing

- Test edge cases: empty string, special chars, unicode, very long input
- Visualize with tools: regex101.com shows matches and explains
- Check which engine documentation you're reading—features vary significantly
