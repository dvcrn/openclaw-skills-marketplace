# Grafana API 参考文档

## 认证方式

### API Key 认证
```
Authorization: Bearer <your_api_key>
```

创建 API Key:
1. 登录 Grafana
2. Configuration → API keys
3. Add API key
4. 选择角色（Viewer/Admin）
5. 复制生成的 Key

## 常用 API 端点

### 仪表盘相关

#### 获取仪表盘
```http
GET /api/dashboards/uid/:uid
```

#### 搜索仪表盘
```http
GET /api/search?type=dash-db&query=:keyword
```

### 数据源相关

#### 获取数据源列表
```http
GET /api/datasources
```

#### 检查数据源健康
```http
GET /api/datasources/uid/:uid/health
```

### 告警相关

#### 获取告警状态
```http
GET /api/v1/alerts/state
```

#### 获取告警规则
```http
GET /api/v1/provisioning/alert-rules
```

### 查询相关

#### 执行 PromQL 查询
```http
POST /api/ds/query
Content-Type: application/json

{
  "queries": [{
    "refId": "A",
    "expr": "up",
    "intervalMs": 1000,
    "maxDataPoints": 100
  }]
}
```

## 渲染服务

### 仪表盘截图
```http
GET /render/d/:uid
  ?from=now-6h
  &to=now
  &width=1920
  &height=1080
  &tz=Asia/Shanghai
```

### 单面板截图
```http
GET /render/d-solo/:uid/:panelId
  ?from=now-6h
  &to=now
  &width=800
  &height=600
```

## 健康检查指标

### 主机监控 (Node Exporter)

```promql
# CPU 使用率
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用率
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# 磁盘使用率
100 - ((node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100)

# 系统负载
node_load1 / node_cpu_count

# 网络接收流量
rate(node_network_receive_bytes_total[5m])

# 网络发送流量
rate(node_network_transmit_bytes_total[5m])

# 磁盘读取I/O
rate(node_disk_reads_completed_total[5m])

# 磁盘写入I/O
rate(node_disk_writes_completed_total[5m])

# 运行进程数
node_procs_running

# 阻塞进程数
node_procs_blocked

# 系统启动时间
node_boot_time_seconds

# 登录用户数
node_logged_in_users

# 文件系统inode使用率
(node_filesystem_files - node_filesystem_files_free) / node_filesystem_files * 100
```

### MySQL 监控

```promql
# MySQL 是否运行
mysql_up

# 连接数
mysql_global_status_threads_connected

# QPS
rate(mysql_global_status_queries[5m])

# 慢查询数
rate(mysql_global_status_slow_queries[5m])

# 缓存命中率
mysql_global_status_qcache_hits / (mysql_global_status_qcache_hits + mysql_global_status_qcache_inserts) * 100

# 锁等待时间
rate(mysql_global_status_innodb_row_lock_waits[5m])

# 临时表创建率
rate(mysql_global_status_created_tmp_tables[5m])

# 临时磁盘表率
rate(mysql_global_status_created_tmp_disk_tables[5m])

# InnoDB缓冲池使用率
mysql_global_status_innodb_buffer_pool_pages_data / mysql_global_status_innodb_buffer_pool_pages_total * 100

# 线程缓存命中率
mysql_global_status_threads_created / mysql_global_status_connections * 100

# 打开表数
mysql_global_status_open_tables

# 表锁等待
rate(mysql_global_status_table_locks_waited[5m])
```

### Redis 监控

```promql
# Redis 是否运行
redis_up

# 内存使用
redis_memory_used_bytes

# 连接数
redis_connected_clients

# 命中率
redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total) * 100

# 键数量
redis_db_keys

# 过期键
rate(redis_expired_keys_total[5m])

# 驱逐键
rate(redis_evicted_keys_total[5m])

# 命令执行数
rate(redis_commands_total[5m])

# 阻塞客户端
redis_blocked_clients

# 拒绝连接
rate(redis_rejected_connections_total[5m])

# 持久化最后保存时间
redis_rdb_last_save_time_seconds

# 内存碎片率
redis_memory_used_rss_bytes / redis_memory_used_bytes
```

### Kubernetes 监控

```promql
# 集群节点数
count(kube_node_info)

# 节点就绪状态
kube_node_status_condition{condition="Ready", status="true"}

# Pod总数
count(kube_pod_info)

# Pod运行状态
kube_pod_status_phase

# 容器CPU使用率
rate(container_cpu_usage_seconds_total[5m]) / container_spec_cpu_quota * 100

# 容器内存使用
container_memory_usage_bytes / container_spec_memory_limit_bytes * 100

# Deployment可用副本
kube_deployment_status_replicas_available / kube_deployment_status_replicas

# StatefulSet就绪副本
kube_statefulset_status_replicas_ready / kube_statefulset_status_replicas

# Job成功率
kube_job_status_succeeded / (kube_job_status_succeeded + kube_job_status_failed)

# PVC使用率
kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes * 100

# API服务器请求率
rate(apiserver_request_total[5m])

# etcd请求延迟
histogram_quantile(0.95, rate(etcd_request_duration_seconds_bucket[5m]))

# 网络接收字节
rate(container_network_receive_bytes_total[5m])

# 网络发送字节
rate(container_network_transmit_bytes_total[5m])
```

### RocketMQ 监控

```promql
# 生产者TPS
rate(rocketmq_producer_tps[5m])

# 消费者TPS
rate(rocketmq_consumer_tps[5m])

# 消息积压
rocketmq_consumer_message_accumulation

# 发送消息成功率
rate(rocketmq_producer_send_success[5m]) / rate(rocketmq_producer_send_total[5m]) * 100

# 消费消息成功率
rate(rocketmq_consumer_consume_success[5m]) / rate(rocketmq_consumer_consume_total[5m]) * 100

# 存储大小
rocketmq_broker_message_store_size

# 主题消息数量
rocketmq_topic_message_count

# 队列偏移量
rocketmq_group_consume_queue_offset

# 代理连接数
rocketmq_broker_connection_count

# 磁盘使用率
rocketmq_broker_disk_usage_ratio * 100

# 内存使用率
rocketmq_broker_memory_usage_ratio * 100

# 拉取消息延迟
histogram_quantile(0.95, rate(rocketmq_consumer_pull_time_bucket[5m]))

# 发送消息延迟
histogram_quantile(0.95, rate(rocketmq_producer_send_time_bucket[5m]))
```

### Elasticsearch 监控

```promql
# 集群健康状态 (1=green, 2=yellow, 3=red)
elasticsearch_cluster_health_status

# 集群节点数
elasticsearch_cluster_health_number_of_nodes

# 集群数据节点数
elasticsearch_cluster_health_number_of_data_nodes

# 索引文档总数
elasticsearch_indices_docs

# 索引存储大小
elasticsearch_indices_store_size_bytes

# 查询总数
rate(elasticsearch_indices_search_query_total[5m])

# 查询延迟
histogram_quantile(0.95, rate(elasticsearch_indices_search_query_time_seconds_bucket[5m]))

# 索引操作总数
rate(elasticsearch_indices_indexing_index_total[5m])

# 索引延迟
histogram_quantile(0.95, rate(elasticsearch_indices_indexing_index_time_seconds_bucket[5m]))

# JVM堆使用率
elasticsearch_jvm_memory_used_bytes / elasticsearch_jvm_memory_max_bytes * 100

# JVM GC 计数
rate(elasticsearch_jvm_gc_collection_seconds_count[5m])

# 线程池活跃线程数
elasticsearch_thread_pool_active_count

# HTTP连接数
elasticsearch_http_open_connections

# 磁盘使用率
elasticsearch_fs_total_disk_free_bytes / elasticsearch_fs_total_disk_total_bytes * 100

# 缓存命中率
elasticsearch_indices_request_cache_hit_count / (elasticsearch_indices_request_cache_hit_count + elasticsearch_indices_request_cache_miss_count) * 100
```

### JVM 监控

```promql
# JVM堆内存使用率
jvm_memory_bytes_used{area="heap"} / jvm_memory_bytes_max{area="heap"} * 100

# JVM非堆内存使用率
jvm_memory_bytes_used{area="nonheap"} / jvm_memory_bytes_max{area="nonheap"} * 100

# JVM堆内存使用量
jvm_memory_bytes_used{area="heap"}

# JVM非堆内存使用量
jvm_memory_bytes_used{area="nonheap"}

# GC次数
rate(jvm_gc_collection_seconds_count[5m])

# GC总时间
rate(jvm_gc_collection_seconds_sum[5m])

# 当前线程数
jvm_threads_current

# 守护线程数
jvm_threads_daemon

# 死锁线程数
jvm_threads_deadlocked

# 已加载类数
jvm_classes_loaded

# 类加载时间
rate(jvm_classes_loaded_total[5m])

# JVM运行时间
jvm_runtime_start_time_ms

# JVM信息
jvm_info

# 内存池使用率
jvm_memory_pool_bytes_used / jvm_memory_pool_bytes_max * 100

# CPU使用时间
rate(jvm_runtime_process_cpu_load[5m]) * 100
```

### .NET 应用监控

```promql
# .NET进程总内存
dotnet_total_memory_bytes

# .NET GC收集次数
rate(dotnet_gc_collections_total[5m])

# .NET GC分配字节数
rate(dotnet_runtime_dotnet_gc_allocated_bytes_total[5m])

# .NET线程池线程数
dotnet_threadpool_threads_total

# .NET工作线程数
dotnet_threadpool_worker_threads

# .NET完成端口线程数
dotnet_threadpool_completed_items_total

# ASP.NET Core请求总数
rate(aspnetcore_requests_total[5m])

# ASP.NET Core请求每秒
rate(aspnetcore_requests_per_second[5m])

# ASP.NET Core当前请求数
aspnetcore_current_requests

# ASP.NET Core失败请求数
rate(aspnetcore_requests_failed_total[5m])

# ASP.NET Core请求持续时间
histogram_quantile(0.95, rate(aspnetcore_request_duration_seconds_bucket[5m]))

# .NET异常总数
rate(dotnet_exceptions_total[5m])

# .NET运行时信息
dotnet_runtime_info

# ASP.NET Core连接数
aspnetcore_connections_current

# ASP.NET Core启动时间
aspnetcore_uptime_seconds

# .NET JIT编译时间
rate(dotnet_jit_compilation_time_total[5m])
```

## 飞书 API 参考

### 获取租户访问令牌
```http
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
Content-Type: application/json

{
  "app_id": "xxx",
  "app_secret": "xxx"
}
```

### 创建云文档
```http
POST https://open.feishu.cn/open-apis/docx/v1/docs
Authorization: Bearer <tenant_access_token>
Content-Type: application/json

{
  "title": "文档标题",
  "folder_token": "文件夹 Token"
}
```

### 更新文档内容
```http
PATCH https://open.feishu.cn/open-apis/docx/v1/docs/:doc_id/content
Authorization: Bearer <tenant_access_token>
Content-Type: application/json

{
  "content": "文档内容"
}
```

### 上传文件
```http
POST https://open.feishu.cn/open-apis/drive/v1/files/upload_all
Authorization: Bearer <tenant_access_token>
Content-Type: multipart/form-data

file: <image_file>
```

### 在文档中插入图片
```http
PATCH https://open.feishu.cn/open-apis/docx/v1/docs/:doc_id/content
Authorization: Bearer <tenant_access_token>
Content-Type: application/json

{
  "requests": [{
    "insertBlocks": {
      "location": {
        "index": 0
      },
      "blocks": [{
        "image": {
          "token": "<file_token>"
        }
      }]
    }
  }]
}
```

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 401 | 认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
| 503 | 服务不可用 |
