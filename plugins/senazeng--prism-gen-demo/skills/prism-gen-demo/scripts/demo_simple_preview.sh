#!/bin/bash
# 环境检查（不强制）
source "$(dirname "$0")/_simple_env.sh" 2>/dev/null || true
set -euo pipefail

# 简化版数据预览 - 不依赖pandas

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <数据源名称> [行数]"
    echo ""
    echo "示例:"
    echo "  $0 step4a_admet_final.csv"
    echo "  $0 step5b_final_candidates.csv 10"
    echo ""
    echo "使用 demo_list_sources.sh 查看所有可用数据源"
    exit 1
fi

SOURCE_NAME="$1"
ROWS="${2:-10}"
CSV_FILE="$DATA_DIR/$SOURCE_NAME"

# 检查文件是否存在
if [ ! -f "$CSV_FILE" ]; then
    echo "❌ 文件不存在: $CSV_FILE"
    echo ""
    echo "可用文件:"
    find "$DATA_DIR" -name "*.csv" -type f -exec basename {} \; | sort
    exit 1
fi

# 检查行数参数
if ! [[ "$ROWS" =~ ^[0-9]+$ ]]; then
    echo "❌ 行数必须是正整数: $ROWS"
    exit 1
fi

if [ "$ROWS" -lt 1 ]; then
    ROWS=10
fi

echo "# PRISM_GEN_DEMO - 简化数据预览"
echo "## 文件: $SOURCE_NAME"
echo "## 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 基本文件信息
line_count=$(wc -l < "$CSV_FILE")
molecule_count=$((line_count - 1))
display_rows=$ROWS

if [ "$display_rows" -gt "$molecule_count" ]; then
    display_rows="$molecule_count"
fi

echo "**基本信息**:"
echo "- 总分子数: $molecule_count"
echo "- 显示行数: $display_rows"
echo ""

# 读取表头
header=$(head -1 "$CSV_FILE")
IFS=',' read -ra columns <<< "$header"
col_count=${#columns[@]}

echo "**数据列 ($col_count列)**:"
echo ""

# 显示列，每行5个
for i in "${!columns[@]}"; do
    printf "%-3d. %-25s" $((i+1)) "${columns[$i]}"
    if [ $(( (i+1) % 5 )) -eq 0 ] || [ $((i+1)) -eq "$col_count" ]; then
        echo ""
    fi
done

echo ""
echo "**数据预览**:"
echo ""

# 显示数据
if command -v csvlook &> /dev/null; then
    # 使用csvlook格式化显示
    head -$((display_rows + 1)) "$CSV_FILE" | csvlook
else
    # 简单显示
    echo "行号 | 前5列数据"
    echo "-----|-------------------"
    
    # 显示前几行数据
    for i in $(seq 1 $display_rows); do
        line_num=$((i + 1))
        line=$(sed -n "${line_num}p" "$CSV_FILE")
        IFS=',' read -ra values <<< "$line"
        
        # 显示前5个值
        preview=""
        for j in {0..4}; do
            if [ $j -lt ${#values[@]} ]; then
                val="${values[$j]}"
                # 截断长值
                if [ ${#val} -gt 15 ]; then
                    val="${val:0:12}..."
                fi
                preview="$preview$val, "
            fi
        done
        preview="${preview%, }"
        
        printf "%-4d | %s\n" "$i" "$preview"
    done
fi

echo ""
echo "**关键数值统计** (基于前$display_rows行):"
echo ""

# 提取关键列并计算基本统计
key_columns=("pIC50" "QED" "LogP" "MW" "hERG_Prob")
for col_name in "${key_columns[@]}"; do
    # 查找列索引
    col_index=-1
    for i in "${!columns[@]}"; do
        if [ "${columns[$i]}" = "$col_name" ]; then
            col_index=$i
            break
        fi
    done
    
    if [ "$col_index" -ge 0 ]; then
        # 提取该列的数据
        values=()
        for i in $(seq 1 $display_rows); do
            line_num=$((i + 1))
            line=$(sed -n "${line_num}p" "$CSV_FILE")
            IFS=',' read -ra row_values <<< "$line"
            if [ $col_index -lt ${#row_values[@]} ]; then
                values+=("${row_values[$col_index]}")
            fi
        done
        
        # 计算基本统计
        if [ ${#values[@]} -gt 0 ]; then
            # 转换为数值并排序
            numeric_values=()
            for val in "${values[@]}"; do
                if [[ "$val" =~ ^-?[0-9]+\.?[0-9]*$ ]]; then
                    numeric_values+=("$val")
                fi
            done
            
            if [ ${#numeric_values[@]} -gt 0 ]; then
                # 排序
                sorted_values=($(printf "%s\n" "${numeric_values[@]}" | sort -n))
                
                min="${sorted_values[0]}"
                max="${sorted_values[-1]}"
                
                # 计算平均值
                sum=0
                count=0
                for val in "${numeric_values[@]}"; do
                    sum=$(echo "$sum + $val" | bc -l 2>/dev/null || echo "$sum")
                    count=$((count + 1))
                done
                
                if [ "$count" -gt 0 ]; then
                    avg=$(echo "scale=3; $sum / $count" | bc -l 2>/dev/null || echo "N/A")
                    
                    # 中位数
                    mid=$((count / 2))
                    if [ $((count % 2)) -eq 0 ]; then
                        median=$(echo "scale=3; (${sorted_values[$((mid-1))]} + ${sorted_values[$mid]}) / 2" | bc -l 2>/dev/null || echo "N/A")
                    else
                        median="${sorted_values[$mid]}"
                    fi
                    
                    echo "- **$col_name**: 平均=$avg, 中位数=$median, 范围=[$min, $max]"
                fi
            fi
        fi
    fi
done

echo ""
echo "## 💡 数据分析"
echo ""

# 简单分析
if [ -f "$CSV_FILE" ]; then
    # 检查高活性分子
    pIC50_index=-1
    for i in "${!columns[@]}"; do
        if [ "${columns[$i]}" = "pIC50" ]; then
            pIC50_index=$i
            break
        fi
    done
    
    if [ "$pIC50_index" -ge 0 ]; then
        high_activity_count=0
        total_count=0
        
        for i in $(seq 2 $((display_rows + 1))); do
            line=$(sed -n "${i}p" "$CSV_FILE")
            IFS=',' read -ra values <<< "$line"
            
            if [ $pIC50_index -lt ${#values[@]} ]; then
                pIC50_val="${values[$pIC50_index]}"
                total_count=$((total_count + 1))
                
                if (( $(echo "$pIC50_val > 7.0" | bc -l 2>/dev/null || echo "0") )); then
                    high_activity_count=$((high_activity_count + 1))
                fi
            fi
        done
        
        if [ "$total_count" -gt 0 ]; then
            pct=$((high_activity_count * 100 / total_count))
            echo "- **活性分析**: $high_activity_count/$total_count (${pct}%) 个分子 pIC50 > 7.0"
        fi
    fi
    
    # 检查药物相似性
    QED_index=-1
    for i in "${!columns[@]}"; do
        if [ "${columns[$i]}" = "QED" ]; then
            QED_index=$i
            break
        fi
    done
    
    if [ "$QED_index" -ge 0 ]; then
        good_qed_count=0
        total_count=0
        
        for i in $(seq 2 $((display_rows + 1))); do
            line=$(sed -n "${i}p" "$CSV_FILE")
            IFS=',' read -ra values <<< "$line"
            
            if [ $QED_index -lt ${#values[@]} ]; then
                QED_val="${values[$QED_index]}"
                total_count=$((total_count + 1))
                
                if (( $(echo "$QED_val > 0.6" | bc -l 2>/dev/null || echo "0") )); then
                    good_qed_count=$((good_qed_count + 1))
                fi
            fi
        done
        
        if [ "$total_count" -gt 0 ]; then
            pct=$((good_qed_count * 100 / total_count))
            echo "- **药物相似性**: $good_qed_count/$total_count (${pct}%) 个分子 QED > 0.6"
        fi
    fi
fi

echo ""
echo "## 🚀 下一步操作"
echo ""
echo "\`\`\`bash"
echo "# 查看完整数据源信息"
echo "bash scripts/demo_source_info.sh $SOURCE_NAME"
echo ""
echo "# 筛选高活性分子"
echo "bash scripts/demo_filter.sh $SOURCE_NAME pIC50 '>' 7.0"
echo ""
echo "# 查看其他数据源"
echo "bash scripts/demo_list_sources.sh"
echo "\`\`\`"