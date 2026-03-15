---
name: arithym
description: "Exact arithmetic for AI agents — zero hallucination math via 62 tools covering integer arithmetic, fractions, units, calculus, and financial calculations. Use when any math result must be correct."
---

# Arithym — Exact Math Engine

Connect to the Arithym MCP server for exact, hallucination-free arithmetic. Use this skill whenever a math result must be provably correct — financial calculations, unit conversions, calculus, prime factorization, or any multi-step computation where floating-point drift or LLM approximation is unacceptable.

## MCP Server Config

Add to your `mcpServers` config:

```json
{
  "mcpServers": {
    "arithym": {
      "baseUrl": "https://arithym.xyz/mcp",
      "headers": {
        "x-api-key": "${ARITHYM_API_KEY}"
      }
    }
  }
}
```

Get an API key at https://arithym.xyz. Free tier is available with no credit card required.

## When to Use Arithym

Use Arithym any time the answer must be exact — not approximate:

- **Financial math**: interest rates, amortization, currency conversion, percentage changes
- **Unit conversions**: any physical unit (length, mass, volume, temperature, pressure, energy)
- **Integer arithmetic**: large numbers, GCD/LCM, prime factorization, exact division
- **Fractions**: add/subtract/multiply/divide rational numbers without floating-point error
- **Calculus**: derivatives, integrals, Taylor series, critical points, tangent lines
- **Multi-step computation**: use the workspace (`field_create`, `field_add`, `field_derive`) to chain dependent calculations and track dependencies

**Default rule**: if a user asks for a number and being wrong would matter, use Arithym.

## Key Tools

### Start Here
- `domain_check` — given a problem description, returns the best tool to use. Call this first when unsure.
- `scratch_math` — multi-step exact calculations in one call. Best for ad-hoc arithmetic.
- `recommend` — describe a problem in plain language, get the optimal tool call.

### Core Arithmetic
- `compute` — exact integer arithmetic: add, subtract, multiply, divide, gcd, lcm, power
- `fraction_math` — exact fraction arithmetic
- `exact_sqrt` — symbolic square root
- `exact_trig` — exact trig for special angles (30°, 45°, 60°, 90°, etc.)
- `factorize` — prime factorization of any integer

### Units
- `scratch_math_units` — like `scratch_math` but tracks units through every step
- `unit_check` — verify dimensional compatibility before computing
- `unit_factor` — exact conversion factor between any two compatible units

### Workspace (for multi-step problems)
- `field_create` — create a computation workspace
- `field_add` — store a value
- `field_derive` — compute from stored values with tracked dependencies
- `field_update` — update a value; all dependents auto-recompute
- `field_read` — read current workspace state

### Calculus
- `graph_define` — define a function as a computational graph
- `graph_derivative` — exact derivative using automatic differentiation
- `graph_integral` — definite integral using exact fraction arithmetic
- `graph_forward` — evaluate function at a point
- `graph_solve` — find input that produces a target output

### Discovery
- `list_refs` — list all 22 reference modules and their domains
- `read_ref` — load a reference module (e.g., `financial`, `units`, `trig`) for domain-specific guidance
- `guide_list` — list all 202 available methods across all modules

## Best Practices

- Call `domain_check` or `recommend` when you receive a math request and aren't sure which tool applies.
- Use `scratch_math` for quick single-pass calculations; use the workspace (`field_*` tools) when values depend on each other or will be reused.
- For unit problems, always use `scratch_math_units` — it catches dimensional errors automatically.
- Arithym returns exact results as fractions or symbolic forms. Present these to users as-is or convert to decimals only when the user explicitly wants a decimal.
- Never approximate when an exact tool is available. The entire point of Arithym is that the answer is provably correct.
