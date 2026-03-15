#!/usr/bin/env python3
"""
OpenClaw HLA OCR Skill - Final v3.1 (Dense format robustness)
"""

import sys, os, json, easyocr, cv2

def clean_allele(a):
    a = a.strip()
    if not a or a == '-': return '-'
    a = a.replace(';', ':').replace('016', '01G')
    if '.' in a and ':' not in a:
        p = a.split('.')
        if len(p) == 2 and all(x.isdigit() for x in p):
            a = f"{p[0]}:{p[1]}"
    return a if ':' in a else '-'

def reconstruct_rows(results, img_h):
    y_centers, cells = [], []
    for bbox, text, conf in results:
        y = sum(p[1] for p in bbox)/4
        x = sum(p[0] for p in bbox)/4
        y_centers.append(y)
        cells.append({'text': text.strip(), 'y': y, 'x': x})
    if img_h:
        thr = img_h * 0.02
        ys = sorted(set(y_centers))
        clusters, cur = [], [ys[0]]
        for y in ys[1:]:
            if y - cur[-1] <= thr:
                cur.append(y)
            else:
                clusters.append(int(sum(cur)/len(cur)))
                cur = [y]
        if cur: clusters.append(int(sum(cur)/len(cur)))
        clusters.sort()
    else:
        clusters = sorted(set(y_centers))
    rows = [[] for _ in range(len(clusters))]
    for c in cells:
        idx = min(range(len(clusters)), key=lambda i: abs(clusters[i]-c['y']))
        rows[idx].append(c)
    for r in rows:
        r.sort(key=lambda c: c['x'])
    return [[c['text'] for c in r] for r in rows]

# ---------- Dense Format (2 alleles per locus in one row) ----------
def parse_dense_format(rows):
    loci = ['HLA-A','HLA-B','HLA-C','HLA-DRB1','HLA-DQB1','HLA-DPB1']
    samples = []
    # Find header row
    header_idx = -1
    for i, r in enumerate(rows):
        header = [c.upper() for c in r]
        if any('HLA-A' in c for c in header) and any('HLA-B' in c for c in header):
            header_idx = i
            break
    if header_idx == -1:
        return samples
    i = header_idx + 1
    while i < len(rows):
        row = rows[i]
        if not row or len(row) < 7:
            i += 1
            continue
        # Skip footer/match annotation rows (e.g., Matchos, Mlatchos, Watchos)
        skip_keywords = {'Matchos', 'Mlatchos', 'Watchos', 'Matching', 'match'}
        if row[0].strip() in skip_keywords:
            i += 1
            continue
        # Name is first cell
        name = row[0].strip()
        # Collect allele-like tokens (contain ':' or ';') from the rest of the row
        allele_tokens = [c for c in row[1:] if ':' in c or ';' in c]
        if len(allele_tokens) < 6:
            i += 1
            continue
        # Ensure we have exactly 12 allele tokens (6 pairs). Pad or truncate.
        if len(allele_tokens) >= 12:
            vals = allele_tokens[:12]
        else:
            vals = allele_tokens + ['-'] * (12 - len(allele_tokens))
        a1 = [vals[j] for j in range(0, 12, 2)]
        a2 = [vals[j] for j in range(1, 12, 2)]
        a1 = [clean_allele(c) for c in a1]
        a2 = [clean_allele(c) for c in a2]
        als = {}
        for j, L in enumerate(loci):
            c1, c2 = a1[j], a2[j]
            als[L] = f"{c1}/{c2}" if c1 != '-' or c2 != '-' else '-'
        samples.append({
            'id': '-',
            'name': name,
            'gender': '-',
            'age': '-',
            'relation': '-',
            'type': '-',
            'alleles': als
        })
        i += 1
    return samples

# ---------- Format A: meta row contains role+ID ----------
def parse_meta_format(rows):
    loci = ['HLA-A','HLA-B','HLA-C','HLA-DRB1','HLA-DQB1','HLA-DPB1']
    samples = []
    i = 0
    while i < len(rows):
        row = rows[i]
        row_str = ''.join(row)
        has_role = any(r in row_str for r in ['患者','供者'])
        has_id = any(('8204-' in c or '8304-' in c or '8316-' in c or (c.startswith('82') and '-' in c and len(c)>5)) for c in row)
        if not (has_role and has_id):
            i += 1
            continue
        # sample ID
        sample_id = '-'
        for cell in row:
            if any(p in cell for p in ['8204-','8304-','8316-']) or (cell.startswith('82') and '-' in cell and len(cell)>5):
                sample_id = cell
                break
        # name, gender, age
        name, gender, age = '-', '-', '-'
        for cell in row:
            if '^' in cell:
                parts = [p.strip() for p in cell.split('^')]
                for p in parts:
                    if p and 2 <= len(p) <= 4 and all('\u4e00' <= ch <= '\u9fff' for ch in p) and p not in {'患者','供者','全血','血','样本'}:
                        name = p
                        break
                if name != '-':
                    break
        if name == '-':
            exclude = {'患者','供者','全血','类型','的关系','编号','姓名','性别','年龄'}
            for cell in row:
                cell_clean = cell.strip()
                if cell_clean and any('\u4e00' <= ch <= '\u9fff' for ch in cell_clean) and cell_clean not in exclude:
                    name = cell_clean
                    break
        if gender == '-' or age == '-':
            for idx, cell in enumerate(row):
                if cell == name:
                    for offset in (1,2):
                        if idx+offset < len(row):
                            nc = row[idx+offset]
                            if '男' in nc or '女' in nc:
                                gender = nc
                            if nc.isdigit() and 10 <= int(nc) <= 100:
                                age = nc
                    break
        # relation
        relation = '-'
        for cell in row:
            if any(k in cell for k in ['患者','弟弟','堂弟','外甥','妹妹','姐姐']):
                relation = cell
                break
        # Collect HLA candidate rows
        hla_rows = []
        for idx, r in enumerate(rows):
            if len(r) >= 6 and all(':' in c or ';' in c for c in r[:6]):
                hla_rows.append((idx, r[:6]))
        a1, a2 = [], []
        meta_idx = i
        if len(row) >= 12:
            a1 = row[-6:]
            for idx, cand in hla_rows:
                if idx > meta_idx:
                    a2 = cand
                    i = idx
                    break
        else:
            after = [cand for idx, cand in hla_rows if idx > meta_idx]
            before = [cand for idx, cand in hla_rows if idx < meta_idx]
            if len(after) >= 2:
                a1, a2 = after[0], after[1]
                i += 2
            elif len(after) == 1:
                if before:
                    a1 = before[-1]
                    a2 = after[0]
                    i += 1
                else:
                    a1 = after[0]
                    a2 = []
                    i += 1
            else:
                if before:
                    a1 = before[-1]
                    a2 = []
                else:
                    a1 = a2 = []
        a1 = (a1 + ['-']*6)[:6]
        a2 = (a2 + ['-']*6)[:6]
        als = {}
        for j, L in enumerate(loci):
            c1, c2 = clean_allele(a1[j]), clean_allele(a2[j])
            als[L] = f"{c1}/{c2}" if c1 != '-' or c2 != '-' else '-'
        samples.append({
            'id': sample_id,
            'name': name,
            'gender': gender,
            'age': age,
            'relation': relation,
            'type': '-',
            'alleles': als
        })
        i += 1
    return samples

# ---------- Format B: Name row + ID row + gender/age row ----------
def parse_second_format(rows):
    loci = ['HLA-A','HLA-B','HLA-C','HLA-DRB1','HLA-DQB1','HLA-DPB1']
    samples = []
    i = 0
    while i < len(rows):
        row_str = ' '.join(rows[i])
        if any(label in row_str for label in ['性别','年龄','关系','A*','B*','DRB1','样本绵号']):
            i += 1
        else:
            break
    while i < len(rows):
        row = rows[i]
        if len(row) >= 7 and any('\u4e00' <= c <= '\u9fff' for c in row[0]):
            name = row[0]
            alleles_row = row[1:7]
            sample_id = "-"
            if i + 1 < len(rows):
                nr = rows[i + 1]
                if nr and (nr[0].startswith('2025') or (nr[0].isdigit() and len(nr[0]) > 8)):
                    sample_id = nr[0]
                    i += 1
            gender, age = "-", "-"
            if i + 1 < len(rows):
                mr = rows[i + 1]
                for cell in mr[:3]:
                    if '男' in cell or '女' in cell:
                        gender = cell
                    if '岁' in cell:
                        age = cell.replace('岁', '')
                    elif cell.isdigit() and 10 <= int(cell) <= 100:
                        age = cell
                i += 1
            alleles_clean = [clean_allele(a) for a in alleles_row]
            alleles = {loci[j]: alleles_clean[j] for j in range(6)}
            samples.append({
                'id': sample_id,
                'name': name,
                'gender': gender,
                'age': age,
                'relation': '-',
                'type': '-',
                'alleles': alleles
            })
        i += 1
    return samples

# ---------- Main Dispatcher ----------
def parse_hla(rows):
    # Detect dense format by looking for header with HLA loci and data rows with many colon tokens
    is_dense = False
    for i, r in enumerate(rows):
        header = [c.upper() for c in r]
        if any('HLA-A' in c for c in header) and any('HLA-B' in c for c in header):
            # Check following rows for dense pattern
            for dr in rows[i+1:]:
                if len(dr) >= 7:
                    colon_count = sum(1 for c in dr if ':' in c or ';' in c)
                    if colon_count >= 12:
                        is_dense = True
                        break
            break
    if is_dense:
        return parse_dense_format(rows)
    # Check for meta format
    has_meta = False
    for row in rows:
        row_str = ''.join(row)
        if any(r in row_str for r in ['患者','供者']):
            if any(('8204-' in c or '8304-' in c or '8316-' in c or (c.startswith('82') and '-' in c and len(c)>5)) for c in row):
                has_meta = True
                break
    if has_meta:
        return parse_meta_format(rows)
    else:
        return parse_second_format(rows)

def run_hla_ocr(image_path):
    if not os.path.exists(image_path):
        return json.dumps({"error": f"Image not found: {image_path}"}, ensure_ascii=False)
    try:
        reader = easyocr.Reader(['ch_sim','en'], gpu=False, verbose=False)
        results = reader.readtext(image_path, detail=1, paragraph=False)
        if not results:
            return json.dumps({"error":"No text detected"}, ensure_ascii=False)
        img = cv2.imread(image_path)
        img_h = img.shape[0] if img is not None else None
        rows = reconstruct_rows(results, img_h)
        samples = parse_hla(rows)
        return json.dumps({"status":"success","image":os.path.basename(image_path),"samples":samples}, ensure_ascii=False, indent=2)
    except Exception as e:
        import traceback
        return json.dumps({"error":str(e), "traceback":traceback.format_exc()}, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: hla_ocr.py <image_path>", file=sys.stderr)
        sys.exit(1)
    print(run_hla_ocr(sys.argv[1]))
    sys.exit(0)
