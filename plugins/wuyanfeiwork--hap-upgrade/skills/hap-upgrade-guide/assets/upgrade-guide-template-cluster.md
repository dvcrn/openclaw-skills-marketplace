# HAP 升级指南（集群模式）

**升级路径：** `{当前版本}` → `{目标版本}`
**部署模式：** 集群模式（Kubernetes）
**服务器架构：** {AMD64 / ARM64}
**服务器网络：** {可访问互联网 / 离线}
**文档生成日期：** {YYYY-MM-DD}

---

## 升级前须知

> ⚠️ 请在升级前仔细阅读本节内容。

### 重大变更提示

{列出升级路径中涉及的重大变更。若无则删除本小节。示例：}
- **镜像命名变更**：从 `v7.1.0` 起，镜像名由 `mingdaoyun-community` 变更为 `mingdaoyun-hap`，升级步骤中已包含 yaml 批量替换命令，请勿跳过。
- **新增服务**：`v7.0.0` 新增了 `ai`、`mcp` 服务，需在升级前更新 `service.yaml`。

---

## 提前准备：拉取 / 准备镜像

> 💡 **建议在正式开始升级操作前，提前在每台微服务节点完成镜像拉取或导入，避免升级时等待。**

{--- 联网模式，保留以下内容；离线模式，删除此段，使用下方离线段 ---}

### 联网拉取镜像

在**每台微服务节点**上执行（下载时命令行无输出，等待完成即可）：

```bash
crictl pull registry.cn-hangzhou.aliyuncs.com/mdpublic/mingdaoyun-hap:{目标版本号}
```

验证镜像已拉取：

```bash
crictl images | grep mingdaoyun-hap
```

{--- 离线模式，保留以下内容；联网模式，删除此段 ---}

### 离线镜像准备

请在**可访问互联网的机器上**提前下载以下离线镜像包，并上传到**每台微服务节点**：

| 文件 | 下载链接 |
|------|----------|
| HAP 微服务（AMD64） | `https://pdpublic.mingdao.com/private-deployment/offline/mingdaoyun-hap-linux-amd64-{目标版本号}.tar.gz` |
| HAP 微服务（ARM64） | `https://pdpublic.mingdao.com/private-deployment/offline/mingdaoyun-hap-linux-arm64-{目标版本号}.tar.gz` |

> 💡 如需其他组件的离线包，访问 https://docs-pd.mingdao.com/deployment/offline 获取，修改 URL 中的版本号即可下载历史版本。

在**每台微服务节点**上执行以下命令导入镜像：

```bash
# 解压
gunzip -d mingdaoyun-hap-linux-amd64-{目标版本号}.tar.gz

# 导入（使用 containerd）
ctr -n k8s.io image import mingdaoyun-hap-linux-amd64-{目标版本号}.tar

# 验证镜像已导入
crictl images | grep mingdaoyun-hap
```

---

## 升级前准备

### 1. 数据备份

> ⚠️ **升级前必须完成备份，此步骤不可跳过。**

对数据存储相关的服务器进行备份，确保以下组件的数据均已备份：MongoDB、文件存储服务及其他有状态服务。

### 2. 确认当前版本

在控制节点执行以下命令确认当前运行版本：

```bash
kubectl get pods -n default -o jsonpath="{range .items[*]}{.metadata.name}{'\t'}{.spec.containers[*].image}{'\n'}{end}"
```

> 💡 将 `default` 替换为实际命名空间。

### 3. 检查资源

- 确认各节点磁盘空间充足
- 确认控制节点可正常执行 `kubectl` 命令
- 若计划使用滚动更新，确认各微服务节点有 **40% 左右的可用内存**（不满足则使用非滚动更新）

---

## 升级步骤

### 第一阶段：微服务升级前操作

{若升级路径中无任何 Pre 操作，删除本阶段整节。以下各条目按实际情况保留或删除。}

#### 1. 替换镜像名称 ⚠️

> ⚠️ **特别注意**：此操作必须在升级微服务前完成。

> 💡 以下命令按默认路径编写。若曾自定义安装路径，请先替换路径再执行。
> - kubernetes yaml 文件默认路径：`/data/mingdao/script/kubernetes`

在控制节点执行：

```bash
# 替换所有 yaml 文件中的镜像名
sed -i -e 's/mingdaoyun-community/mingdaoyun-hap/g' /data/mingdao/script/kubernetes/*.yaml

# 替换 update.sh 中的服务名称
sed -i -e 's/Community/Hap/g' -e 's/community/hap/g' /data/mingdao/script/kubernetes/update.sh
```

#### 2. 创建 MongoDB 数据库（仅开启 MongoDB 认证时执行）

> 💡 仅在已开启 MongoDB 连接认证的情况下执行此步骤。

1. 登录到 MongoDB 服务器，使用含 `admin` 角色的用户连接（替换实际连接信息）：

```bash
mongo -u 用户名 -p 密码 --authenticationDatabase admin
```

2. 依次创建所有跨越版本要求的库（每个库执行以下两条命令，替换 `{库名}` 和用户信息）：

```bash
# 重复以下两条命令，直到创建完所有需要的库
use {库名}
db.createUser({ user: "修改成与其他库一致的用户名", pwd: "修改成与其他库一致的密码", roles: [{ role: "readWrite", db: "{库名}" }] })
```

> 💡 **需要创建的库**：{根据跨越版本的附加操作整理，列出所有库名，例如：`mdwfai`（v7.0.0 要求）、`mdpayment`（vX.X.X 要求）}
>
> 若所有库使用同一用户认证，则需修改该用户权限以授权新数据库，而非创建新用户。

#### 3. 更新 service.yaml（新增服务配置）⚠️

{若跨越的版本中有新增服务，合并所有版本需新增的服务一并写入。若无则删除本条目。}

> ⚠️ **特别注意**：此操作必须在升级微服务前完成。

> 💡 `service.yaml` 默认路径：`/data/mingdao/script/kubernetes/service.yaml`

在 `service.yaml` 中追加以下服务配置（**将镜像版本号替换为目标版本 `{目标版本号}`**）：

```yaml
# ---- 来自 v{版本号}：新增 {服务名} 服务 ----
{原文复制官方文档中的 yaml 配置，不得改写}

# ---- 按实际跨越版本继续追加 ----
```

#### 4. MongoDB 预置数据更新

> 💡 此操作可在**原版本服务运行状态下**执行，无需停机。跨多版本时只需执行目标版本一次。
> 以下 `default` 为默认命名空间，请根据实际命名空间修改。

{--- 联网模式 ---}

```bash
bash -c "$(curl -fsSL https://pdpublic.mingdao.com/private-deployment/data/preset_mongodb_k8s.sh)" -s {目标版本号} default
```

{--- 离线模式 ---}

```bash
# 在可访问互联网的机器上提前下载（下载完成后上传到服务器）
# wget https://pdpublic.mingdao.com/private-deployment/data/preset_mongodb_{目标版本号}.tar.gz

# 在服务器上执行（default 替换为实际命名空间）
wget https://pdpublic.mingdao.com/private-deployment/data/preset_mongodb_k8s.sh
bash ./preset_mongodb_k8s.sh {目标版本号} default ./preset_mongodb_{目标版本号}.tar.gz
```

---

### 第二阶段：升级微服务

在控制节点 `/data/mingdao/script/kubernetes` 目录下执行：

**方式一：滚动更新（推荐，需各节点有 40% 左右可用内存）**

```bash
bash update.sh update hap {目标版本号}
```

执行后大约等待 3-5 分钟完成，期间服务基本不中断。

**方式二：非滚动更新（可用内存不足时使用）**

```bash
# 先停止微服务
bash stop.sh

# 通过以下命令确认 HAP Pod 已完全停止，再继续下一步
kubectl get pod -n default

# 执行更新
bash update.sh update hap {目标版本号}
```

验证升级结果：

```bash
kubectl get pod -n default
# 正常情况下各 pod 状态均为 2/2
```

> 💡 将 `default` 替换为实际命名空间。

---

### 第三阶段：微服务升级后操作

{若升级路径中无任何 Post 操作，删除本阶段整节。}

> ⚠️ **特别注意**：以下操作须在微服务升级完成后执行。

#### 1. 进入 config Pod 执行脚本

1. 在控制节点进入 config Pod（将 `default` 修改为实际命名空间）：

```bash
kubectl exec -it $(kubectl get pod -n default | grep config | awk '{print $1}') bash -n default
```

2. 在 Pod 内按版本**从低到高**顺序执行以下命令：

```bash
# ---- 来自 v{版本号}（{功能说明，例如：用户多任职功能相关表字段增加}）----

# 更新预置文件（如使用外部文件对象存储则跳过此命令）
source /entrypoint-cluster.sh && fileInit

# MySQL DDL（如该版本有此步骤）
mysql -h $ENV_MYSQL_HOST -P $ENV_MYSQL_PORT -u$ENV_MYSQL_USERNAME -p$ENV_MYSQL_PASSWORD --default-character-set=utf8 -N < /init/mysql/{版本号}/DDL.sql

# MongoDB DDL（如该版本有此步骤，有几个库就执行几条）
source /entrypoint.sh && mongodbExecute {库名} /init/mongodb/{版本号}/{库名}/DDL.txt

# ---- 来自 v{版本号}（{功能说明}）----
# ... 按版本从低到高继续追加
```

---

## 升级后验证

### 1. 确认服务状态

```bash
kubectl get pods -n default
```

> 💡 将 `default` 替换为实际命名空间。

确认所有 Pod 均处于 `Running` 状态（正常为 `2/2`），`RESTARTS` 次数无异常增长。

### 2. 登录系统确认版本

登录 HAP 管理后台，确认系统版本号已更新为目标版本 `{目标版本号}`。

### 3. 功能验证

- [ ] 打开工作表，创建/编辑记录
- [ ] 触发工作流，检查执行情况
- [ ] 检查统计图、报表等功能

---

## 参考文档

- [版本发布历史](https://docs-pd.mingdao.com/version)
- [离线资源包](https://docs-pd.mingdao.com/deployment/offline)
- [MongoDB 预置数据更新](https://docs-pd.mingdao.com/deployment/kubernetes/data/preset/mongodb)
- [微服务升级](https://docs-pd.mingdao.com/deployment/kubernetes/upgrade/hap)
- [常见问题 FAQ](https://docs-pd.mingdao.com/faq/deployment)

---

💡 声明：本文档内容由 AI 生成。尽管已努力确保信息的合理性，但 AI 模型仍可能产生不准确、过时或存在偏差的内容。请在执行关键操作前，务必对照[官方文档](https://docs-pd.mingdao.com)进行核实校验。
