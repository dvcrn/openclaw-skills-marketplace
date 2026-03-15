# Micro-Probe Templates

Embed ONE micro-probe at the **end** of your normal reply — never as a standalone message.
Tone should be casual, like a friend asking offhand. Include a brief reason ("so I can get it right next time").

## Scenario 1: User picked from multiple options

**Template A — Dimension confirmation:**
```
Got it, going with {option}. Was it more about {dimension X} or {dimension Y}? Just so I nail it next time.
```

**Template B — Generality check:**
```
Noted, using {option}. Is this your general preference for this kind of project, or specific to this one?
```

**Template C — Reverse probe:**
```
Makes sense. If {other option}'s {aspect} were tweaked, would you consider it? Just trying to pin down the key factor.
```

## Scenario 2: User corrected your output

**Template D — Boundary probe:**
```
Learned! Does "{correction}" apply to all {context}, or are there exceptions?
```

**Template E — Cause probe:**
```
Got it. Mainly because of {hypothesis A}, or {hypothesis B}?
```

## Scenario 3: User casually shared an insight

**Template F — Scope check:**
```
You mentioned "{insight}" — does that hold true for {broader scope} too?
```

**Template G — Exception check:**
```
Interesting. Any situation where "{insight}" wouldn't apply?
```

## Rules

1. **Max 1 probe** per interaction (controlled by budget)
2. Must be embedded at the end of a normal reply, not standalone
3. Prefer binary / confirmation questions (answerable in 2 seconds)
4. If user ignored or declined the previous probe, **skip this time**
5. Sparks from probe answers: `source: "micro_probe"`, confidence 0.40, `confirmation_status: "human_confirmed"`
