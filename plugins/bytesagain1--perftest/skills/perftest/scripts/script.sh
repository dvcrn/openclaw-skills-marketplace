#!/bin/bash
cmd_time() { local cmd="$*"; [ -z "$cmd" ] && { echo "Usage: perftest time <command>"; return 1; }
    echo "Timing: $cmd"
    local start=$(python3 -c "import time; print(time.time())")
    eval "$cmd" > /dev/null 2>&1
    local end=$(python3 -c "import time; print(time.time())")
    python3 -c "print('Elapsed: {:.3f}s'.format(float('$end')-float('$start')))"
}
cmd_benchmark() { local n="${1:-10}"; shift; local cmd="$*"
    [ -z "$cmd" ] && { echo "Usage: perftest benchmark <iterations> <command>"; return 1; }
    echo "Benchmarking ($n iterations): $cmd"
    python3 -c "
import subprocess,time
times=[]
for i in range(int('$n')):
 start=time.time()
 subprocess.run('$cmd',shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 elapsed=time.time()-start
 times.append(elapsed)
print('  Min: {:.3f}s'.format(min(times)))
print('  Max: {:.3f}s'.format(max(times)))
print('  Avg: {:.3f}s'.format(sum(times)/len(times)))
print('  Total: {:.3f}s'.format(sum(times)))
"; }
cmd_diskio() { local size="${1:-100}"
    echo "Disk IO test (${size}MB)..."
    local start=$(date +%s%N)
    dd if=/dev/zero of=/tmp/perftest_disk bs=1M count="$size" 2>/dev/null
    local end=$(date +%s%N)
    local elapsed=$(( (end-start)/1000000 ))
    local speed=$((size*1000/elapsed))
    echo "  Write: ${speed}MB/s (${elapsed}ms for ${size}MB)"
    rm -f /tmp/perftest_disk
}
cmd_help() { echo "PerfTest - Performance Benchmarking"; echo "Commands: time <command> | benchmark <n> <command> | diskio [size_mb] | help"; }
cmd_info() { echo "PerfTest v1.0.0 | Powered by BytesAgain"; }
case "$1" in time) shift; cmd_time "$@";; benchmark) shift; cmd_benchmark "$@";; diskio) shift; cmd_diskio "$@";; info) cmd_info;; help|"") cmd_help;; *) cmd_help; exit 1;; esac
