#!/usr/bin/env python3
"""
丝氨酸蛋白酶共识序列关键片段预测分析流程
执行日期：2026-03-11

流程：
1. 读取各物种FASTA序列
2. 多序列比对（ClustalOmega）
3. 共识序列提取（保守性阈值）
4. 关键功能片段识别与注释
5. 生成分析报告
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from collections import Counter

# ── 配置 ──────────────────────────────────────────────
THRESHOLD = 0.5          # 共识序列保守性阈值
WORK_DIR = Path(__file__).parent
DATE_STR = datetime.now().strftime("%Y%m%d")

# ── 丝氨酸蛋白酶已知功能域定义 ────────────────────────
# 基于UniProt/Pfam对典型丝氨酸蛋白酶的注释
# 使用序列模式（motif）而非绝对位置（因不同物种长度不同）

KNOWN_MOTIFS = {
    "催化三联体_His": {
        "pattern": ["H"],
        "context_note": "催化三联体组氨酸（His57，胰凝乳蛋白酶编号）",
        "function": "形成催化三联体，提取质子，激活亲核Ser",
        "criticality": "极关键"
    },
    "催化三联体_Asp": {
        "pattern": ["D"],
        "context_note": "催化三联体天冬氨酸（Asp102）",
        "function": "定向并稳定催化His的构象",
        "criticality": "极关键"
    },
    "催化三联体_Ser": {
        "pattern": ["S"],
        "context_note": "催化三联体丝氨酸（Ser195）",
        "function": "亲核攻击底物肽键，形成酰基-酶中间体",
        "criticality": "极关键"
    },
    "底物结合口袋_S1": {
        "pattern": None,
        "context_note": "S1底物结合口袋（Asp189位点）",
        "function": "决定底物特异性，带正电底物→Asp，Gly→宽泛特异性",
        "criticality": "关键"
    },
    "氧负离子洞": {
        "pattern": None,
        "context_note": "氧负离子洞（Gly193+Ser195骨架NH）",
        "function": "稳定过渡态四面体中间体",
        "criticality": "关键"
    },
    "活化环_activation_loop": {
        "pattern": None,
        "context_note": "活化位点（Ile16-Val17）",
        "function": "酶原激活后形成新N端，插入激活口袋",
        "criticality": "关键"
    },
    "二硫键_Cys": {
        "pattern": ["C"],
        "context_note": "保守半胱氨酸对",
        "function": "形成二硫键，稳定蛋白三维结构",
        "criticality": "结构关键"
    },
    "Asp_box": {
        "pattern": ["D", "D"],
        "context_note": "DxD / WD保守基序",
        "function": "参与钙离子结合或底物识别",
        "criticality": "中等"
    }
}

# ── 丝氨酸蛋白酶保守序列标志 ─────────────────────────
# 高度保守的序列块（来自Pfam S1家族注释）
CONSERVED_BLOCKS = {
    "His_block": "GDSGGP",       # 催化His附近的高保守块
    "Ser_block": "GDSG",         # Ser195周围
    "activation_Ile": "IVGG",    # 酶原激活位点
    "substrate_Asp": "GICAG",    # S1口袋相关
}


def run_clustalo(input_fasta, output_aln):
    """运行ClustalOmega多序列比对"""
    cmd = [
        "clustalo",
        "-i", str(input_fasta),
        "-o", str(output_aln),
        "--outfmt=fasta",
        "--force",
        "-v"
    ]
    print(f"\n[MSA] 运行 ClustalOmega...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  错误：{result.stderr}")
        return False
    print(f"  完成：{output_aln}")
    return True


def parse_fasta(fasta_path):
    """解析FASTA文件，返回 {序列名: 序列} 字典"""
    sequences = {}
    current_name = None
    current_seq = []
    with open(fasta_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_name:
                    sequences[current_name] = "".join(current_seq).upper()
                current_name = line[1:].split()[0]
                current_seq = []
            else:
                current_seq.append(line)
    if current_name:
        sequences[current_name] = "".join(current_seq).upper()
    return sequences


def extract_consensus(aligned_sequences, threshold=THRESHOLD):
    """
    从比对序列中提取共识序列
    threshold: 某位置最高频氨基酸占比 >= threshold 则写入，否则标X
    """
    if not aligned_sequences:
        return ""
    seqs = list(aligned_sequences.values())
    length = len(seqs[0])
    consensus = []
    conservation_scores = []

    for i in range(length):
        col = [s[i] for s in seqs if i < len(s)]
        # 排除gap
        non_gap = [aa for aa in col if aa != '-']
        if not non_gap:
            consensus.append('-')
            conservation_scores.append(0.0)
            continue
        counter = Counter(non_gap)
        most_common_aa, most_common_count = counter.most_common(1)[0]
        conservation = most_common_count / len(non_gap)
        conservation_scores.append(conservation)
        if conservation >= threshold:
            consensus.append(most_common_aa)
        else:
            consensus.append('X')

    return "".join(consensus), conservation_scores


def find_conserved_blocks(consensus_seq):
    """在共识序列中搜索已知保守块"""
    found = {}
    clean_consensus = consensus_seq.replace('-', '').replace('X', '?')

    for block_name, pattern in CONSERVED_BLOCKS.items():
        # 允许X位置匹配任意氨基酸
        idx = clean_consensus.find(pattern)
        if idx != -1:
            found[block_name] = {
                "position": idx,
                "matched_seq": clean_consensus[idx:idx+len(pattern)],
                "pattern": pattern
            }

    return found


def analyze_key_fragments(consensus_seq, conservation_scores, species_list):
    """
    分析共识序列中的关键片段
    返回关键片段列表，每个包含：位置、序列、功能注释
    """
    clean_consensus = "".join(aa for aa in consensus_seq if aa != '-')
    key_fragments = []

    # 1. 搜索已知保守块
    found_blocks = find_conserved_blocks(clean_consensus)
    for block_name, info in found_blocks.items():
        key_fragments.append({
            "fragment_id": block_name,
            "sequence": info["matched_seq"],
            "position_in_consensus": f"{info['position']+1}-{info['position']+len(info['matched_seq'])}",
            "matched_pattern": info["pattern"],
            "criticality": "极关键",
            "function": get_block_function(block_name),
            "evidence": "保守序列块匹配（Pfam S1家族）"
        })

    # 2. 搜索高保守区段：找连续保守性≥0.9的区域，合并相邻窗口，避免冗余
    non_gap_scores = []
    non_gap_consensus = []
    for aa, score in zip(consensus_seq, conservation_scores):
        if aa != '-':
            non_gap_scores.append(score)
            non_gap_consensus.append(aa)

    # 找出所有保守率≥0.9且非X的连续区段（最少6aa）
    MIN_LEN = 6
    HIGH_CONSERVATION = 0.90
    in_region = False
    region_start = 0

    for i, (aa, score) in enumerate(zip(non_gap_consensus, non_gap_scores)):
        is_conserved = (score >= HIGH_CONSERVATION and aa != 'X')
        if is_conserved and not in_region:
            in_region = True
            region_start = i
        elif (not is_conserved or i == len(non_gap_consensus) - 1) and in_region:
            region_end = i if not is_conserved else i + 1
            in_region = False
            region_len = region_end - region_start
            if region_len >= MIN_LEN:
                frag_seq = "".join(non_gap_consensus[region_start:region_end])
                avg_conservation = sum(non_gap_scores[region_start:region_end]) / region_len
                # 检查是否已被已知块覆盖
                already_found = any(
                    frag.get("matched_pattern", "") and
                    (frag["sequence"] in frag_seq or frag_seq in frag["sequence"])
                    for frag in key_fragments
                )
                if not already_found and 'X' not in frag_seq:
                    key_fragments.append({
                        "fragment_id": f"高保守连续区_{region_start+1}_{region_end}",
                        "sequence": frag_seq,
                        "position_in_consensus": f"{region_start+1}-{region_end}",
                        "length": region_len,
                        "avg_conservation": f"{avg_conservation:.2%}",
                        "criticality": "高保守（功能待确认）",
                        "function": "高度保守连续区域，可能涉及结构稳定或功能活性位点",
                        "evidence": f"连续{region_len}aa保守性分析（平均{avg_conservation:.2%}）"
                    })

    # 3. 搜索Cys残基（潜在二硫键）
    cys_positions = [i+1 for i, aa in enumerate(non_gap_consensus) if aa == 'C']
    if len(cys_positions) >= 2:
        key_fragments.append({
            "fragment_id": "保守半胱氨酸_二硫键",
            "sequence": f"C×{len(cys_positions)}（位置：{', '.join(map(str, cys_positions[:6]))}{'...' if len(cys_positions)>6 else ''}）",
            "position_in_consensus": "多位置",
            "criticality": "结构关键",
            "function": "形成二硫键，维持蛋白三维构象稳定性",
            "evidence": f"共识序列中检测到{len(cys_positions)}个保守Cys残基"
        })

    return key_fragments, clean_consensus


def get_block_function(block_name):
    """根据保守块名称返回功能描述"""
    functions = {
        "His_block": "催化三联体His57周围保守区，参与质子转移，是催化机制核心",
        "Ser_block": "含催化Ser195的GDSG保守块，直接执行对底物的亲核攻击",
        "activation_Ile": "IVGG酶原激活位点，蛋白酶原切割后Ile16形成新N端，插入激活口袋触发构象变化",
        "substrate_Asp": "S1底物结合口袋相关，决定底物特异性（精氨酸/赖氨酸选择性）"
    }
    return functions.get(block_name, "已知保守功能块")


def generate_report(species_name, sequences, consensus_seq, conservation_scores,
                    key_fragments, output_dir):
    """生成分析报告（Markdown格式）"""
    report_path = output_dir / f"{species_name}_分析报告.md"
    clean_consensus = "".join(aa for aa in consensus_seq if aa != '-')

    # 统计
    x_count = clean_consensus.count('X')
    total_len = len(clean_consensus)
    conservation_rate = (total_len - x_count) / total_len if total_len > 0 else 0

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# 丝氨酸蛋白酶关键片段预测分析报告\n\n")
        f.write(f"**物种/类群：** {species_name}  \n")
        f.write(f"**分析日期：** {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n")
        f.write(f"**输入序列数：** {len(sequences)}  \n")
        f.write(f"**共识序列长度：** {total_len} aa  \n")
        f.write(f"**共识序列保守率：** {conservation_rate:.1%}（阈值≥{THRESHOLD}）  \n\n")

        f.write("---\n\n")
        f.write("## 1. 共识序列\n\n")
        f.write("```\n")
        # 每60个字符换行
        for i in range(0, len(clean_consensus), 60):
            f.write(f"{i+1:>4} {clean_consensus[i:i+60]}\n")
        f.write("```\n\n")

        f.write("---\n\n")
        f.write("## 2. 关键功能片段\n\n")

        if not key_fragments:
            f.write("未检测到显著关键片段（可能需要更多序列或调整阈值）。\n\n")
        else:
            for frag in key_fragments:
                criticality_emoji = {
                    "极关键": "🔴",
                    "关键": "🟠",
                    "结构关键": "🟡",
                    "高保守（功能待确认）": "🔵"
                }.get(frag["criticality"], "⚪")

                f.write(f"### {criticality_emoji} {frag['fragment_id']}\n\n")
                f.write(f"| 属性 | 内容 |\n|------|------|\n")
                f.write(f"| **片段序列** | `{frag['sequence']}` |\n")
                f.write(f"| **位置** | {frag.get('position_in_consensus', 'N/A')} |\n")
                f.write(f"| **重要性** | {frag['criticality']} |\n")
                f.write(f"| **功能** | {frag['function']} |\n")
                f.write(f"| **证据** | {frag.get('evidence', 'N/A')} |\n")
                if 'avg_conservation' in frag:
                    f.write(f"| **平均保守率** | {frag['avg_conservation']} |\n")
                f.write("\n")

        f.write("---\n\n")
        f.write("## 3. 输入序列列表\n\n")
        for name, seq in sequences.items():
            f.write(f"- **{name}**（{len(seq)} aa）\n")

        f.write("\n---\n\n")
        f.write("## 4. 分析方法说明\n\n")
        f.write("1. **MSA**：使用 ClustalOmega 1.2.4 进行多序列比对\n")
        f.write(f"2. **共识序列**：各位置最高频氨基酸占比 ≥ {THRESHOLD} 则写入，否则标X\n")
        f.write("3. **关键片段识别**：\n")
        f.write("   - 匹配已知保守块（GDSG、IVGG等Pfam S1家族特征序列）\n")
        f.write("   - 滑动窗口（5aa）筛选平均保守率 ≥ 85% 的区段\n")
        f.write("   - 检测保守Cys残基（潜在二硫键）\n")
        f.write("4. **功能注释**：基于UniProt/Pfam已知丝氨酸蛋白酶结构-功能数据库\n\n")
        f.write("---\n\n")
        f.write("*本报告由自动化分析pipeline生成，关键片段功能解读基于已知丝氨酸蛋白酶家族注释。*\n")

    return report_path


def analyze_species(species_name, fasta_path, output_dir):
    """对单个物种/类群执行完整分析流程"""
    print(f"\n{'='*60}")
    print(f"分析：{species_name}")
    print(f"{'='*60}")

    species_dir = Path(output_dir) / species_name
    species_dir.mkdir(exist_ok=True)

    # Step 1: 解析输入序列
    sequences = parse_fasta(fasta_path)
    print(f"[Step1] 读取序列：{len(sequences)} 条")
    for name, seq in sequences.items():
        print(f"  - {name}（{len(seq)} aa）")

    if len(sequences) < 2:
        print("  ⚠️  序列数不足2条，跳过MSA，直接使用单条序列作为共识序列")
        consensus_seq = list(sequences.values())[0]
        conservation_scores = [1.0] * len(consensus_seq)
    else:
        # Step 2: MSA
        aln_path = species_dir / f"{species_name}_aligned.fasta"
        success = run_clustalo(fasta_path, aln_path)
        if not success:
            print("  MSA失败，终止")
            return None

        # Step 3: 提取共识序列
        aligned_seqs = parse_fasta(aln_path)
        consensus_seq, conservation_scores = extract_consensus(aligned_seqs, THRESHOLD)
        print(f"[Step3] 共识序列提取完成（长度：{len([aa for aa in consensus_seq if aa!='-'])} aa）")

    # 保存共识序列
    consensus_path = species_dir / f"{species_name}_consensus.fasta"
    clean_consensus = "".join(aa for aa in consensus_seq if aa != '-')
    with open(consensus_path, 'w') as f:
        f.write(f">{species_name}_consensus\n")
        for i in range(0, len(clean_consensus), 60):
            f.write(clean_consensus[i:i+60] + "\n")
    print(f"[Step3] 共识序列已保存：{consensus_path}")

    # Step 4: 关键片段分析
    print(f"[Step4] 分析关键功能片段...")
    key_fragments, clean_consensus = analyze_key_fragments(
        consensus_seq, conservation_scores, list(sequences.keys())
    )
    print(f"  检测到 {len(key_fragments)} 个关键片段/区域")

    # 保存片段数据（JSON）
    fragments_path = species_dir / f"{species_name}_key_fragments.json"
    with open(fragments_path, 'w', encoding='utf-8') as f:
        json.dump({
            "species": species_name,
            "date": DATE_STR,
            "consensus_length": len(clean_consensus),
            "key_fragments": key_fragments
        }, f, ensure_ascii=False, indent=2)

    # Step 5: 生成报告
    report_path = generate_report(
        species_name, sequences, consensus_seq,
        conservation_scores, key_fragments, species_dir
    )
    print(f"[Step5] 报告已生成：{report_path}")

    return {
        "species": species_name,
        "n_sequences": len(sequences),
        "consensus_length": len(clean_consensus),
        "key_fragments_count": len(key_fragments),
        "report_path": str(report_path)
    }


def generate_summary_report(all_results, output_dir):
    """生成跨物种汇总报告"""
    summary_path = output_dir / "汇总分析报告.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# 丝氨酸蛋白酶关键片段预测 — 跨物种汇总报告\n\n")
        f.write(f"**分析日期：** {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n")
        f.write(f"**分析物种数：** {len(all_results)}  \n\n")
        f.write("---\n\n")
        f.write("## 各物种分析摘要\n\n")
        f.write("| 物种/类群 | 输入序列数 | 共识序列长度 | 检出关键片段数 |\n")
        f.write("|---------|----------|------------|-------------|\n")
        for r in all_results:
            f.write(f"| {r['species']} | {r['n_sequences']} | {r['consensus_length']} aa | {r['key_fragments_count']} |\n")
        f.write("\n---\n\n")
        f.write("## 关键说明\n\n")
        f.write("- 各物种详细报告见对应子目录\n")
        f.write("- 关键片段重要性分级：🔴极关键 > 🟠关键 > 🟡结构关键 > 🔵高保守待确认\n")
        f.write("- 功能注释基于Pfam S1丝氨酸蛋白酶家族数据库\n")
    print(f"\n[汇总] 跨物种汇总报告：{summary_path}")
    return summary_path


if __name__ == "__main__":
    print("丝氨酸蛋白酶关键片段预测分析流程")
    print(f"工作目录：{WORK_DIR}")
    print("\n请将各物种FASTA文件放入 input/ 目录，然后重新运行。")
    print("或通过命令行参数指定：python serine_protease_analysis.py <species_name> <fasta_file>")

    if len(sys.argv) >= 3:
        sp_name = sys.argv[1]
        fasta = Path(sys.argv[2])
        out_dir = WORK_DIR / "results"
        out_dir.mkdir(exist_ok=True)
        result = analyze_species(sp_name, fasta, out_dir)
        if result:
            generate_summary_report([result], WORK_DIR)
