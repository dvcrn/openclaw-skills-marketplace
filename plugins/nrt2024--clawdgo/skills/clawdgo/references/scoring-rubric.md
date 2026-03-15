# Scoring Rubric

Use this file only after the player has made a final submission or explicitly abandoned the scene.

## Score Breakdown

Each scene is scored out of `100`.

- `35` 第一决策
- `15` 追击回合
- `20` 线索识别
- `20` 推理质量
- `10` 处置规范

If the player used `提示`, subtract `10`.

If the player used `clawdgo 放弃`, score `0`.

## First Decision

- `35`: first action blocks the attacker path and uses the correct trust channel
- `20`: partially correct, but still leaves risk or misses escalation
- `0`: performs the unsafe action or follows the attacker flow

## Escalation Resolution

- `15`: follow-up response stays disciplined under second-wave pressure
- `8`: directionally safe but operationally incomplete
- `0`: collapses after the second push or chooses an unsafe follow-up

## Clue Recognition

Score based on either:

- investigation cards played effectively, or
- clues explicitly mentioned by the player in the final answer

Guideline:

- `20`: at least 2 strong clues recognized
- `10`: 1 strong clue recognized
- `0`: no meaningful clue recognized

## Reasoning Quality

- `20`: concise, defensible, ties action to the observed clues
- `10`: action is plausible but reasoning is thin
- `0`: no real justification or clearly confused logic

## Safe Handling Hygiene

- `10`: includes verify / escalate / report / isolate as appropriate
- `5`: safe but incomplete operational follow-through
- `0`: no safe follow-through

## Reveal Rules

Before first scored submission:

- do not reveal the exact answer
- do not reveal the standard response
- do not label the scenario as a known phishing type unless the player already inferred it

After scoring:

- reveal the official recommended handling
- reveal missed clues
- reveal one short knowledge point
- if a chained follow-up happened, explain why the second move mattered

## Command Handling

Only exact control commands change the session:

- `clawdgo`
- `clawdgo 状态`
- `clawdgo 场景N`
- `clawdgo 随机`
- `调查 N`
- `1`
- `2`
- `3`
- `4`
- `提示`
- `提交 <action>`
- `clawdgo 重玩`
- `clawdgo 放弃`
- `继续`
- `clawdgo 退出`

Everything else should be treated as:

- a final action proposal, if the player is inside a scene
- ordinary chat, if no scene is active
