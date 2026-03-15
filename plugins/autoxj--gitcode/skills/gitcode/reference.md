# GitCode API v5 完整文档（全量接口一览）

本文档整理自 [GitCode 官方 API 文档](https://docs.gitcode.com/docs/apis/)，按分类列出 **全部** v5 接口的路径、说明及官方单独文档链接，形成详细界面便于查阅与对接。

---

## 目录

- [通用说明](#通用说明)
- [Repositories（仓库）](#repositories仓库)
- [Branch（分支）](#branch分支)
- [Issues（议题）](#issues议题)
- [Search（搜索）](#search搜索)
- [Pull Requests（合并请求）](#pull-requests合并请求)
- [Commit（提交）](#commit提交)
- [Tag（标签）](#tag标签)
- [Labels（标签）](#labels标签)
- [Milestone（里程碑）](#milestone里程碑)
- [Users（用户）](#users用户)
- [Organizations（组织）](#organizations组织)
- [Webhooks](#webhooks)
- [Member（成员）](#member成员)
- [Release（发布）](#release发布)
- [Enterprise / Dashboard / OAuth / AI hub](#enterprise--dashboard--oauth20--ai-hub)
- [响应与文档说明](#响应与文档说明)

**约定**：官方文档链接格式为 `https://docs.gitcode.com/docs/apis/{slug}`，表中「官方文档」列可直接点击进入该接口的请求参数、响应示例与 Demo。

---

## 通用说明

| 项目 | 说明 |
|------|------|
| **Base URL** | `https://api.gitcode.com/api/v5` |
| **认证** | 请求头 `PRIVATE-TOKEN: {token}` 或 `Authorization: Bearer {token}`，或 query `access_token={token}`；多数列表/获取接口必选。 |
| **状态码** | 200/201/204 成功；400 缺参或未认证；401 无效/缺失 Token；403/404/409/422 禁止/未找到/冲突；429 限流（默认 50/分、4000/小时）。 |
| **官方入口** | [API 文档总览](https://docs.gitcode.com/docs/apis/)（侧栏展开各分类可看到全部接口）。 |

---

## Repositories（仓库）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/repos/{owner}/{repo}` | 获取仓库详情（含 star/fork/watch 数量等） | `stargazers_count`（星标数，该仓库被 star 的总数）、`forks_count`（Fork 数，被 fork 的次数）、`watchers_count`（关注数，watch 该仓库的用户数）、`full_name`（仓库全名，如 owner/repo）、`description`（仓库描述）、`default_branch`（默认分支名）、`open_issues_count`（未关闭的 Issue 数）等 | [获取仓库详情](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo) |
| GET | `/repos/{owner}/{repo}/git/trees/{sha}` | 获取仓库指定 SHA 的目录树 | 目录 tree：`type`（tree/blob）、`path`（路径）、`sha`（对象 SHA）等 | [获取仓库目录Tree](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-git-trees-sha) |
| GET | `/repos/{owner}/{repo}/contents/{path}` | 获取指定路径下的文件/目录内容 | 文件或目录：`name`（文件名）、`path`（路径）、`sha`（对象 SHA）、`content`（Base64 编码的文件内容，目录无此字段）等 | [获取仓库具体路径下的内容](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-contents-path) |
| POST | `/repos/{owner}/{repo}/contents/{path}` | 在仓库中新建文件 | 新建文件的提交/内容信息 | [新建文件](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-contents-path) |
| PUT | `/repos/{owner}/{repo}/contents/{path}` | 更新指定路径的文件内容 | 更新后的提交/内容信息 | [更新文件](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-contents-path) |
| DELETE | `/repos/{owner}/{repo}/contents/{path}` | 删除指定路径的文件 | 删除操作的提交信息 | [删除文件](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-contents-path) |
| GET | `/repos/{owner}/{repo}/file_list` | 获取仓库文件列表（可按 path/ref 筛选） | 文件列表：每项含路径、类型（file/dir）等 | [获取文件列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-file-list) |
| GET | `/repos/{owner}/{repo}/git/blobs/{sha}` | 根据 SHA 获取文件 Blob 内容 | Blob：`size`（字节数）、`content`（Base64 编码的原始内容）等 | [获取文件Blob](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-git-blobs-sha) |
| GET | `/repos/{owner}/{repo}/languages` | 获取仓库各语言代码统计 | 各语言及对应字节数（如 `Python: 12345`）等 | [获取仓库的语言](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-languages) |
| GET | `/repos/{owner}/{repo}/contributors` | 获取仓库贡献者列表 | 贡献者列表：每项含用户信息（id、username 等）、提交数等 | [获取仓库贡献者](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-contributors) |
| GET | `/repos/{owner}/{repo}/contributors/statistic` | 获取贡献者统计信息 | 各贡献者的统计明细 | [获取仓库贡献者统计信息](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-contributors-statistic) |
| PUT | `/repos/{owner}/{repo}/module/setting` | 设置项目模块 | 操作结果 | [设置项目模块](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-module-setting) |
| PATCH | `/repos/{owner}/{repo}` | 更新仓库设置 | 更新后的仓库对象 | [更新仓库设置](https://docs.gitcode.com/docs/apis/patch-api-v-5-repos-owner-repo) |
| DELETE | `/repos/{owner}/{repo}` | 删除仓库 | 操作结果 | [删除一个仓库](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo) |
| PUT | `/repos/{owner}/{repo}/reviewer` | 修改代码审查设置 | 操作结果 | [修改项目代码审查设置](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-reviewer) |
| PUT | `/org/{org}/repo/{repo}/status` | 仓库归档 | 操作结果 | [仓库归档](https://docs.gitcode.com/docs/apis/put-api-v-5-org-org-repo-repo-status) |
| POST | `/org/{org}/projects/{repo}/transfer` | 转移仓库 | 操作结果 | [转移仓](https://docs.gitcode.com/docs/apis/post-api-v-5-org-org-projects-repo-transfer) |
| GET | `/repos/{owner}/{repo}/transition` | 获取项目权限模式 | 权限模式信息 | [获取项目的权限模式](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-transition) |
| PUT | `/repos/{owner}/{repo}/transition` | 更新仓库权限模式 | 操作结果 | [更新仓库的权限模式](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-transition) |
| PUT | `/repos/{owner}/{repo}/push_config` | 设置项目推送规则 | 操作结果 | [设置项目推送规则](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-push-config) |
| GET | `/repos/{owner}/{repo}/push_config` | 获取项目推送规则 | 推送规则配置 | [获取项目推送规则](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-push-config) |
| POST | `/repos/{owner}/{repo}/forks` | Fork 该仓库 | 新 fork 出的仓库对象 | [Fork一个仓库](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-forks) |
| GET | `/repos/{owner}/{repo}/forks` | 查看该仓库的 Forks 列表 | Fork 仓库列表（分页，含 sort、page、per_page） | [查看仓库的Forks](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-forks) |
| POST | `/repos/{owner}/{repo}/img/upload` | 上传图片 | 图片 URL 等信息 | [上传图片](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-img-upload) |
| POST | `/repos/{owner}/{repo}/file/upload` | 上传文件 | 文件 URL 等信息 | [上传文件](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-file-upload) |
| GET | `/repos/{owner}/{repo}/subscribers` | 列出 watch 了该仓库的用户 | watch 用户列表（分页） | [列出 watch 了仓库的用户](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-subscribers) |
| GET | `/repos/{owner}/{repo}/stargazers` | 列出 star 了该仓库的用户 | star 用户列表（分页） | [列出 star 了仓库的用户](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-stargazers) |
| PUT | `/repos/{owner}/{repo}/repo_settings` | 更新仓库设置 | 操作结果 | [更新仓库设置](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-repo-settings) |
| GET | `/repos/{owner}/{repo}/repo_settings` | 获取仓库设置 | 仓库设置项 | [获取仓库设置](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-repo-settings) |
| GET | `/repos/{owner}/{repo}/pull_request_settings` | 获取 PR 相关设置 | PR 设置项 | [获取 Pull Request设置](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pull-request-settings) |
| PUT | `/repos/{owner}/{repo}/pull_request_settings` | 更新 PR 设置 | 操作结果 | [更新 Pull Request设置](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-pull-request-settings) |
| PUT | `/repos/{owner}/{repo}/members/{username}` | 更新项目成员角色 | 操作结果 | [更新项目成员角色](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-members-username) |
| POST | `/repos/{owner}/{repo}/transfer` | 仓库转移 | 操作结果 | [仓库转移](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-transfer) |
| GET | `/repos/{owner}/{repo}/customized_roles` | 获取项目自定义角色列表 | 自定义角色列表 | [获取项目自定义角色](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-customized-roles) |
| GET | `/repos/{owner}/{repo}/download_statistics` | 下载次数统计（当天/近 30 天/历史总量）；路径为下划线 `download_statistics` | `download_statistics_detail`（按日明细，含 pdate、today_dl_cnt、total_dl_cnt）、`download_statistics_total`（近 30 天总下载量）、`download_statistics_history_total`（历史总下载量） | [下载次数统计](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-download-statistics) |
| GET | `/repos/{owner}/{repo}/raw/{path}` | 获取 raw 文件内容 | 文件原始内容 | [获取 raw 文件](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-raw-path) |
| GET | `/repos/{owner}/{repo}/events` | 获取仓库动态 | 动态事件列表 | [获取仓库动态](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-events-access-token-your-token) |
| GET | `/users/{username}/repos` | 列出某用户的公开仓库 | 仓库列表（分页） | [用户公开仓库](https://docs.gitcode.com/docs/apis/get-api-v-5-users-username-repos) |
| GET | `/user/repos` | 列出当前用户仓库（需认证） | 仓库列表（分页） | [当前用户仓库](https://docs.gitcode.com/docs/apis/get-api-v-5-user-repos) |
| POST | `/orgs/{org}/repos` | 创建组织下仓库 | 新建的仓库对象 | [创建组织仓库](https://docs.gitcode.com/docs/apis/post-api-v-5-orgs-org-repos) |

---

## Branch（分支）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/repos/{owner}/{repo}/branches` | 获取项目所有分支 | 分支列表：`name`（分支名）、`commit`（最新提交信息）、`protected`（是否保护分支）等 | [获取项目所有分支](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-branches) |
| POST | `/repos/{owner}/{repo}/branches` | 创建分支（body: ref, branch 名） | 新分支对象 | [创建分支](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-branches) |
| DELETE | `/repos/{owner}/{repo}/branches/{name}` | 删除指定分支 | 操作结果 | [删除分支](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-branches-name) |
| GET | `/repos/{owner}/{repo}/branches/{branch}` | 获取单个分支详情 | `name`（分支名）、`commit`（该分支最新提交）、`protected`（是否保护分支）等 | [获取单个分支](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-branches-branch) |
| PUT | `/repos/{owner}/{repo}/branches/setting_new` | 新建保护分支规则 | 操作结果 | [新建保护分支规则](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-branches-setting-new) |
| DELETE | `/repos/{owner}/{repo}/branches/{wildcard}/setting` | 删除保护分支规则 | 操作结果 | [删除保护分支规则](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-branches-wildcard-setting) |
| GET | `/repos/{owner}/{repo}/protect_branches` | 获取保护分支规则列表 | 保护规则列表 | [获取保护分支规则列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-protect-branches) |
| PUT | `/repos/{owner}/{repo}/branches/{wildcard}/setting` | 更新保护分支规则 | 操作结果 | [更新保护分支规则](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-branches-wildcard-setting) |

---

## Issues（议题）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/repos/{owner}/{repo}/issues` | 获取仓库所有 issues（可 state/per_page/page） | Issue 列表：`title`（标题）、`state`（open/closed）、`number`（Issue 编号）、`user`（创建者）、`labels`（标签）等 | [获取仓库所有 issues](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-issues) |
| GET | `/repos/{owner}/{repo}/issues/{number}` | 获取仓库某个 Issue 详情 | 单个 Issue 完整信息 | [获取仓库的某个Issue](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-issues-number) |
| POST | `/repos/{owner}/{repo}/issues` | 创建 Issue | 新建的 Issue 对象 | [创建Issue](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-issues) |
| PATCH | `/repos/{owner}/issues/{number}` | 更新 Issue | 更新后的 Issue 对象 | [更新Issue](https://docs.gitcode.com/docs/apis/patch-api-v-5-repos-owner-issues-number) |
| GET | `/repos/{owner}/{repo}/issues/{number}/related_branches` | 获取 issue 关联分支列表 | 关联分支列表 | [获取issue关联的分支列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-issues-number-related-branches) |
| PUT | `/repos/{owner}/{repo}/issues/{number}/related_branches` | 设置 Issue 关联分支 | 操作结果 | [设置Issue关联的分支](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-issues-number-related-branches) |
| GET | `/repos/{owner}/{repo}/issues/{number}/pull_requests` | 获取 issue 关联的 PR 列表 | 关联的 PR 列表 | [获取 issue 关联的 pull requests](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-issues-number-pull-requests) |
| GET | `/repos/{owner}/issues/{number}/operate_logs` | 获取某个 issue 操作日志 | 操作日志列表 | [获取某个issue下的操作日志](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-issues-number-operate-logs) |
| GET | `/repos/{owner}/{repo}/issues/{number}/comments` | 获取某个 Issue 所有评论 | 评论列表 | [获取仓库某个Issue所有的评论](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-issues-number-comments) |
| POST | `/repos/{owner}/{repo}/issues/{number}/comments` | 创建 Issue 评论 | 新建的评论对象 | [创建Issue评论](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-issues-number-comments) |
| GET | `/repos/{owner}/{repo}/issues/comments` | 获取仓库所有 Issue 评论 | 评论列表 | [获取仓库所有 Issue 评论](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-issues-comments) |
| GET | `/repos/{owner}/{repo}/issues/comments/{id}` | 获取 Issue 某条评论 | 单条评论内容 | [获取仓库Issue某条评论](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-issues-comments-id) |
| PATCH | `/repos/{owner}/{repo}/issues/comments/{id}` | 更新 Issue 某条评论 | 更新后的评论 | [更新Issue某条评论](https://docs.gitcode.com/docs/apis/patch-api-v-5-repos-owner-repo-issues-comments-id) |
| DELETE | `/repos/{owner}/{repo}/issues/comments/{id}` | 删除 Issue 某条评论 | 操作结果 | [删除Issue某条评论](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-issues-comments-id) |
| POST | `/repos/{owner}/{repo}/issues/{number}/labels` | 为 Issue 添加标签 | 操作结果 | [创建Issue标签](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-issues-number-labels) |
| DELETE | `/repos/{owner}/{repo}/issues/{number}/labels/{name}` | 删除 Issue 某标签 | 操作结果 | [删除Issue标签](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-issues-number-labels-name) |
| GET | `/user/issues` | 获取授权用户所有 Issues | Issue 列表 | [获取授权用户的所有Issues](https://docs.gitcode.com/docs/apis/get-api-v-5-user-issues) |
| GET | `/orgs/{org}/issues` | 获取当前用户某组织 Issues | Issue 列表 | [获取当前用户某个组织的Issues](https://docs.gitcode.com/docs/apis/get-api-v-5-orgs-org-issues) |
| GET | `/enterprises/{enterprise}/issues` | 获取某企业所有 Issues | Issue 列表 | [获取某个企业的所有Issues](https://docs.gitcode.com/docs/apis/get-api-v-5-enterprises-enterprise-issues) |
| GET | `/enterprises/{enterprise}/issues/{number}` | 获取企业的某个 Issue | 单个 Issue | [获取企业的某个Issue](https://docs.gitcode.com/docs/apis/get-api-v-5-enterprises-enterprise-issues-number) |
| GET | `/enterprises/{enterprise}/issues/{number}/comments` | 获取企业某 Issue 所有评论 | 评论列表 | [获取企业某个Issue所有评论](https://docs.gitcode.com/docs/apis/get-api-v-5-enterprises-enterprise-issues-number-comments) |
| GET | `/enterprises/{enterprise}/issue_statuses` | 获取企业 issue 状态 | 状态列表 | [获取企业issue状态](https://docs.gitcode.com/docs/apis/get-api-v-5-enterprises-enterprise-issue-statuses) |
| GET | `/enterprises/{enterprise}/issues/{issue_id}/labels` | 获取企业某 Issue 所有标签 | 标签列表 | [获取企业某个Issue所有标签](https://docs.gitcode.com/docs/apis/get-api-v-5-enterprises-enterprise-issues-issue-id-labels) |
| GET | `/repos/{owner}/{repo}/issues/{number}/user_reactions` | 获取 issue 表态列表 | 表态用户列表 | [获取issue的表态列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-issues-number-user-reactions) |
| GET | `/repos/{owner}/{repo}/issues/comment/{comment_id}/user_reactions` | 获取 issue 评论表态列表 | 表态列表 | [获取issue评论的表态列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-issues-comment-comment-id-user-reactions) |
| GET | `/repos/{owner}/{repo}/issues/{number}/modify_history` | 获取 issue 修改历史 | 修改历史列表 | [获取issue的修改历史](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-issues-number-modify-history) |
| GET | `/repos/{owner}/{repo}/issues/comment/{comment_id}/modify_history` | 获取 issue 评论修改历史 | 修改历史列表 | [获取issue评论的修改历史](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-issues-comment-comment-id-modify-history) |

---

## Search（搜索）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/search/users` | 按关键词搜索用户（q、sort、order、per_page、page） | 用户列表：`id`（用户 ID）、`username`（用户名）、`avatar`（头像 URL）等 | [搜索用户](https://docs.gitcode.com/docs/apis/get-api-v-5-search-users) |
| GET | `/search/issues` | 全局搜索 Issues（q、state、repo 等） | Issue 列表 | [搜索 Issues](https://docs.gitcode.com/docs/apis/get-api-v-5-search-issues) |
| GET | `/search/repositories` | 搜索仓库（q、sort、order、per_page、page） | 仓库列表：每项含 `stargazers_count`、`forks_count`、`watchers_count`、`full_name`、`description` 等 | [搜索仓库](https://docs.gitcode.com/docs/apis/get-api-v-5-search-repositories) |

---

## Pull Requests（合并请求）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/repos/{owner}/{repo}/pulls` | 获取 PR 列表（state/per_page/page） | PR 列表：`title`（标题）、`state`（open/closed/merged）、`number`（PR 编号）、`head`（源分支）、`base`（目标分支）等 | [列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls) |
| GET | `/repos/{owner}/{repo}/pulls/{number}` | 获取单个 PR 详情 | 单个 PR 完整信息（含 diff、合并状态等） | [获取单个](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number) |
| GET | `/user/pulls` | 获取当前用户 PR 列表 | PR 列表 | [当前用户 PR](https://docs.gitcode.com/docs/apis/get-api-v-5-user-pulls) |
| POST | `/repos/{owner}/{repo}/pulls` | 创建 PR | 新建的 PR 对象 | [创建](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-pulls) |
| PATCH | `/repos/{owner}/{repo}/pulls/{number}` | 更新 PR | 更新后的 PR 对象 | [更新 PR](https://docs.gitcode.com/docs/apis/patch-api-v-5-repos-owner-repo-pulls-number) |
| PUT | `/repos/{owner}/{repo}/pulls/{number}/merge` | 合并 PR | 合并结果 | [合并 PR](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-pulls-number-merge) |
| GET | `/repos/{owner}/{repo}/pulls/{number}/merge` | 获取 PR 合并状态 | 是否已合并等信息 | [获取 PR 合并状态](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number-merge) |
| GET | `/repos/{owner}/{repo}/pulls/{number}/files` | PR 变更文件列表与 diff | 文件列表及 diff 统计 | [PR 文件](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number-files) |
| GET | `/repos/{owner}/{repo}/pulls/{number}/files/json` | PR 文件列表（仅 JSON） | 文件列表 JSON | [PR 文件 JSON](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number-files-json) |
| GET | `/repos/{owner}/{repo}/pulls/{number}/commits` | PR 提交列表 | 提交列表 | [PR 提交列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number-commits) |
| GET | `/repos/{owner}/{repo}/pulls/{number}/issues` | PR 关联的 issues | 关联 Issue 列表 | [PR 关联 issues](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number-issues) |
| POST | `/repos/{owner}/{repo}/pulls/{number}/comments` | 创建 PR 评论 | 新建评论对象 | [创建 PR 评论](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-pulls-number-comments) |
| GET | `/repos/{owner}/{repo}/pulls/{number}/comments` | 获取 PR 评论列表 | 评论列表 | [获取 PR 评论](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number-comments) |
| GET | `/repos/{owner}/{repo}/pulls/comments/{id}` | 获取 PR 某条评论 | 单条评论 | [获取 PR 评论](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-comments-id) |
| PATCH | `/repos/{owner}/{repo}/pulls/comments/{id}` | 更新 PR 某条评论 | 更新后的评论 | [更新 PR 评论](https://docs.gitcode.com/docs/apis/patch-api-v-5-repos-owner-repo-pulls-comments-id) |
| DELETE | `/repos/{owner}/{repo}/pulls/comments/{id}` | 删除 PR 某条评论 | 操作结果 | [删除 PR 评论](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-pulls-comments-id) |
| POST | `/repos/{owner}/{repo}/pulls/{number}/review` | 提交 PR 审查 | 审查结果 | [提交 PR 审查](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-pulls-number-review) |
| GET | `/repos/{owner}/{repo}/pulls/{number}/operate_logs` | 获取 PR 操作日志 | 操作日志列表 | [PR 操作日志](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number-operate-logs) |
| POST | `/repos/{owner}/{repo}/pulls/{number}/labels` | 为 PR 添加标签 | 操作结果 | [PR 添加标签](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-pulls-number-labels) |
| GET | `/repos/{owner}/{repo}/pulls/{number}/labels` | 获取 PR 标签列表 | 标签列表 | [PR 标签列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number-labels) |
| PUT | `/repos/{owner}/{repo}/pulls/{number}/labels` | 更新 PR 标签 | 操作结果 | [更新 PR 标签](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-pulls-number-labels) |
| DELETE | `/repos/{owner}/{repo}/pulls/{number}/labels/{name}` | 删除 PR 某标签 | 操作结果 | [删除 PR 标签](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-pulls-number-labels-name) |
| POST | `/repos/{owner}/{repo}/pulls/{number}/test` | 提交 PR 测试 | 操作结果 | [提交 PR 测试](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-pulls-number-test) |
| GET | `/repos/{owner}/{repo}/pulls/{number}/option_approval_testers` | 获取 PR 可选审批测试人 | 可选用户列表 | [可选审批测试人](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number-option-approval-testers) |
| PATCH | `/repos/{owner}/{repo}/pulls/{number}/testers` | 更新 PR 测试人 | 操作结果 | [更新 PR 测试人](https://docs.gitcode.com/docs/apis/patch-api-v-5-repos-owner-repo-pulls-number-testers) |
| POST | `/repos/{owner}/{repo}/pulls/{number}/testers` | 添加 PR 测试人 | 操作结果 | [添加 PR 测试人](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-pulls-number-testers) |
| DELETE | `/repos/{owner}/{repo}/pulls/{number}/testers` | 移除 PR 测试人 | 操作结果 | [移除 PR 测试人](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-pulls-number-testers) |
| PATCH | `/repos/{owner}/{repo}/pulls/{number}/assignees` | 更新 PR 指派人 | 操作结果 | [更新 PR 指派人](https://docs.gitcode.com/docs/apis/patch-api-v-5-repos-owner-repo-pulls-number-assignees) |
| POST | `/repos/{owner}/{repo}/pulls/{number}/assignees` | 添加 PR 指派人 | 操作结果 | [添加 PR 指派人](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-pulls-number-assignees) |
| DELETE | `/repos/{owner}/{repo}/pulls/{number}/assignees` | 移除 PR 指派人 | 操作结果 | [移除 PR 指派人](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-pulls-number-assignees) |
| POST | `/repos/{owner}/{repo}/pulls/{number}/linked_issues` | 关联 PR 与 Issue | 操作结果 | [关联 PR 与 Issue](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-pulls-number-linked-issues) |
| DELETE | `/repos/{owner}/{repo}/pulls/{number}/issues` | 解除 PR 关联 Issue | 操作结果 | [解除 PR 关联 Issue](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-pulls-number-issues) |
| POST | `/repos/{owner}/{repo}/pulls/{number}/discussions/{discussions_id}/comments` | PR 讨论下创建评论 | 新建评论 | [PR 讨论评论](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-pulls-number-discussions-discussions-id-comments) |
| PUT | `/repos/{owner}/{repo}/pulls/{number}/comments/discussions/{id}` | 更新 PR 讨论评论 | 操作结果 | [更新 PR 讨论评论](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-pulls-number-comments-discussions-id) |
| POST | `/repos/{owner}/{repo}/pulls/{number}/approval_reviewers` | 添加 PR 审批人 | 操作结果 | [添加 PR 审批人](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-pulls-number-approval-reviewers) |
| DELETE | `/repos/{owner}/{repo}/pulls/{number}/approval_reviewers` | 移除 PR 审批人 | 操作结果 | [移除 PR 审批人](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-pulls-number-approval-reviewers) |
| GET | `/repos/{owner}/{repo}/pulls/{number}/option_approval_reviewers` | 获取 PR 可选审批人 | 可选用户列表 | [PR 可选审批人](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number-option-approval-reviewers) |
| GET | `/repos/{owner}/{repo}/pulls/{number}/user_reactions` | 获取 PR 表态列表 | 表态用户列表 | [PR 表态列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number-user-reactions) |
| GET | `/repos/{owner}/{repo}/pulls/comment/{comment_id}/user_reactions` | 获取 PR 评论表态列表 | 表态列表 | [PR 评论表态](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-comment-comment-id-user-reactions) |
| GET | `/repos/{owner}/{repo}/pulls/{number}/modify_history` | 获取 PR 修改历史 | 修改历史列表 | [PR 修改历史](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-number-modify-history) |
| GET | `/repos/{owner}/{repo}/pulls/comment/{comment_id}/modify_history` | 获取 PR 评论修改历史 | 修改历史列表 | [PR 评论修改历史](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-pulls-comment-comment-id-modify-history) |
| GET | `/org/{org}/pull_requests` | 获取组织 PR 列表 | PR 列表 | [组织 PR 列表](https://docs.gitcode.com/docs/apis/get-api-v-5-org-org-pull-requests) |
| GET | `/enterprises/{enterprise}/pull_requests` | 获取企业 PR 列表 | PR 列表 | [企业 PR 列表](https://docs.gitcode.com/docs/apis/get-api-v-5-enterprises-enterprise-pull-requests) |
| GET | `/enterprises/{enterprise}/issues/{number}/pull_requests` | 获取企业某 Issue 关联 PR | PR 列表 | [企业 Issue 关联 PR](https://docs.gitcode.com/docs/apis/get-api-v-5-enterprises-enterprise-issues-number-pull-requests) |

---

## Commit（提交）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/repos/{owner}/{repo}/commits` | 获取提交列表（branch/sha/path、per_page、page） | 提交列表：`sha`（提交 SHA）、`message`（提交说明）、`author`（作者）、`date`（提交时间）等 | [列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-commits) |
| GET | `/repos/{owner}/{repo}/commits/{sha}` | 获取单个 commit 详情 | 单条提交详情（sha、message、author、parents、stats 等） | [单个](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-commits-sha) |
| POST | `/repos/{owner}/{repo}/commits/{sha}/comments` | 创建 commit 评论 | 新建评论对象 | [创建 commit 评论](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-commits-sha-comments) |
| GET | `/repos/{owner}/{repo}/commits/{ref}/comments` | 获取 commit 评论列表 | 评论列表 | [获取 commit 评论](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-commits-ref-comments) |
| GET | `/repos/{owner}/{repo}/commits/{sha}/diff` | 获取 commit 的 diff | diff 文本 | [获取 commit 的 diff](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-commits-sha-diff) |
| GET | `/repos/{owner}/{repo}/commits/{sha}/patch` | 获取 commit 的 patch | patch 文本 | [获取 commit 的 patch](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-commits-sha-patch) |

---

## Tag（标签）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/repos/{owner}/{repo}/tags` | 获取仓库 tag 列表 | tag 列表：`name`（标签名）、`zipball_url`（zip 下载链接）、`tarball_url`（tar 下载链接）、`commit`（指向的提交）等 | [列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-tags) |
| POST | `/repos/{owner}/{repo}/tags` | 创建 tag（body: ref, tag 名, message） | 新建的 tag 对象 | [创建](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-tags) |
| DELETE | `/repos/{owner}/{repo}/tags/{tag}` | 删除指定 tag | 操作结果 | [删除](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-tags-tag) |

---

## Labels（标签）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/repos/{owner}/{repo}/labels` | 获取仓库标签列表 | 标签列表：`name`（标签名）、`color`（颜色值）、`description`（描述）等 | [列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-labels) |
| POST | `/repos/{owner}/{repo}/labels` | 创建标签 | 新建的标签对象 | [创建](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-labels) |
| PUT | `/repos/{owner}/{repo}/labels/{name}` | 更新标签 | 更新后的标签对象 | [更新](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-labels-name) |
| DELETE | `/repos/{owner}/{repo}/labels/{name}` | 删除标签 | 操作结果 | [删除](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-labels-name) |
| PUT | `/repos/{owner}/{repo}/project_labels` | 更新项目标签设置 | 操作结果 | [更新项目标签](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-project-labels) |
| POST | `/repos/{owner}/{repo}/issues/{number}/labels` | 为 issue 添加标签 | 操作结果 | [为 issue 添加标签](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-issues-number-labels) |

---

## Milestone（里程碑）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/repos/{owner}/{repo}/milestones` | 获取里程碑列表 | 里程碑列表：`title`（标题）、`state`（open/closed）、`due_on`（截止日期）、`open_issues`（未关闭 Issue 数）等 | [列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-milestones) |
| GET | `/repos/{owner}/{repo}/milestones/{id}` | 获取单个里程碑详情 | 单个里程碑完整信息 | [单个](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-milestones-id) |
| POST | `/repos/{owner}/{repo}/milestones` | 创建里程碑 | 新建的里程碑对象 | [创建](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-milestones) |
| PUT | `/repos/{owner}/{repo}/milestones/{id}` | 更新里程碑 | 更新后的里程碑对象 | [更新](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-milestones-id) |
| DELETE | `/repos/{owner}/{repo}/milestones/{id}` | 删除里程碑 | 操作结果 | [删除](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-milestones-id) |

---

## Users（用户）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/user` | 获取当前登录用户（需认证） | 用户信息：`id`（用户 ID）、`username`（用户名）、`avatar`（头像 URL）、`email`（邮箱）等 | [当前用户](https://docs.gitcode.com/docs/apis/get-api-v-5-user) |
| GET | `/users/{username}` | 按用户名获取用户信息 | 用户信息：`id`、`username`、`avatar`（头像）、`bio`（个人简介）等 | [按用户名](https://docs.gitcode.com/docs/apis/get-api-v-5-users-username) |
| GET | `/users/{username}/repos` | 列出某用户的公开仓库 | 仓库列表 | [用户公开仓库](https://docs.gitcode.com/docs/apis/get-api-v-5-users-username-repos) |
| GET | `/users/{username}/orgs` | 获取用户所属组织列表 | 组织列表 | [用户所属组织](https://docs.gitcode.com/docs/apis/get-api-v-5-users-username-orgs) |
| GET | `/user/orgs` | 获取当前用户所属组织（需认证） | 组织列表 | [当前用户组织](https://docs.gitcode.com/docs/apis/get-api-v-5-user-orgs) |
| GET | `/users/{username}/starred` | 获取用户 star 的仓库列表 | 仓库列表 | [用户 star 的仓库](https://docs.gitcode.com/docs/apis/get-api-v-5-users-username-starred) |
| POST | `/user/repos` | 创建个人仓库 | 见官方文档 | [创建个人仓库](https://docs.gitcode.com/docs/apis/post-api-v-5-user-repos) |

---

## Organizations（组织）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/orgs/{org}` | 获取组织信息 | 组织信息：`id`、`name`（组织名）、`avatar`（头像）、`description`（描述）等 | [组织信息](https://docs.gitcode.com/docs/apis/get-api-v-5-orgs-org) |
| GET | `/orgs/{org}/repos` | 列出组织下仓库 | 仓库列表 | [组织仓库](https://docs.gitcode.com/docs/apis/get-api-v-5-orgs-org-repos) |
| GET | `/orgs/{org}/members` | 获取组织成员列表 | 成员列表 | [组织成员](https://docs.gitcode.com/docs/apis/get-api-v-5-orgs-org-members) |
| GET | `/orgs/{org}/members/{username}` | 获取组织内某成员详情 | 成员信息及角色 | [组织成员详情](https://docs.gitcode.com/docs/apis/get-api-v-5-orgs-org-members-username) |
| POST | `/orgs/{org}/repos` | 创建组织仓库 | 见官方文档 | [创建组织仓库](https://docs.gitcode.com/docs/apis/post-api-v-5-orgs-org-repos) |

---

## Webhooks

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/repos/{owner}/{repo}/hooks` | 获取仓库 Webhook 列表 | Webhook 列表：`url`（回调地址）、`events`（触发事件类型）、`active`（是否启用）等 | [列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-hooks) |
| POST | `/repos/{owner}/{repo}/hooks` | 创建 Webhook | 新建的 Webhook 对象 | [创建](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-hooks) |
| PUT | `/repos/{owner}/{repo}/hooks/{id}` | 更新 Webhook | 更新后的 Webhook 对象 | [更新](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-hooks-id) |
| DELETE | `/repos/{owner}/{repo}/hooks/{id}` | 删除 Webhook | 操作结果 | [删除](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-hooks-id) |

---

## Member（成员）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/repos/{owner}/{repo}/members` | 获取项目成员列表 | 成员列表（用户名、角色等） | [项目成员列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-members) |
| GET | `/repos/{owner}/{repo}/members/{username}` | 获取项目内某成员详情 | 成员信息及角色 | [项目成员详情](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-members-username) |
| POST | `/repos/{owner}/{repo}/members` | 添加项目成员 | 操作结果 | [添加成员](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-members) |
| DELETE | `/repos/{owner}/{repo}/members/{username}` | 移除项目成员 | 操作结果 | [移除成员](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-members-username) |
| PUT | `/repos/{owner}/{repo}/collaborators/{username}` | 更新项目协作者权限 | 操作结果 | [更新项目协作者](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-collaborators-username) |
| GET | `/orgs/{org}/members/{username}` | 获取组织内某成员详情 | 成员信息及角色 | [组织成员](https://docs.gitcode.com/docs/apis/get-api-v-5-orgs-org-members-username) |
| PUT | `/repos/{owner}/{repo}/members/{username}` | 更新项目成员角色 | 见官方文档 | [更新项目成员角色](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-members-username) |

---

## Release（发布）

| Method | Path | 功能说明 | 可获取信息 | 官方文档 |
|--------|------|----------|------------|----------|
| GET | `/repos/{owner}/{repo}/releases` | 获取 Release 列表 | Release 列表：`tag_name`（关联 tag）、`name`（Release 名称）、`body`（说明）、`assets`（附件及下载链接）、`published_at`（发布时间）等 | [列表](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-releases) |
| GET | `/repos/{owner}/{repo}/releases/tags/{tag}` | 按 tag 名获取对应 Release | 单个 Release 详情 | [按 tag](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-releases-tags-tag) |
| GET | `/repos/{owner}/{repo}/releases/{id}` | 获取单个 Release 详情 | Release 详情（含 assets 下载链接等） | [单个](https://docs.gitcode.com/docs/apis/get-api-v-5-repos-owner-repo-releases-id) |
| POST | `/repos/{owner}/{repo}/releases` | 创建 Release | 新建的 Release 对象 | [创建](https://docs.gitcode.com/docs/apis/post-api-v-5-repos-owner-repo-releases) |
| PUT | `/repos/{owner}/{repo}/releases/{id}` | 更新 Release | 更新后的 Release 对象 | [更新](https://docs.gitcode.com/docs/apis/put-api-v-5-repos-owner-repo-releases-id) |
| DELETE | `/repos/{owner}/{repo}/releases/{id}` | 删除 Release | 操作结果 | [删除](https://docs.gitcode.com/docs/apis/delete-api-v-5-repos-owner-repo-releases-id) |

---

## Enterprise / Dashboard / OAuth2.0 / AI hub

| 分类 | 功能说明 | 可获取信息 / 说明 | 官方入口 |
|------|----------|-------------------|----------|
| **Enterprise** | 企业版接口（成员、议题、PR 等），含 v8 接口 | 各接口响应见官方文档 | [官方侧栏 Enterprise](https://docs.gitcode.com/docs/apis/) |
| **Dashboard** | 动态、看板等（如 kanban-list） | 各接口响应见官方文档 | [官方侧栏 Dashboard](https://docs.gitcode.com/docs/apis/) |
| **OAuth2.0** | 获取/刷新授权 Token | access_token、refresh_token、expires_in 等 | [OAuth2.0](https://docs.gitcode.com/docs/apis/oauth) · [获取或刷新 Token](https://docs.gitcode.com/docs/apis/post-oauth-token-grant-type-authorization-code-code-code-client-id-client-id-client-secret-client-secret) |
| **AI hub** | AI 相关能力 | 见官方文档 | [官方侧栏 AI hub](https://docs.gitcode.com/docs/apis/) |

---

## 响应与文档说明

- 各接口的**功能说明**与**可获取信息**已写在对应分类的表格中；按需查阅上文各节即可。
- **仓库详情**（GET `/repos/{owner}/{repo}`）：一次请求即可获得 `stargazers_count`（星标数，该仓库被 star 的总数）、`forks_count`（Fork 数）、`watchers_count`（关注数）及 `full_name`、`description`、`default_branch`、`open_issues_count` 等；完整字段见 [OpenAPI 仓库模块](https://docs.gitcode.com/v1-docs/docs/openapi/repos/)。
- **下载次数**：需单独请求 GET `/repos/{owner}/{repo}/download_statistics`（路径为下划线 **`download_statistics`**，非 `download-statistics`）；响应含 `download_statistics_detail`（按日明细）、`download_statistics_total`（近 30 天总下载量）、`download_statistics_history_total`（历史总下载量）。

### 文档来源与更新

- 本文档整理自 [GitCode API 文档入口](https://docs.gitcode.com/docs/apis/)，每个接口在官方站有单独页面（请求参数、响应示例、Demo）。
- 更完整参数与示例可参考 [OpenAPI 仓库/议题/PR 等模块](https://docs.gitcode.com/v1-docs/docs/openapi/)。
- 若与官方文档不一致，**以官方文档为准**。
