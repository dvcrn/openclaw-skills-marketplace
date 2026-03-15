# 调试案例集

详细的内核崩溃调试案例分析。

## 案例 1: kernel BUG 定位

### 症状

```
PANIC: "kernel BUG at pipe.c:120!"
```

### 分析步骤

```
# 1. 确认系统信息
crash> sys
KERNEL: vmlinux
DUMPFILE: vmcore
CPUS: 8
DATE: Mon Jan 15 10:30:45 2024
UPTIME: 00:15:32
LOAD AVERAGE: 0.50, 0.35, 0.20
TASKS: 156
NODENAME: server01
RELEASE: 4.18.0-348.el8.x86_64
VERSION: #1 SMP Mon Jan 1 00:00:00 UTC 2024
MACHINE: x86_64  (2900 Mhz)
MEMORY: 32 GB
PANIC: "kernel BUG at pipe.c:120!"

# 2. 查看内核日志
crash> log | tail -100
[...]
kernel BUG at fs/pipe.c:120!
invalid opcode: 0000 [#1] SMP PTI
CPU: 3 PID: 1234 Comm: worker Tainted: G           O      4.18.0-348.el8.x86_64
RIP: 0010:pipe_read+0x120/0x300
[...]

# 3. 分析调用栈
crash> bt
PID: 1234   TASK: ffff88012b98e040  CPU: 3   COMMAND: "worker"
#0 [ffffc90000123e00] __die at ffffffff8105a2b0
#1 [ffffc90000123e30] do_trap at ffffffff8105a1a0
#2 [ffffc90000123e80] invalid_op at ffffffff81c00bf4
#3 [ffffc90000123f00] pipe_read at ffffffff81234560
#4 [ffffc90000123f80] do_readv at ffffffff81210000
#5 [ffffc90000123fc0] sys_readv at ffffffff81210100

# 4. 展开栈帧获取参数
crash> bt -f
#3 [ffffc90000123f00] pipe_read at ffffffff81234560
    ffff88012b98e040:  ffff880123456000   # file 指针
    ffff88012b98e080:  ffff880123457000   # buffer
    ffff88012b98e0c0:  0000000000001000   # count
    [...]

# 5. 链式追踪数据结构
crash> struct file.f_dentry ffff880123456000
  f_dentry = ffff880123458000

crash> struct dentry.d_inode ffff880123458000
  d_inode = ffff880123459000

crash> struct inode.i_pipe ffff880123459000
  i_pipe = ffff88012345a000

crash> struct pipe_inode_info ffff88012345a000
struct pipe_inode_info {
  mutex = {
    owner = 0,
    count = 2,        # 异常！应该 <= 1
    wait_list = {...}
  },
  readers = 1,
  writers = 1,
  [...]
}

# 6. 批量检查所有 pipe inode
crash> kmem -S pipe_inode_cache | head
CACHE    NAME                OBJSIZE  ALLOCATED  TOTAL  SLABS  SSIZE
ffff88012a000000  pipe_inode_cache      184       45      60     3    4k

# 查找计数异常的 mutex
crash> foreach bt | grep -B10 "pipe_read"
```

### 根因分析

`pipe_inode_info.mutex.count = 2` 表示信号量计数异常，可能是：
- 双重释放
- 竞态条件
- 使用后释放

---

## 案例 2: 死锁分析

### 症状

系统挂起，无响应，但心跳正常。

### 分析步骤

```
# 1. 查看所有 CPU 状态
crash> bt -a
CPU 0:
#0 [ffff880000000000] schedule at ffffffff81a12345
#1 [ffff880000000100] schedule_timeout at ffffffff81a13456
#2 [ffff880000000180] wait_for_completion at ffffffff81a14567
PID: 100   TASK: ffff88012a000000  CPU: 0   COMMAND: "thread_A"

CPU 1:
#0 [ffff880000010000] schedule at ffffffff81a12345
#1 [ffff880000010100] schedule_timeout at ffffffff81a13456
#2 [ffff880000010180] __down at ffffffff81a15678
PID: 101   TASK: ffff88012a001000  CPU: 1   COMMAND: "thread_B"

# 2. 查看不可中断睡眠进程
crash> ps -m | grep UN
  100  UN   0.0   0  ffff88012a000000  thread_A
  101  UN   0.1   0  ffff88012a001000  thread_B

# 3. 分析等待队列
crash> foreach UN bt
PID: 100   TASK: ffff88012a000000  CPU: 0   COMMAND: "thread_A"
#0 schedule
#1 schedule_timeout
#2 wait_for_completion
#3 some_function_A

PID: 101   TASK: ffff88012a001000  CPU: 1   COMMAND: "thread_B"
#0 schedule
#1 __down
#2 down
#3 some_function_B

# 4. 检查锁持有情况
crash> struct mutex ffff88012b000000
struct mutex {
  owner = 0xffff88012a000000,  # thread_A 持有
  wait_lock = {...},
  count = 0,
  wait_list = {
    next = 0xffff88012b000020,
    prev = 0xffff88012b000020
  }
}

# 5. 追踪 thread_A 等待什么
crash> bt -f 100
#2 wait_for_completion
    completion = 0xffff88012b001000
crash> struct completion ffff88012b001000
struct completion {
  done = 0,
  wait = {...}
}

# 6. 谁应该完成这个 completion？
crash> search -k ffff88012b001000
ffff88012a002000: ffff88012b001000  # 在 thread_B 的栈中
```

### 根因分析

- thread_A 持有 mutex，等待 completion
- thread_B 等待同一个 mutex
- thread_B 应该完成 completion，但被阻塞

**死锁模式**: ABBA 死锁

---

## 案例 3: 内存耗尽

### 症状

```
Out of memory: Kill process 1234 (java) score 500 or sacrifice child
```

### 分析步骤

```
# 1. 查看内存统计
crash> kmem -i
                 PAGES        TOTAL      PERCENTAGE
TOTAL MEM       8388608      32 GB         ----
FREE            104857       400 MB         1%
USED            8283751     31.6 GB        98%
SHARED           524288       2 GB         6%
BUFFERS          262144       1 GB         3%
CACHED          1572864       6 GB        18%

# 2. 查看内存区域
crash> kmem -z
ZONE  DMA:
  pages_free     = 4096
  pages_min      = 128
ZONE  DMA32:
  pages_free     = 65536
ZONE  NORMAL:
  pages_free     = 32768
ZONE  MOVABLE:
  pages_free     = 0

# 3. 查看 slab 使用
crash> kmem -s | sort -k 4 -rn | head
CACHE            NAME              OBJSIZE  ALLOCATED  TOTAL
ffff88012a000000 kmalloc-8192       8192    524288    600000
ffff88012a001000 kmalloc-4096       4096    262144    300000
ffff88012a002000 dentry              192    131072    150000
ffff88012a003000 inode_cache         592     65536     80000

# 4. 查看进程内存使用
crash> ps -G | sort -k 5 -rn | head
PID    PPID  CPU   TASK        ST  %MEM   VSZ      RSS   COMM
1234   1     3   ffff88012a003000  IN  25.0  8GB    8GB   java
5678   1     2   ffff88012a004000  IN  15.0  5GB    5GB   python
9012   1     1   ffff88012a005000  IN  10.0  3GB    3GB   node

# 5. 详细查看大进程
crash> vm 1234
PID: 1234   TASK: ffff88012a003000  CPU: 3   COMMAND: "java"
MM               PGD          RSS    TOTAL_VM
ffff88012b000000 ffff88012b001000  8GB    8GB

VMA           START          END     FLAGS FILE
ffff88012c000000 7f0000000000 7f0000800000 877b3b [heap]
ffff88012c001000 7f0000800000 7f0001000000 877b3b [heap]
...

# 6. 查看 OOM killer 记录
crash> log | grep -A 50 "Out of memory"
```

### 根因分析

- 内存使用率 98%
- java 进程占用 25% 内存
- NORMAL zone 几乎耗尽
- 可能存在内存泄漏

---

## 案例 4: NULL 指针解引用

### 症状

```
BUG: unable to handle kernel NULL pointer dereference at 0000000000000010
```

### 分析步骤

```
# 1. 查看 panic 信息
crash> sys
PANIC: "BUG: unable to handle kernel NULL pointer dereference at 0000000000000010"

# 2. 查看调用栈
crash> bt
#0 __die at ffffffff8105a2b0
#1 exc_page_fault at ffffffff8105b3c0
#2 asm_exc_page_fault at ffffffff81c00bf4
#3 my_driver_ioctl at ffffffff81234560
#4 sys_ioctl at ffffffff81210000

# 3. 反汇编出问题函数
crash> dis my_driver_ioctl
0xffffffff81234500 <my_driver_ioctl>:   push   rbp
0xffffffff81234501 <my_driver_ioctl+1>: mov    rbp,rsp
...
0xffffffff81234550 <my_driver_ioctl+80>: mov    rax,QWORD PTR [rdi+0x10]  # 崩溃点
...

# 4. 展开栈帧看参数
crash> bt -f
#3 my_driver_ioctl at ffffffff81234550
    rdi = 0x0000000000000000   # NULL!
    rsi = 0x000000000000abcd

# 5. 确认结构体偏移
crash> struct -o my_device
struct my_device {
    [0x0] void *priv;
    [0x8] int state;
    [0x10] struct device *dev;   # +0x10 正是崩溃偏移
}

# 6. 追踪 NULL 从哪里来
crash> bt -l
#3 my_driver_ioctl at /home/user/my_driver.c:123
crash> list my_driver.devices -s my_driver.device -h my_driver_head
```

### 根因分析

- `my_driver_ioctl` 第一个参数 `rdi` 为 NULL
- 尝试访问 `rdi + 0x10` 导致页错误
- 需要在代码中添加 NULL 检查

---

## 案例 5: 栈溢出

### 症状

```
kernel stack overflow (double-fault)
```

### 分析步骤

```
# 1. 检查栈溢出
crash> bt -v
PID: 1234   COMMAND: "worker"   STACK OVERFLOW DETECTED
    stack pointer: ffffc90000123fc0
    stack base:    ffffc90000120000
    stack limit:   ffffc90000124000
    overflow by:   16 bytes

# 2. 查看调用栈深度
crash> bt
#0 recursive_function at ffffffff81234560
#1 recursive_function at ffffffff81234580
#2 recursive_function at ffffffff81234580
...（重复数百次）
#500 recursive_function at ffffffff81234580

# 3. 查看栈使用
crash> bt -r | wc -l
8192    # 8KB 栈已满

# 4. 检查大结构体
crash> struct large_context
struct large_context {
    char buffer[4096];
    int data[1024];
    ...
}
SIZE: 8200  # 结构体本身超过栈大小！

# 5. 检查其他任务栈状态
crash> foreach bt -v
```

### 根因分析

- 递归调用过深
- 或在栈上分配大结构体
- 需要改为动态分配或减少递归深度