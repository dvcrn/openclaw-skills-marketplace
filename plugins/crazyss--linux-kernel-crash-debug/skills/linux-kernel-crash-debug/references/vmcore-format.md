# vmcore 文件格式

内核转储文件格式详解。

## ELF 格式基础

vmcore 通常采用 ELF (Executable and Linkable Format) 格式：

```bash
# 查看 vmcore 类型
file vmcore
# 输出: ELF 64-bit LSB core file, x86-64, version 1 (SYSV), SVR4-style

# 查看 ELF 头
readelf -h vmcore

# 查看 Program Headers（描述内存段）
readelf -l vmcore

# 查看 Section Headers
readelf -S vmcore

# 查看 Note Sections
readelf -n vmcore

# 使用 objdump 查看
objdump -p vmcore     # Program Headers
objdump -x vmcore     # 所有头信息
```

### ELF Core Dump 结构

```
+------------------+
|   ELF Header     |  <- 文件类型: ET_CORE
+------------------+
| Program Headers  |  <- 描述内存段
+------------------+
|  Note Sections   |  <- VMCOREINFO, 寄存器等
+------------------+
|   Memory Segments|  <- 实际内存内容
+------------------+
```

## VMCOREINFO

VMCOREINFO 是一个特殊的 ELF note section，包含内核关键信息：

```
# 在 crash 中查看
crash> sys -i

# 使用 readelf 查看
readelf -n vmcore | grep -A 100 VMCOREINFO

# 提取并解析
crash> p *vmcoreinfo_data
```

### 关键字段

| 字段 | 说明 |
|------|------|
| `OSRELEASE` | 内核版本字符串 |
| `PAGESIZE` | 页面大小 |
| `init_uts_ns.name.release` | 内核版本 |
| `phys_base` | 物理地址基址（x86_64） |
| `VA_BITS` | 虚拟地址位数（ARM64） |
| `KERNELOFFSET` | 内核偏移（KASLR） |
| `CRASHTIME` | 崩溃时间戳 |

### 结构体信息

VMCOREINFO 包含关键结构体的大小和成员偏移：

```
SIZE(page)=64
OFFSET(page.flags)=0
OFFSET(page._refcount)=8
OFFSET(page.mapping)=24

SIZE(pglist_data)=...
SIZE(zone)=...
SIZE(free_area)=...
SIZE(list_head)=16
```

### 符号地址

```
init_uts_ns=ffffffff8283a040
node_online_map=ffffffff8283e000
swapper_pg_dir=ffffffff82800000
init_task=ffffffff82812480
```

## 支持的转储格式

### 1. ELF Core Dump

标准 ELF 格式，最通用：

```bash
# 特点
- 可用 gdb 直接读取
- 包含完整的内存布局信息
- 支持压缩（ELF with gzip/xz）

# 生成方式
kdump (默认配置)
makedumpfile -E vmcore vmcore.elf
```

### 2. kdump Compressed

压缩格式，节省空间：

```bash
# 特点
- 默认压缩格式
- 需要 crash 或 makedumpfile 解析
- 支持过滤和压缩级别

# 生成方式
kdump (压缩配置)
makedumpfile -c -d 31 vmcore vmcore.kdump

# 解压为 ELF
makedumpfile -E vmcore.kdump vmcore.elf
```

### 3. diskdump

Red Hat diskdump 格式：

```bash
# 特点
- Red Hat 历史格式
- 支持压缩
- 需要特定内核补丁

# 识别
crash> sys
DUMPFILE: diskdump
```

### 4. netdump

Red Hat netdump 格式：

```bash
# 特点
- 通过网络传输转储
- 用于远程崩溃收集
- 需要 netdump 服务器

# 识别
crash> sys
DUMPFILE: netdump
```

### 5. LKCD

Linux Kernel Crash Dump：

```bash
# 特点
- 早期 Linux 转储机制
- 分段存储
- 已较少使用
```

### 6. Raw RAM Dump

原始内存转储：

```bash
# 启动方式
crash vmlinux ddr.bin --ram_start=0x80000000

# 多个内存块
crash vmlinux ddr1.bin@0x80000000 ddr2.bin@0x880000000

# 特点
- 无 ELF 头
- 需要指定物理起始地址
- 常用于嵌入式系统
```

## kdump 工作原理

### 正常内核 vs 捕获内核

```
+-------------------+     +-------------------+
|   正常内核        |     |   捕获内核        |
|   (生产系统)      |     |   (kdump 内核)    |
+-------------------+     +-------------------+
        |                         |
        | crash/panic             |
        |------------------------>|
        |   kexec 快速重启        |
        |                         |
        |                   生成 vmcore
        |                         |
        v                         v
```

### 内存预留

```bash
# 查看 kdump 预留内存
cat /sys/kernel/kexec_crash_size

# GRUB 配置
crashkernel=128M@16M      # 固定位置
crashkernel=auto          # 自动计算
crashkernel=256M,high     # 高端内存
```

### 转储流程

```
1. 内核 panic
2. kexec 快速启动捕获内核
3. 捕获内核运行
4. 通过 /proc/vmcore 读取内存
5. makedumpfile 处理并保存
6. 重启系统
```

## makedumpfile 工具

处理和压缩 vmcore：

```bash
# 基本用法
makedumpfile vmcore vmcore.filtered

# 压缩
makedumpfile -c vmcore vmcore.compressed   # zlib
makedumpfile -l vmcore vmcore.compressed   # lzo
makedumpfile -p vmcore vmcore.compressed   # snappy

# 过滤（-d 级别）
# 1: 排除零页
# 2: 排除缓存页
# 4: 排除缓存私有页
# 8: 排除用户数据页
# 16: 排除空闲页
makedumpfile -d 31 -c vmcore vmcore.small  # 最小化

# 转换为 ELF
makedumpfile -E vmcore vmcore.elf

# 查看信息
makedumpfile -f vmcore

# 分割大文件
makedumpfile --split vmcore part1 part2 part3

# 合并分割文件
makedumpfile --reassemble part1 part2 part3 vmcore
```

## vmcore 分析技巧

### 检查 vmcore 完整性

```bash
# 使用 file 命令
file vmcore

# 使用 crash 测试加载
crash --osrelease vmcore

# 检查 VMCOREINFO
readelf -n vmcore | grep VMCOREINFO
```

### 查找匹配的 vmlinux

```bash
# 从 vmcore 提取内核版本
strings vmcore | grep "Linux version"
readelf -n vmcore | grep OSRELEASE

# 或在 crash 中
crash --osrelease vmcore
```

### 处理损坏的 vmcore

```bash
# 跳过错误检查
crash --no_kallsyms vmlinux vmcore

# 使用最小加载
crash --minimal vmlinux vmcore
```

### 从部分内存重建

```bash
# 多个内存区域
crash vmlinux mem1.bin@0x0 mem2.bin@0x100000000

# 使用 System.map 替代部分符号
crash -S System.map vmlinux vmcore
```

## 调试信息

### 查看 vmcore 详细信息

```
crash> sys
crash> sys -i           # VMCOREINFO
crash> sys -t           # panic 时间
crash> sys -n           # NMI 信息
```

### 内存布局

```
crash> kmem -v          # vmalloc 区域
crash> kmem -n          # 内存节点信息
crash> vtop <addr>      # 地址翻译
```

### CPU 状态

```
crash> bt -a            # 所有 CPU 调用栈
crash> mach             # 机器信息
crash> set -c <cpu>     # 切换 CPU 上下文
```