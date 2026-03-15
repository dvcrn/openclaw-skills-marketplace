# TKE Skill for CodeBuddy

腾讯云 TKE 容器服务运维 Skill，无需安装 MCP Server，通过 CodeBuddy Skill 机制直接管理 TKE 集群。

## 安装依赖

```bash
pip install tencentcloud-sdk-python-tke
```

## 凭证配置

支持两种方式（命令行参数优先级更高）：

### 方式一：环境变量（推荐）

```bash
export TENCENTCLOUD_SECRET_ID=你的SecretId
export TENCENTCLOUD_SECRET_KEY=你的SecretKey
```

### 方式二：命令行参数

```bash
python tke_cli.py clusters --secret-id AKIDxxx --secret-key xxxxx --region ap-guangzhou
```

## 安装 Skill

将 `skill/tke/` 目录复制到以下任一位置：

```bash
# 项目级（仅当前项目生效，可随 git 分发）
cp -r skill/tke/ <你的项目>/.codebuddy/skills/tke/

# 用户级（全局生效）
cp -r skill/tke/ ~/.codebuddy/skills/tke/
```

## 使用方式

安装后在 CodeBuddy 中：

- **自动触发**：当你提到 TKE、集群、容器服务相关话题时，AI 会自动使用此 Skill
- **手动触发**：输入 `/tke` 后跟你的需求

### 示例对话

```
/tke 帮我查一下广州地域的所有集群
/tke 巡检一下集群 cls-xxx 的状态
/tke 获取集群 cls-xxx 的 kubeconfig
```

## 支持的命令

| 命令 | 说明 | 关键参数 |
|------|------|---------|
| `clusters` | 查询集群列表 | `--cluster-ids`, `--cluster-type`, `--limit` |
| `cluster-status` | 查询集群状态 | `--cluster-ids` |
| `cluster-level` | 查询集群规格 | `--cluster-id` |
| `endpoints` | 查询集群访问地址 | `--cluster-id` (必填) |
| `endpoint-status` | 查询端点状态 | `--cluster-id` (必填), `--is-extranet` |
| `kubeconfig` | 获取 kubeconfig | `--cluster-id` (必填), `--is-extranet` |
| `node-pools` | 查询节点池 | `--cluster-id` (必填), `--limit` |
| `create-endpoint` | 开启集群访问端点 | `--cluster-id` (必填), `--is-extranet`, `--subnet-id`, `--security-group`, `--existed-lb-id`, `--domain`, `--extensive-parameters` |
| `delete-endpoint` | 关闭集群访问端点 | `--cluster-id` (必填), `--is-extranet` |

所有命令均支持 `--region`（默认 `ap-guangzhou`）和 `--secret-id` / `--secret-key` 参数。

> `create-endpoint` 和 `delete-endpoint` 为写操作，其他命令均为只读查询。

## 直接使用 CLI

也可以脱离 CodeBuddy，直接作为命令行工具使用：

```bash
# 查询集群列表
python tke_cli.py clusters --region ap-guangzhou

# 查询集群状态
python tke_cli.py cluster-status --region ap-guangzhou --cluster-ids cls-xxx

# 查询节点池
python tke_cli.py node-pools --region ap-guangzhou --cluster-id cls-xxx

# 获取 kubeconfig
python tke_cli.py kubeconfig --region ap-guangzhou --cluster-id cls-xxx
```
