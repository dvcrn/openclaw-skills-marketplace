# Advanced Commands Reference

详细的高级命令用法，按需加载。

## list - 链表遍历

遍历内核链表，自动跟踪 next/prev 指针：

```
# 基本语法
list <struct.member> <start_addr>
list -h <start_addr>    # start 是包含嵌入 list_head 的数据结构
list -H <start_addr>    # start 是独立的 LIST_HEAD() 地址

# 常用选项
-o offset     # next 指针在结构体中的偏移
-s struct     # 格式化显示结构体内容
-S struct     # 直接从内存读取成员值
-r            # 反向遍历（使用 prev 指针）
-B            # 使用 Brent 算法检测循环链表
-e end        # 指定结束地址

# 示例
# 遍历任务层次
crash> list task_struct.p_pptr c169a000

# 遍历文件系统类型
crash> list file_system_type.next -s file_system_type.name,fs_flags c03adc90

# 遍历运行队列
crash> list task_struct.run_list -H runqueue_head

# 遍历所有任务的 PID
crash> list task_struct.tasks -s task_struct.pid -h ffff88012b98e040

# 遍历 dentry 子目录
crash> list -o dentry.d_child -s dentry.d_name.name -O dentry.d_subdirs -h <parent_dentry>

# 检测循环链表
crash> list -B -h <start_addr>
```

## rd - 内存读取

读取并显示内存内容：

```
# 基本语法
rd [options] <address|symbol> [count]

# 地址类型选项
-p      # 物理地址
-u      # 用户虚拟地址
-m      # Xen 主机机器地址
-f      # dumpfile 偏移

# 输出格式选项
-d      # 有符号十进制
-D      # 无符号十进制
-x      # 不显示 ASCII 翻译
-s      # 符号化显示
-S      # 显示 slab cache 名称
-N      # 网络字节序
-R      # 反向显示
-a      # ASCII 字符显示

# 数据大小选项
-8      # 8 位
-16     # 16 位
-32     # 32 位（默认）
-64     # 64 位

# 范围选项
-e addr     # 显示到指定地址
-o offs     # 偏移起始地址
-r file     # 输出原始数据到文件

# 示例
crash> rd -a linux_banner       # ASCII 显示内核版本字符串
crash> rd -s f6e31f70 28        # 符号化显示 28 个字
crash> rd -S f6e31f70 28        # 显示 slab cache 名
crash> rd -SS f6e31f70 28       # 双重 slab 显示
crash> rd -d jiffies            # 十进制显示
crash> rd -64 kernel_version    # 64 位显示
crash> rd c009bf2c -e c009bf60  # 范围显示
crash> rd -p 1000 10            # 从物理地址读取
crash> rd -u 80b4000 20         # 从用户空间读取
```

## search - 内存搜索

在内存中搜索特定值：

```
# 基本语法
search [options] <value>

# 搜索范围选项
-s start    # 起始地址
-e end      # 结束地址
-l length   # 搜索长度
-k          # 内核虚拟地址空间
-K          # 内核空间（不含 vmalloc）
-V          # 内核空间（不含 unity-mapped）
-u          # 用户虚拟地址空间
-p          # 物理地址空间
-t          # 所有任务的内核栈
-T          # 活动任务的内核栈

# 搜索类型选项
-c          # 搜索字符串
-w          # 搜索 32 位整数
-h          # 搜索 16 位短整数

# 其他选项
-m mask     # 忽略掩码位
-x count    # 显示找到值前后的内存内容

# 示例
# 在用户空间搜索 0xdeadbeef
crash> search -u deadbeef

# 带掩码搜索
crash> search -s _etext -m ffff0000 abcd

# 搜索 4KB 页面
crash> search -s c532c000 -l 4096 ffffffff

# 搜索物理内存
crash> search -p babe0000 -m ffff

# 搜索字符串
crash> search -k -c "can't allocate memory"
crash> search -k -c "Failure to"

# 搜索所有任务栈
crash> search -t ffff81002c0a3050

# 显示上下文
crash> search -x 5 -k deadbeef
```

## vtop - 虚拟地址翻译

将虚拟地址转换为物理地址，显示页表遍历过程：

```
# 基本语法
vtop [-c [pid|taskp]] [-u|-k] <address>

# 选项
-u          # 用户虚拟地址
-k          # 内核虚拟地址
-c pid      # 使用指定进程的页表
-c taskp    # 使用指定任务地址的页表

# 示例
# 翻译用户空间地址
crash> vtop 80b4000

# 翻译内核空间地址
crash> vtop c806e000

# 使用指定进程的页表
crash> vtop -c 1359 c806e000

# 输出结构示例
VIRTUAL   PHYSICAL
7f09cd705000 2322db000
PGD: 235d707f0 => 800000023489f067
PUD: 23489f138 => 234727067
PMD: 234727358 => 35eba067
PTE: 35eba828

# 页面标志位解释
(PRESENT|RW|USER|ACCESSED|DIRTY)

# 交换分区信息（如果页面已换出）
SWAP: /dev/sda8  OFFSET: 22716
```

### 页表层级

x86_64 四级页表：
- **PGD** (Page Global Directory): 页全局目录
- **PUD** (Page Upper Directory): 页上级目录
- **PMD** (Page Middle Directory): 页中间目录
- **PTE** (Page Table Entry): 页表项

## kmem - 内存子系统分析

深入分析内核内存状态：

```
# 内存使用概览
crash> kmem -i              # 显示内存使用信息

# 页面相关
crash> kmem -p              # 显示所有 page 结构
crash> kmem -p <addr>       # 显示特定地址的 page 信息
crash> kmem -P <phys_addr>  # 物理地址参数
crash> kmem -m <fields>     # 显示指定 page 字段
crash> kmem -g              # 显示 page flags 枚举值

# Slab 分配器
crash> kmem -s              # 显示基本 kmalloc slab 数据
crash> kmem -S              # 显示详细 slab 数据（包括所有对象）
crash> kmem -S <cache>      # 显示指定 slab 缓存
crash> kmem -r              # 显示 root slab 缓存累积数据
crash> kmem -I <cache>      # 忽略指定的 slab 缓存

# 内存区域
crash> kmem -z              # 显示 per-zone 内存统计
crash> kmem -n              # 显示内存节点/section/block

# vmalloc
crash> kmem -v              # 显示 vmalloc 分配的区域

# 空闲内存
crash> kmem -f              # 显示空闲内存头
crash> kmem -F              # 同 -f，并显示链接的页面

# 其他
crash> kmem -c              # 验证 page_hash_table
crash> kmem -V              # 显示 vm_stat 表
crash> kmem -o              # 显示 CPU 偏移值
crash> kmem -h              # 显示 hugepage 信息

# 查找地址所属
crash> kmem <addr>          # 查找地址属于哪个 slab/page
```

## foreach - 批量任务操作

对一组任务执行同一命令：

```
# 基本语法
foreach [pid|taskp|name|state] <command> [flags]

# 进程状态筛选
RU  - Running
IN  - Interruptible
UN  - Uninterruptible
ST  - Stopped
ZO  - Zombie
TR  - Traced
SW  - Swapping
DE  - Dead
WA  - Wakekill
PA  - Parked
ID  - Idle
NE  - New

# 特殊筛选
kernel      # 内核线程
user        # 用户进程
gleader     # 线程组领导者
active      # 活动任务

# 支持的命令及其标志
bt:     -r -t -l -e -R -f -F -o -s -x -d
vm:     -p -v -m -R -d -x
task:   -R -d -x
files:  -c -R
net:    -s -S -R -d -x
ps:     -G -s -p -c -t -l -a -g -r -y
sig:    -g
vtop:   -c -u -k
set:    (无标志)

# 示例
crash> foreach bt              # 所有进程调用栈
crash> foreach bash task       # 所有 bash 进程的 task_struct
crash> foreach files           # 所有进程打开的文件
crash> foreach UN bt           # 所有不可中断睡眠进程的调用栈
crash> foreach kernel bt       # 所有内核线程的调用栈
crash> foreach user ps         # 所有用户进程
crash> foreach 'event.*' task -R state  # 正则匹配进程名
```

## bt - 高级选项

调用栈回溯的高级用法：

```
# CPU 相关
-a              # 所有 CPU 的活动任务
-c cpu          # 指定 CPU（可逗号分隔多个）

# 栈帧展开
-f              # 展开每个栈帧的原始数据
-F              # 符号化显示栈帧数据

# 符号信息
-l              # 显示源文件和行号
-s              # 显示符号名和偏移
-x              # 十六进制偏移（配合 -s）
-d              # 十进制偏移（配合 -s）

# 栈分析
-t              # 显示栈中所有文本符号
-T              # 从 task_struct 上方开始
-e              # 搜索栈中的异常帧
-v              # 检查栈溢出

# 过滤
-R symbol       # 仅显示引用该符号的栈
-n idle         # 过滤 idle 任务
-g              # 显示线程组所有线程

# 自定义起点
-I ip           # 指定起始指令指针
-S sp           # 指定起始栈指针

# 兼容性
-o              # 使用旧版回溯方法
-O              # 默认使用旧版方法

# 示例
crash> bt -a                   # 所有 CPU 活动任务
crash> bt -c 0,2               # CPU 0 和 2
crash> bt -f 1592              # 展开进程 1592 的栈帧
crash> bt -F -l                # 符号化 + 源码行号
crash> bt -sx                  # 符号名 + 十六进制偏移
crash> bt -e                   # 搜索异常帧
crash> bt -v                   # 检查栈溢出
crash> bt -R spin_lock         # 仅显示含 spin_lock 的栈
crash> bt -I ffffffff81000000 -S ffff880000000000  # 自定义起点
```

## gdb 直通模式

直接使用 GDB 命令：

```
# 单次调用
crash> gdb help
crash> gdb bt
crash> gdb info registers
crash> gdb x/20i $rip

# 持续 gdb 模式
crash> set gdb on
(gdb) bt
(gdb) info threads
(gdb) frame 3
(gdb) print *current
(gdb) set gdb off

# 在 gdb 模式下调用 crash 命令
(gdb) crash bt
(gdb) crash ps

# 常用 gdb 命令
(gdb) info registers       # 寄存器信息
(gdb) info threads         # 线程信息
(gdb) frame N              # 切换栈帧
(gdb) up/down              # 上下移动栈帧
(gdb) print <expr>         # 打印表达式
(gdb) x/NFU <addr>         # 检查内存
(gdb) disassemble          # 反汇编
(gdb) list                 # 源码列表
```