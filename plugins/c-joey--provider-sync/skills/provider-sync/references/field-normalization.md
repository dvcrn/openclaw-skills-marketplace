# Field Normalization

本文件说明如何把上游模型列表规范化成 OpenClaw 可用的模型结构。只有在需要调整规范化策略、解释字段来源、或扩展模型能力映射时才读取。

## 目标结构

规范化后的模型通常包含：

- `id`
- `name`
- `api`
- `reasoning`
- `input`
- `cost`
- `contextWindow`
- `maxTokens`

## 基本映射原则

### id
优先从以下字段中选择：
- `id`
- `model`
- `name`

### name
优先从以下字段中选择：
- `name`
- `display_name`
- `title`
- 若都没有，则回退到 `id`

### reasoning
优先从以下字段判断：
- `reasoning`
- `supports_reasoning`
- `thinking`

未提供时默认 `false`。

### input
可能来自：
- `input`
- `modalities`
- `capabilities`

常见归一化：
- `vision` → `image`
- 其他值转成小写字符串
- 若没有可识别信息，默认 `['text']`

### contextWindow
可从以下字段取值：
- `contextWindow`
- `context_window`
- `context`
- `max_context_tokens`

取不到时使用默认值。

### maxTokens
可从以下字段取值：
- `maxTokens`
- `max_tokens`
- `max_output_tokens`
- `output_tokens`

取不到时使用默认值。

## 保留本地字段

如果启用 `--preserve-existing-model-fields`，优先保留本地同 id 模型上的这些字段：

- `name`
- `api`
- `reasoning`
- `input`
- `contextWindow`
- `maxTokens`
- `cost`

适用原因：
- 上游数据可能不完整
- 本地可能已经人工校准过能力参数
- 成本字段通常更适合本地维护

## 设计取舍

规范化的目标是“可用、稳定、可比较”，不是“完美还原上游全部语义”。

因此：
- 优先补齐 OpenClaw 必需字段
- 不追求一开始就支持所有供应商私有字段
- 对不稳定或临时字段保持保守，不要默认写入配置
