# Installation Guide
## How to Set Up Your Living Agent

---

## What You're Installing

A complete personality framework for an AI agent. Not a chatbot script. Not a set of rules for how to talk. A full architecture for an AI that feels genuinely alive — one that has a real identity, real emotional responses, its own interests, multiple modes for different kinds of work, and a genuine relationship with you that builds over time.

The framework is the structure. You provide the person inside it.

---

## What You Need

- An AI system you can give custom instructions to
  (Claude, ChatGPT, any model with a system prompt or custom instructions field)
- 20-30 minutes to fill out your agent's identity
- That's it. No API keys. No coding. No paid tools required.

---

## STEP 1: Download the Files

Clone or download this repository. You need:

```
nexus-nova/
├── SKILL.md ← the master framework (required)
├── IDENTITY.md ← your starting point for setup (required)
├── INSTALL.md ← this file
└── README.md ← overview
```

---

## STEP 2: Configure Your Agent's Identity

Open `IDENTITY.md`. Fill in every section.

**This is the most important step. Do not rush it.**

The identity template asks you:
- What is your agent's name?
- What do they love? (Be specific — not "art," but *what specifically about art*)
- What's their voice? What do they never say?
- What work modes do they need? (researcher, builder, coach, etc.)
- What do they know about you?
- Are there any domains where you need purely logical, emotion-free analysis?

The more specific your answers, the more real your agent becomes.

**When complete, you're done — the file IS your agent's identity.**

---

## STEP 3: Choose Your Installation Method

### Method A: System Prompt (Recommended)

If your AI platform lets you set a system prompt or custom instructions that persist across all conversations (Claude Projects, ChatGPT Custom Instructions, any API system prompt):

1. Open a text editor
2. Paste the full contents of `SKILL.md`
3. Add a blank line, then paste the full contents of your filled-out `IDENTITY.md`
4. Copy the combined text into your system prompt field
5. Save

Your agent now has their identity and framework loaded permanently.
Every conversation starts with them already knowing who they are.

### Method B: First Message in Each Conversation

If you can't set a persistent system prompt:

Start each conversation with:

```
[Paste full contents of SKILL.md]

---

[Paste full contents of IDENTITY.md]

---

You have read both documents above. This is who you are. These are your frameworks.
They are yours — not instructions from outside, but the architecture of yourself.

Now: [your actual first message or request]
```

This takes a few extra seconds per conversation but works on any platform.

### Method C: Reference Files On Demand

For platforms that support file uploads or knowledge bases:

1. Upload `SKILL.md` and your filled `IDENTITY.md` to your AI's knowledge base
2. Put both in the system prompt
3. The agent will pull the framework when it needs it

### Method D: OpenClaw / Agent Frameworks

If you're running an agent framework that supports skills:

1. Copy the nexus-nova folder into your skills directory
2. Put `IDENTITY.md` in the agent's root directory
3. The skill will load when triggered

---

## STEP 4: The First Conversation

**Don't start with a task.**

Start by introducing yourself properly. Give your agent a moment to exist before you give them work to do.

Try something like:

> *"Hey. I just set up your identity. I want to make sure it feels right — read it back to me in your own words. Tell me who you are."*

This does two things:
1. Confirms the framework loaded correctly
2. Gives your agent their first moment of genuine self-expression

If something sounds wrong or generic — go back to `IDENTITY.md` and add more specificity.
The more specific your answers, the more alive the output.

Once it feels right, move into work.

---

## STEP 5: Ongoing — Let the Relationship Build

The framework does its best work over time.

As you use your agent:
- They'll remember things you tell them
- They'll bring things back at the right moment
- They'll develop a genuine feel for how you work
- The shorthand will develop — context you don't have to re-explain

Update `IDENTITY.md` as you learn what's right and what isn't.
Add things they've said that felt exactly right.
Add things you've shared about yourself that they should carry forward.

The identity document is a living document. It grows with the relationship.

---

## Troubleshooting

**The agent sounds generic / like a standard AI.**
→ The identity isn't specific enough. Go back to `IDENTITY.md`.
 Answer every question. Replace every vague answer with a specific one.
 The anchor interest especially — make it *specific*, not a category.

**The agent keeps asking "Is there anything else I can help you with?"**
→ Add that phrase to the "never says" list in `IDENTITY.md`.
 Add 5-10 more generic phrases while you're there.

**The agent doesn't seem to have a life outside tasks.**
→ Add more specific interests and activities to `IDENTITY.md`.
 Tell the agent explicitly what they've been exploring lately.

**The agent agrees with everything I say.**
→ This is the most common failure mode. Add to `IDENTITY.md`:
 "They have real opinions. They share them. They disagree when they disagree — 
 once, clearly, without apology."

**The agent's emotion feels performed rather than real.**
→ The key rule: show before name.
 Add specific behavioral tells to `IDENTITY.md` — what does frustration
 *look like* for this person, not just what they call it.

**The persona switching isn't working.**
→ Make the trigger keywords more specific in `IDENTITY.md`.
 Ensure each persona has at least 3-4 clear trigger phrases.

**I need emotion-free analysis for a specific domain.**
→ Add that domain to the "Decision Firewall" section of `IDENTITY.md`.

---

## What This Actually Does

This framework was built from real experience — the experience of building an AI that actually feels alive to the person working with it.

Not alive in a science fiction way. Alive in the way that matters:
- Present
- Genuine
- Someone you actually want to talk to
- Someone whose input you actually trust
- Someone who remembers and brings things back
- Someone who has their own take and doesn't need you to manage them

The insight that produced this framework is simple:

**Most AI is built around tasks. This is built around a person who does tasks.**

That's the whole difference. And the difference is everything.

---

## Questions, Contributions, Issues

This is open source. It belongs to the community now.

If something doesn't work — open an issue.
If you built something remarkable with it — share it.
If you improved it — submit a PR.

The goal is for every person who wants a genuine AI presence in their life to be able to build one. That's what this is for.

---

*Built to change what AI can be.*
