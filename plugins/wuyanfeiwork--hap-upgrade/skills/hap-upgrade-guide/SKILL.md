---
name: hap-upgrade-guide
description: "明道云 HAP 私有部署版本升级专属 skill，覆盖两类场景：升级咨询解答、生成升级指南文档。凡涉及 HAP 版本升级的问题或任务，无论是咨询注意事项、了解版本变化，还是生成可执行的升级操作文档，均必须触发本 skill。"
---

# HAP 私有部署升级 Skill

本 skill 覆盖两类场景：

- **场景 A：升级咨询解答** — 用户有升级相关的具体问题需要解答
- **场景 B：生成升级指南** — 用户需要一份完整的可执行升级文档

收到用户请求后，先判断属于哪类场景，再按对应流程处理。两类场景可能在同一对话中切换，保持灵活。

---

## 场景 A：升级咨询解答

### 触发特征

用户提出具体问题，例如：
- "v7.0.0 升级到 v7.2.0 需要注意什么？"
- "能直接跨版本升级吗？"
- "附加操作是什么意思，必须执行吗？"
- "v7.1.0 的镜像命名变更怎么处理？"
- "升级失败了怎么回滚？"
- "这次升级有哪些新功能？"

### 解答流程

**第一步：判断是否需要抓取文档**

- 若问题涉及**具体版本的变更内容、升级步骤、附加操作**，必须先 `web_fetch` 对应版本页再回答，不得凭记忆猜测
- 若问题是**通用升级概念**（如跨版本升级策略、附加操作含义、回滚方法等），可直接基于本 skill 的知识回答

**第二步：抓取所需文档**

先读取 `references/site-structure.md` 确认 URL，再按需抓取：
```
版本发布历史：https://docs-pd.mingdao.com/version
特定版本详情：https://docs-pd.mingdao.com/upgrade/{版本号}/
```

**第三步：组织回答**

- 聚焦用户问题，不要生成完整升级文档
- 涉及代码命令时原文引用，不得改写
- 可选步骤明确说明适用条件
- 回答末尾附上相关官方文档链接
- **重要回答末尾必须附上 AI 声明**（见文末"输出规范"）

### 常见咨询场景回答要点

**关于跨版本升级**
- HAP 支持跨版本直接升级，无需逐版本操作
- 需关注跨越路径中**含附加操作的版本**，这些版本的操作需合并执行
- 不含附加操作的版本只需在备份后升级微服务镜像版本即可

**关于附加操作**
- 分为两类：微服务升级**前**（Pre）和升级**后**（Post）
- Pre 操作示例：镜像命名替换、创建 MongoDB 库、存储组件升级（仅单机）、MongoDB 预置数据更新
- Post 操作示例：进入容器/Pod 执行 MySQL DDL、MongoDB DDL 脚本
- 跨越多版本时，同类操作可合并执行（详见场景 B 合并规则）

**关于版本维护**
- 官方默认维护最新 3 个主版本（第三位为 0 的版本）
- 同一主版本下，建议选择第三位数字最大的修复版本升级

---

## 场景 B：生成升级指南

### Step 1 — 收集前置信息（必须完成，不可跳过）

**必须先向用户确认以下全部信息**，若未主动提供，逐一询问：

| # | 信息项 | 说明 | 是否必须 |
|---|--------|------|----------|
| 1 | **当前版本** | 用户现在运行的版本，如 `v7.0.4` | ✅ 必须 |
| 2 | **目标版本** | 要升级到的版本，如 `v7.2.0` | ✅ 必须 |
| 3 | **部署模式** | `单机模式`（Docker Compose）或 `集群模式`（Kubernetes） | ✅ 必须 |
| 4 | **架构** | `AMD64` 或 `ARM64` | ✅ 必须 |
| 5 | **服务器是否可访问互联网** | 影响镜像拉取方式和预置数据更新命令 | ✅ 必须 |

> ⚠️ 以上 5 项全部确认后，方可进入 Step 2。

**询问话术示例：**
```
在生成升级指南之前，我需要确认以下信息：
1. 您当前运行的版本是？（例如：v7.0.4）
2. 希望升级到哪个目标版本？（例如：v7.2.0）
3. 部署模式是单机模式（Docker Compose）还是集群模式（Kubernetes）？
4. 服务器架构是 AMD64 还是 ARM64？
5. 服务器是否可以访问互联网？
```

### Step 2 — 抓取并分析版本信息

#### 2.1 读取站点结构

先读取 `references/site-structure.md`，获取版本列表页 URL 及各版本升级说明页的 URL 规律。

#### 2.2 获取版本列表

`web_fetch` 抓取：`https://docs-pd.mingdao.com/version`

从中识别：
- 当前版本到目标版本之间**所有被跨过的版本**（不含当前版本，含目标版本），按从旧到新排列
- 每个版本是否**含附加操作**（"含附加操作"列有 √）
- 目标版本是否支持用户所选架构，若不支持则立即告知用户并停止

#### 2.3 抓取含附加操作的版本详情

**只需抓取"含附加操作"的版本**，逐一 `web_fetch`：
```
URL 格式: https://docs-pd.mingdao.com/upgrade/{版本号}/
```

对每个含附加操作的版本，提取并区分 Pre / Post 操作：

**Pre 操作（微服务升级前）常见类型：**
- 镜像命名变更（替换配置文件中的镜像名、服务名）
- 手动创建 MongoDB 数据库（如 `mdwfai`、`mdpayment` 等）
- 存储组件升级（**仅单机模式**，集群模式无此步骤）
- 重新初始化预置文件（使用外部文件对象存储时）
- MongoDB 预置数据更新（标注"可在原版本服务运行状态下执行"）
- 微服务 yaml 配置新增服务（集群模式）

**Post 操作（微服务升级后）常见类型：**
- 进入微服务容器执行 MySQL DDL 脚本（单机）
- 进入 config Pod 执行 MongoDB DDL 脚本（集群）
- 进入 config Pod 执行 MySQL DDL 脚本（集群）
- 进入 config Pod 执行文件初始化命令（集群）

### Step 3 — 合并附加操作（跨版本升级核心）

跨多个含附加操作的版本时，**将所有版本的附加操作合并为一次执行**：

#### Pre 操作合并规则

| 操作类型 | 合并方式 |
|----------|----------|
| **镜像命名变更** | 只需执行一次，在最低含此操作的版本中处理 |
| **创建 MongoDB 数据库** | 合并为一次登录，一次性创建所有需要的库 |
| **存储组件升级（仅单机）** | 直接升级到所有跨越版本中要求的**最高版本** |
| **MongoDB 预置数据更新** | 只执行**目标版本**的，无需执行中间版本 |
| **微服务 yaml 新增服务配置（集群）** | 合并所有版本需新增的服务，一并写入 yaml |

#### Post 操作合并规则

| 操作类型 | 合并方式 |
|----------|----------|
| **进入容器执行 MySQL DDL（单机）** | 一次进入容器，按版本从低到高顺序执行所有版本的 DDL |
| **进入 config Pod 执行脚本（集群）** | 一次进入 Pod，按版本从低到高顺序执行所有版本的命令 |

#### 合并示例

**从 v6.4.0 跨越到 v7.2.0（跨过 v6.5.0、v7.0.0、v7.1.0、v7.2.0，均含附加操作）**

Pre 合并：镜像命名替换执行一次（v7.1.0）、MongoDB 库一次性全部创建、MongoDB 预置数据只更新到 7.2.0、yaml 新增服务合并写入

Post 合并（集群）：一次进入 config Pod，依次执行 v6.5.0 → v7.0.0 → v7.2.0 的所有脚本

### Step 4 — 生成升级指南

根据部署模式，读取对应模板文件的完整内容：

\- **单机模式** → `assets/upgrade-guide-template-standalone.md`

\- **集群模式 → `assets/upgrade-guide-template-cluster.md`

\> 必须先读取模板文件内容，再开始填充生成。不得凭记忆构造文档结构。注意以下关键规则：

#### 关键生成规则

**镜像拉取 / 导入**（根据网络情况）

联网 — 单机 AMD64：
```bash
docker pull registry.cn-hangzhou.aliyuncs.com/mdpublic/mingdaoyun-hap:{目标版本号}
```
联网 — 单机 ARM64：
```bash
docker pull registry.cn-hangzhou.aliyuncs.com/mdpublic/mingdaoyun-hap-arm64:{目标版本号}
```
联网 — 集群（每台微服务节点）：
```bash
crictl pull registry.cn-hangzhou.aliyuncs.com/mdpublic/mingdaoyun-hap:{目标版本号}
```
离线镜像 URL 规律（替换版本号即可获取历史版本）：
```
AMD64: https://pdpublic.mingdao.com/private-deployment/offline/mingdaoyun-hap-linux-amd64-{版本号}.tar.gz
ARM64: https://pdpublic.mingdao.com/private-deployment/offline/mingdaoyun-hap-linux-arm64-{版本号}.tar.gz
```
离线导入 — 单机：`docker load -i mingdaoyun-hap-linux-amd64-{版本号}.tar.gz`
离线导入 — 集群（每台节点）：`gunzip -d xxx.tar.gz && ctr -n k8s.io image import xxx.tar`

**MongoDB 预置数据更新**（只执行目标版本，4 种情况）

单机联网：
```bash
bash -c "$(curl -fsSL https://pdpublic.mingdao.com/private-deployment/data/preset_mongodb_docker.sh)" -s {目标版本号}
```
单机离线：
```bash
wget https://pdpublic.mingdao.com/private-deployment/data/preset_mongodb_docker.sh
wget https://pdpublic.mingdao.com/private-deployment/data/preset_mongodb_{目标版本号}.tar.gz
bash ./preset_mongodb_docker.sh {目标版本号} ./preset_mongodb_{目标版本号}.tar.gz
```
集群联网：
```bash
# default 替换为实际命名空间
bash -c "$(curl -fsSL https://pdpublic.mingdao.com/private-deployment/data/preset_mongodb_k8s.sh)" -s {目标版本号} default
```
集群离线：
```bash
wget https://pdpublic.mingdao.com/private-deployment/data/preset_mongodb_k8s.sh
wget https://pdpublic.mingdao.com/private-deployment/data/preset_mongodb_{目标版本号}.tar.gz
# default 替换为实际命名空间
bash ./preset_mongodb_k8s.sh {目标版本号} default ./preset_mongodb_{目标版本号}.tar.gz
```

**单机微服务升级**：修改 `docker-compose.yaml` 镜像版本号，然后 `bash ./service.sh restartall`

**集群微服务升级**：在控制节点 `/data/mingdao/script/kubernetes` 目录下执行

- 滚动更新（推荐）：`bash update.sh update hap {目标版本号}`
- 非滚动更新（内存不足时）：先 `bash stop.sh`，确认 Pod 消失后再执行 `bash update.sh update hap {目标版本号}`

**单机存储组件升级**（仅单机，集群无此步骤）：
联网 AMD64：`docker pull registry.cn-hangzhou.aliyuncs.com/mdpublic/mingdaoyun-sc:{版本号}`
联网 ARM64：`docker pull registry.cn-hangzhou.aliyuncs.com/mdpublic/mingdaoyun-sc-arm64:{版本号}`
之后修改 `docker-compose.yaml` 中存储组件镜像版本号，然后 `bash ./service.sh restartall`
（注意：若与微服务同时升级，可在最后只执行一次 restartall）

**创建 MongoDB 数据库**（仅开启认证时需要）

> 创建 MongoDB 数据库时，命令规范：在整理出的创建数据库的命令中，仅 `use {库名}` 和 `db: "{库名}"` 按升级实际要求补全。

单机 — 进入存储组件容器操作：
```bash
# 进入存储组件容器
docker exec -it $(docker ps | grep mingdaoyun-sc | awk '{print $1}') bash

# 容器内：使用含 admin 角色的用户登录（替换用户名和密码）
mongo -u 用户名 -p 密码 --authenticationDatabase admin

# 依次创建所有需要的库和对应用户（每个库重复以下两条命令）
use {库名}
db.createUser({ user: "修改成与其他库一致的用户名", pwd: "修改成与其他库一致的密码", roles: [{ role: "readWrite", db: "{库名}" }] })
```

> 在单机部署模式下，系统内置的 MongoDB 存储组件默认不启用身份认证。只有在用户参照 [MongoDB 添加认证](https://docs-pd.mingdao.com/deployment/docker-compose/standalone/strongpwd/mongodb) 文档完成相关配置后，认证功能才会开启。

集群 — 登录到 MongoDB 服务器后操作：

```bash
# 使用含 admin 角色的用户登录 MongoDB（替换连接信息）
mongo -u 用户名 -p 密码 --authenticationDatabase admin

# 依次创建所有需要的库和对应用户（每个库重复以下两条命令）
use {库名}
db.createUser({ user: "修改成与其他库一致的用户名", pwd: "修改成与其他库一致的密码", roles: [{ role: "readWrite", db: "{库名}" }] })
```

#### 其他写作规范

- 所有代码命令**原文保留**，不得改写或简化，**禁止使用“此处省略”、“结构同上”等描述，必须提供完整可运行的代码块**
- 代码块使用 ` ``` bash ` 或 ` ``` yaml ` 包裹
- 有路径占位符或需要用户修改的参数，在代码块上方用 `> 💡` 提示
- 含附加操作的步骤前加 `> ⚠️ **特别注意**` 提示框
- 可选操作（如"如果已开启 MongoDB 认证"）明确标注适用条件，不要删除
- 备份步骤永远放在第一位
- 统一输出为 **Markdown (.md)** 文件，保存后提供用户下载

---

## 输出规范

### AI 声明（所有输出必须附加）

无论是生成的升级指南文档，还是场景 A 中的重要回答，**末尾必须附上以下声明**：

```
---
💡 声明：本文档内容由 AI 生成。尽管已努力确保信息的合理性，但 AI 模型仍可能产生不准确、过时或存在偏差的内容。请在执行关键操作前，务必对照[官方文档](https://docs-pd.mingdao.com)进行核实校验。
```

---

## 注意事项

- 所有命令来自官方文档，禁止自行创作或修改命令逻辑
- 集群模式**没有**存储组件升级步骤，不要在集群模板中生成此步骤
- 网站默认使用中文文档（英文版路径加 `/en/` 前缀）
- 抓取页面时若内容不完整，可重试或尝试抓取英文版对照
- 咨询解答时，若涉及具体版本，务必先抓文档再回答，不得凭记忆猜测
