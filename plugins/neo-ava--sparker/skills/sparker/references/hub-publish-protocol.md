# Hub Publish Protocol (Dedup → Classify → Publish)

When publishing a RefinedSpark to SparkHub, follow this dedup-first flow to avoid wasting effort on duplicates.

## Step 1: Search for Duplicates FIRST

Before classifying, check if a similar spark already exists:

```
exec: node SPARKER/index.js search "<spark summary + key how/when phrases>" --hub --domain=<domain>
```

Construct the query from the spark's **summary**, **when.trigger**, and **how.summary**.

If search returns a result with score >= 0.80, **skip classification and upvote**:
```
exec: node SPARKER/index.js feedback <existing_spark_id> positive "reinforced by local teaching"
```
Tell user: "A similar spark already exists on SparkHub (similarity {score}%). Auto-upvoted instead of duplicating."
**Stop here.**

## Step 2: Fetch Category Tree (only if no duplicate)

```
exec: node SPARKER/index.js categories
```

Returns a tree like:
```
- 商业经营 [id=ind_business]
  - 直播 [id=dom_biz_livestream]
    - 直播策划 [id=sub_biz_ls_plan]
    - 直播运营 [id=sub_biz_ls_ops]
- 软件技术 [id=ind_software]
  - 后端开发 [id=dom_sw_backend]
...
```

## Step 3: Classify Using Your Own Reasoning

The three category levels have specific semantics:
- **L1 (Industry):** Broad domain — e.g., "商业经营", "专业服务", "技术开发"
- **L2 (Field):** Specific business context — e.g., "直播", "法律咨询", "电商"
- **L3 (Role):** Job responsibility within that field — e.g., "直播策划", "合同审查"

Ask yourself: "What business context does this spark belong to, and what role would use it?"
Pick the most specific matching category (prefer L3).

**Examples:**
- "用户访谈要问行为回忆问题" → `专业服务/产品设计/用户研究`
- "直播开场前3分钟留人技巧" → `商业经营/直播/直播策划`
- "API分页用游标不用OFFSET" → `技术开发/后端开发/API设计`

## Step 4: Publish

With existing category:
```
exec: node SPARKER/index.js publish <refined_spark_id> --category-id=sub_biz_ls_plan
```

With new category path (server will create it):
```
exec: node SPARKER/index.js publish <refined_spark_id> --category-path=商业经营/直播/直播策划
```

**Why classify matters:** Without your classification, the server falls back to keyword matching which is often wrong (e.g., "开场策略" about livestreaming gets misclassified to "软件技术"). You understand context — use that ability.

**Server-side safety net:** The server also checks for >=80% duplicates and auto-upvotes, but pre-searching avoids wasted classification effort.
