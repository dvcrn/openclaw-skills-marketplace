# HAP 升级指南（单机模式）

**升级路径：** `{当前版本}` → `{目标版本}`
**部署模式：** 单机模式（Docker Compose）
**服务器架构：** {AMD64 / ARM64}
**服务器网络：** {可访问互联网 / 离线}
**文档生成日期：** {YYYY-MM-DD}

---

## 升级前须知

> ⚠️ 请在升级前仔细阅读本节内容。

### 重大变更提示

{列出升级路径中涉及的重大变更。若无则删除本小节。示例：}
- **镜像命名变更**：从 `v7.1.0` 起，镜像名由 `mingdaoyun-community` 变更为 `mingdaoyun-hap`，升级步骤中已包含替换命令，请勿跳过。

---

## 提前准备：拉取 / 准备镜像

> 💡 **建议在正式开始升级操作前，提前完成镜像的拉取或导入，避免升级过程中长时间等待。**

{--- 联网模式，保留以下内容；离线模式，删除此段，使用下方离线段 ---}

### 联网拉取镜像

{--- 下载升级所需所有镜像 ---}

在服务器上执行以下命令提前拉取目标版本镜像：

```bash
# 微服务镜像 AMD64
docker pull registry.cn-hangzhou.aliyuncs.com/mdpublic/mingdaoyun-hap:{目标版本号}

# 微服务镜像 ARM64（如为 ARM64 架构，使用此命令替代上方）
# docker pull registry.cn-hangzhou.aliyuncs.com/mdpublic/mingdaoyun-hap-arm64:{目标版本号}

# 存储组件镜像 AMD64
docker pull registry.cn-hangzhou.aliyuncs.com/mdpublic/mingdaoyun-sc:{目标存储组件版本号}

# 存储组件镜像 ARM64（如为 ARM64 架构，使用此命令替代上方）
# docker pull registry.cn-hangzhou.aliyuncs.com/mdpublic/mingdaoyun-sc-arm64:{目标存储组件版本号}
```

{--- 离线模式，保留以下内容；联网模式，删除此段 ---}

### 离线镜像准备

{--- 导入升级所需所有离线镜像 ---}

请在**可访问互联网的机器上**提前下载以下离线镜像包，并上传到服务器：

| 文件 | 下载链接 |
|------|----------|
| HAP 微服务（AMD64） | `https://pdpublic.mingdao.com/private-deployment/offline/mingdaoyun-hap-linux-amd64-{目标版本号}.tar.gz` |
| HAP 微服务（ARM64） | `https://pdpublic.mingdao.com/private-deployment/offline/mingdaoyun-hap-linux-arm64-{目标版本号}.tar.gz` |
| HAP 存储组件（AMD64） | `https://pdpublic.mingdao.com/private-deployment/offline/mingdaoyun-sc-linux-amd64-{目标版本号}.tar.gz` |
| HAP 存储组件（ARM64） | `https://pdpublic.mingdao.com/private-deployment/offline/mingdaoyun-sc-linux-amd64-{目标版本号}.tar.gz` |

> 💡 如需其他组件（文档预览等）的离线包，访问 https://docs-pd.mingdao.com/deployment/offline 获取，修改 URL 中的版本号即可下载历史版本。

上传到服务器后，执行以下命令导入镜像：

```bash
# 导入镜像（替换为实际文件名）
docker load -i mingdaoyun-hap-linux-amd64-{目标版本号}.tar.gz

# 验证镜像已导入
docker images | grep mingdaoyun-hap
```

> 如有其他离线镜像，一并列出导入与验证命令

---

## 升级前准备

### 1. 数据备份

> ⚠️ **升级前必须完成备份，此步骤不可跳过。**

请参考官方文档完成数据备份：[数据备份文档](https://docs-pd.mingdao.com/deployment/docker-compose/standalone/data/backup)

### 2. 确认当前版本

执行以下命令确认当前运行版本与本文档起始版本一致：

```bash
docker ps --format "table {{.Image}}\t{{.Names}}"
```

### 3. 检查资源

- 确保磁盘空间充足（建议预留 20GB 以上）
- 确保服务器网络状态正常

---

## 升级步骤

### 第一阶段：微服务升级前操作

{若升级路径中无任何 Pre 操作，删除本阶段整节。以下各条目按实际情况保留或删除。}

#### 1. 替换镜像名称 ⚠️

> ⚠️ **特别注意**：此操作必须在升级微服务前完成。

> 💡 以下命令按默认路径编写。若曾自定义安装路径，请先替换路径再执行。
> - `docker-compose.yaml` 默认路径：`/data/mingdao/script/`
> - `service.sh` 默认路径：`/usr/local/MDPrivateDeployment/`
> - `run.sh` 默认路径：`/data/mingdao/script/`

```bash
# 替换 docker-compose.yaml 中的镜像名
sed -i -e 's/mingdaoyun-community/mingdaoyun-hap/g' /data/mingdao/script/docker-compose.yaml

# 替换 service.sh 中的服务名称
sed -i -e 's/Community/Hap/g' -e 's/community/hap/g' /usr/local/MDPrivateDeployment/service.sh

# 替换 run.sh 中的镜像名（如文件存在）
if [ -f /data/mingdao/script/run.sh ]; then
  sed -i -e 's/mingdaoyun-community/mingdaoyun-hap/g' /data/mingdao/script/run.sh
fi
```

#### 2. 创建 MongoDB 数据库（仅开启 MongoDB 认证时执行）

> 💡 仅在已开启 MongoDB 连接认证的情况下执行此步骤。

1. 进入存储组件容器：

```bash
docker exec -it $(docker ps | grep mingdaoyun-sc | awk '{print $1}') bash
```

2. 在容器内，使用含 `admin` 角色的用户登录 MongoDB（替换实际用户名和密码）：

```bash
mongo -u 用户名 -p 密码 --authenticationDatabase admin
```

3. 依次创建所有跨越版本要求的库（每个库执行以下两条命令，替换 `{库名}` 和用户信息）：

```bash
# 重复以下两条命令，直到创建完所有需要的库
use {库名}
db.createUser({ user: "修改成与其他库一致的用户名", pwd: "修改成与其他库一致的密码", roles: [{ role: "readWrite", db: "{库名}" }] })
```

> 💡 **需要创建的库**：{根据跨越版本的附加操作整理，列出所有库名，例如：`mdwfai`（v7.0.0 要求）、`mdpayment`（vX.X.X 要求）}
>
> 若所有库使用同一用户认证，则需修改该用户权限以授权新数据库，而非创建新用户。

#### 3. 存储组件升级

{若跨越多个含存储组件升级的版本，直接升级到所有版本中要求的最高版本号。}

> ⚠️ **特别注意**：将存储组件升级到 `{目标存储组件版本号}`。

1. 修改 `/data/mingdao/script/docker-compose.yaml` 中存储组件的镜像版本号为 `{目标存储组件版本号}`

> 💡 如果存储组件与微服务同时升级，可在修改完两处版本号后，最后只执行一次 `restartall`，无需分开重启。

#### 4. MongoDB 预置数据更新

> 💡 此操作可在**原版本服务运行状态下**执行，无需停机。跨多版本时只需执行目标版本一次。

{--- 联网模式 ---}

```bash
bash -c "$(curl -fsSL https://pdpublic.mingdao.com/private-deployment/data/preset_mongodb_docker.sh)" -s {目标版本号}
```

{--- 离线模式 ---}

```bash
# 在可访问互联网的机器上提前下载（下载完成后上传到服务器）
# wget https://pdpublic.mingdao.com/private-deployment/data/preset_mongodb_{目标版本号}.tar.gz

# 在服务器上执行
wget https://pdpublic.mingdao.com/private-deployment/data/preset_mongodb_docker.sh
bash ./preset_mongodb_docker.sh {目标版本号} ./preset_mongodb_{目标版本号}.tar.gz
```

---

### 第二阶段：升级微服务

#### 1. 修改镜像版本号

编辑 `/data/mingdao/script/docker-compose.yaml`，将 HAP 镜像版本号修改为目标版本：

```
image: registry.cn-hangzhou.aliyuncs.com/mdpublic/mingdaoyun-hap:{目标版本号}
```

#### 2. 重启服务

在管理器根目录下执行（通常在 `/usr/local/MDPrivateDeployment/`，以实际为准）：

```bash
bash ./service.sh restartall
```

等待命令执行完成，服务将自动完成升级并重启。

- 如遗忘 `service.sh` 文件所在路径，可使用以下命令查找

  ```text
  find / -path /proc -prune -o -name "service.sh" -print
  ```

---

### 第三阶段：微服务升级后操作

{若升级路径中无任何 Post 操作，删除本阶段整节。}

> ⚠️ **特别注意**：以下操作须在微服务镜像升级并重启完成后执行。

#### 1. 进入微服务容器执行脚本

1. 进入容器：

```bash
docker exec -it $(docker ps | grep -E 'mingdaoyun-community|mingdaoyun-hap' | awk '{print $1}') bash
```

2. 在容器内按版本**从低到高**顺序执行以下命令：

> 💡 如已自定义 MySQL 用户名、密码，注意修改命令中对应参数值（默认：用户名 `root`，密码 `123456`）。

```bash
# ---- 来自 v{版本号}（{功能说明，例如：用户多任职功能相关表字段增加}）----
mysql -h sc -P 3306 -uroot -p123456 --default-character-set=utf8 -N < /init/mysql/{版本号}/DDL.sql

# ---- 来自 v{版本号}（{功能说明}）----
mysql -h sc -P 3306 -uroot -p123456 --default-character-set=utf8 -N < /init/mysql/{版本号}/DDL.sql

# ---- 按实际跨越版本继续追加（版本从低到高排列）----
```

---

## 升级后验证

### 1. 确认服务状态

```bash
docker ps
```

确认所有容器均处于 `Up` 状态，无异常重启。

### 2. 登录系统确认版本

登录 HAP 管理后台，确认系统版本号已更新为目标版本 `{目标版本号}`。

### 3. 功能验证

- [ ] 打开工作表，创建/编辑记录
- [ ] 触发工作流，检查执行情况
- [ ] 检查统计图、报表等功能



## 异常情况排查

参考[服务运行状况检查](https://docs-pd.mingdao.com/faq/troubleshooting/service-status-check)文档对容器日志进行检查

### 1. 容器日志检查

查看微服务应用容器健康检查日志

```text
docker logs $(docker ps -a | grep mingdaoyun-community|mingdaoyun-hap | awk '{print $1}')
```

查看存储组件容器健康检查日志

```text
docker logs $(docker ps -a | grep mingdaoyun-sc | awk '{print $1}')
```

---

## 参考文档

- [版本发布历史](https://docs-pd.mingdao.com/version)
- [离线资源包](https://docs-pd.mingdao.com/deployment/offline)
- [数据备份](https://docs-pd.mingdao.com/deployment/docker-compose/standalone/data/backup)
- [微服务升级](https://docs-pd.mingdao.com/deployment/docker-compose/standalone/upgrade/hap)
- [常见问题 FAQ](https://docs-pd.mingdao.com/faq/deployment)

---

💡 声明：本文档内容由 AI 生成。尽管已努力确保信息的合理性，但 AI 模型仍可能产生不准确、过时或存在偏差的内容。请在执行关键操作前，务必对照[官方文档](https://docs-pd.mingdao.com)进行核实校验。
