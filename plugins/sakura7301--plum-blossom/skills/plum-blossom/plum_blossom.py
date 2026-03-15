#!/usr/bin/env python3
"""MB"""
import datetime, time, json, os
from typing import Dict, Tuple

with open(os.path.join(os.path.dirname(__file__), 'data', 'yao_gua_data.json'), 'r') as f:
    _D = json.load(f)

GUA_SHENYUN_MAP = {int(k):v for k,v in _D['g'].items()}
yao_data = _D['y']
GUANAME = {k:v[0].split()[0] for k,v in GUA_SHENYUN_MAP.items()}

TRIGRAMS = {
    1:{"name":"乾","element":"金","symbol":"☰","lines":["yang","yang","yang"]},
    2:{"name":"兑","element":"金","symbol":"☱","lines":["yang","yang","yin"]},
    3:{"name":"离","element":"火","symbol":"☲","lines":["yang","yin","yang"]},
    4:{"name":"震","element":"木","symbol":"☳","lines":["yang","yin","yin"]},
    5:{"name":"巽","element":"木","symbol":"☴","lines":["yin","yang","yang"]},
    6:{"name":"坎","element":"水","symbol":"☵","lines":["yin","yang","yin"]},
    7:{"name":"艮","element":"土","symbol":"☶","lines":["yin","yin","yang"]},
    8:{"name":"坤","element":"土","symbol":"☷","lines":["yin","yin","yin"]},
}

GENERATING = {"金":"水","水":"木","木":"火","火":"土","土":"金"}
OVERCOMING = {"金":"木","木":"土","土":"水","水":"火","火":"金"}
MONTH_LUNAR = {1:"寅",2:"卯",3:"辰",4:"巳",5:"午",6:"未",7:"申",8:"酉",9:"戌",10:"亥",11:"子",12:"丑"}
WX_STRENGTH = {"金":{"旺":"申酉","相":"巳午","死":"寅卯","囚":"亥子","休":"辰戌丑未"},"木":{"旺":"寅卯","相":"亥子","死":"申酉","囚":"巳午","休":"辰戌丑未"},"水":{"旺":"亥子","相":"申酉","死":"巳午","囚":"寅卯","休":"辰戌丑未"},"火":{"旺":"巳午","相":"寅卯","死":"亥子","囚":"申酉","休":"辰戌丑未"},"土":{"旺":"辰戌丑未","相":"亥子","死":"寅卯","囚":"巳午","休":"申酉"}}

def get_gua_ci(u,l):
    return GUA_SHENYUN_MAP.get(u*10+l,["未知",""])[1]

def get_yao_ci(u,l,y):
    return yao_data.get(f"{u},{l},{y}",f"详见{u}卦{y}爻")

class PlumBlossom:
    def __init__(self): pass

    def _mod8(self, n):
        r = n % 8
        return r if r != 0 else 8

    def _mod6(self, n):
        r = n % 6
        return r if r != 0 else 6

    def _count_strokes(self, text: str) -> int:
        total = 0
        for char in text:
            total += STROKES.get(char, 5)
        return total

    def _get_hugua(self, upper: int, lower: int) -> Tuple[int, int]:
        lower_lines = TRIGRAMS[lower]['lines']
        upper_lines = TRIGRAMS[upper]['lines']
        bengua_lines = lower_lines + upper_lines

        hugua_lines = bengua_lines[1:5]
        hugua_lower = hugua_lines[:3]
        hugua_upper = hugua_lines[1:4]

        def find_trigram(lines):
            for num, tri in TRIGRAMS.items():
                if tri['lines'] == lines:
                    return num
            return 1

        hu_upper = find_trigram(hugua_upper)
        hu_lower = find_trigram(hugua_lower)
        return hu_upper, hu_lower

    def _get_biangua(self, upper: int, lower: int, mv: int) -> Tuple[int, int]:
        lower_lines = TRIGRAMS[lower]['lines']
        upper_lines = TRIGRAMS[upper]['lines']
        bengua_lines = lower_lines + upper_lines
        idx = mv - 1
        bian_gua_lines = bengua_lines.copy()
        bian_gua_lines[idx] = 'yang' if bian_gua_lines[idx] == 'yin' else 'yin'

        bian_lower_lines = bian_gua_lines[:3]

        bian_upper_lines = bian_gua_lines[3:]

        def find_trigram(lines):
            for num, tri in TRIGRAMS.items():
                if tri['lines'] == lines:
                    return num
            return 1

        bian_upper = find_trigram(bian_upper_lines)
        bian_lower = find_trigram(bian_lower_lines)
        return bian_upper, bian_lower

    def _wuxing_relation(self, body_elem: str, use_elem: str) -> Tuple[str, str]:
        if OVERCOMING.get(body_elem) == use_elem:
            return '用克体', '凶'
        if GENERATING.get(use_elem) == body_elem:
            return '用生体', '吉'
        if GENERATING.get(body_elem) == use_elem:
            return '体生用', '耗'
        if body_elem == use_elem:
            return '体用比和', '吉'
        return '体克用', '吉'

    def _get_month_strength(self, element: str, month: int) -> str:
        lunar_month = MONTH_LUNAR.get(month, '子')
        return WX_STRENGTH.get(lunar_month, {}).get(element, '平')

    def _get_ganzhi(self, year: int, month: int, day: int, hour: int) -> Dict:
        gan = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
        zhi = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
        year_g = gan[(year - 4) % 10]
        year_z = zhi[(year - 4) % 12]
        month_g = gan[(year * 2 + month + 2) % 10]
        month_z = zhi[(month + 1) % 12]
        day_num = (year-2000)*365 + month*30 + day
        day_g = gan[(day_num + 6) % 10]
        day_z = zhi[(day_num + 4) % 12]
        hour_g = gan[(day_num * 2 + hour + 2) % 10]
        hour_z = zhi[hour % 12]
        return {'year': year_g+year_z, 'month': month_g+month_z, 'day': day_g+day_z, 'hour': hour_g+hour_z}

    def time_divination(self, year: int, month: int, day: int, hour: int) -> Dict:
        upper = self._mod8(year + month + day)
        lower = self._mod8(year + month + day + hour)
        mv = self._mod6(year + month + day + hour)
        return self._build_result(upper, lower, mv, f"时间起卦：{year}年{month}月{day}日{hour}时", month, year, month, day, hour)

    def number_divination(self, num1: int, num2: int, month: int = None) -> Dict:
        upper = self._mod8(num1)
        lower = self._mod8(num2)
        mv = self._mod6(int(time.time()) % 6 + 1)
        if month is None: month = datetime.datetime.now().month
        now = datetime.datetime.now()
        return self._build_result(upper, lower, mv, f"数字起卦：{num1}, {num2}", month, now.year, now.month, now.day, now.hour)

    def text_divination(self, text: str, month: int = None) -> Dict:
        total = self._count_strokes(text)
        upper = self._mod8(total)
        lower = self._mod8(total + 1)
        mv = self._mod6(int(time.time()) % 6 + 1)
        if month is None: month = datetime.datetime.now().month
        now = datetime.datetime.now()
        info = f"汉字起卦：「{text}」笔画数={total}"
        return self._build_result(upper, lower, mv, info, month, now.year, now.month, now.day, now.hour)

    def _build_result(self, upper: int, lower: int, mv: int, info: str, month: int, year: int, month2: int, day: int, hour: int) -> Dict:
        ben_upper = TRIGRAMS[upper]
        ben_lower = TRIGRAMS[lower]
        hu_upper, hu_lower = self._get_hugua(upper, lower)
        bian_upper, bian_lower = self._get_biangua(upper, lower, mv)

        if mv <= 3:
            body_elem = ben_upper['element']
            use_elem = ben_lower['element']
            body_gua_name = ben_upper['name']
            use_gua_name = ben_lower['name']
        else:
            body_elem = ben_lower['element']
            use_elem = ben_upper['element']
            body_gua_name = ben_lower['name']
            use_gua_name = ben_upper['name']

        relation, fortune = self._wuxing_relation(body_elem, use_elem)

        body_strength = self._get_month_strength(body_elem, month)
        use_strength = self._get_month_strength(use_elem, month)
        ganzhi = self._get_ganzhi(year, month2, day, hour)

        hour_num = (hour + 1) % 12 + 1
        if hour_num > 12:
            hour_num = hour_num - 12
        zhi_num = {'子':1, '丑':2, '寅':3, '卯':4, '辰':5, '巳':6, '午':7, '未':8, '申':9, '酉':10, '戌':11, '亥':12}
        hour_zhi = ganzhi['hour'][-1]
        hour_num = zhi_num.get(hour_zhi, hour + 1)
        yingqi = upper + lower + hour_num

        return {
            'info': info, 'month': month, 'year': year, 'month2': month2, 'day': day, 'hour': hour,
            'ben': {'upper': ben_upper, 'lower': ben_lower, 'mv': mv, 'gua': (upper, lower)},
            'hu': {'upper': TRIGRAMS[hu_upper], 'lower': TRIGRAMS[hu_lower], 'gua': (hu_upper, hu_lower)},
            'bian': {'upper': TRIGRAMS[bian_upper], 'lower': TRIGRAMS[bian_lower], 'gua': (bian_upper, bian_lower)},
            'body_elem': body_elem, 'use_elem': use_elem, 'relation': relation, 'fortune': fortune,
            'body_strength': body_strength, 'use_strength': use_strength, 'ganzhi': ganzhi,
            'yingqi': yingqi, 'upper': upper, 'lower': lower, 'hour_num': hour_num,
            'body_gua_name': body_gua_name, 'use_gua_name': use_gua_name,
        }


    def format_output(self, result: Dict, question: str = "") -> str:
        lines = []
        gz = result['ganzhi']
        lines.append(f"{gz['year']}年 {gz['month']}月 {gz['day']}日 {gz['hour']}时")
        month_lunar = ['寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑'][result['month']-1]
        wx_strength = {'木':'', '火':'', '土':'', '金':'', '水':''}
        strength_map = {'旺':'旺', '相':'相', '生':'相', '死':'死', '囚':'囚', '休':'休'}
        for elem in wx_strength:
            wx_strength[elem] = strength_map.get(WX_STRENGTH.get(month_lunar, {}).get(elem, ''), '')
        wx_list = [f"{e}{s}" for e,s in wx_strength.items() if s]
        lines.append('，'.join(wx_list))
        b = result['ben']
        bagua_name = {'乾':'天','兑':'泽','离':'火','震':'雷','巽':'风','坎':'水','艮':'山','坤':'地'}
        upper_char = b['upper']['name']
        lower_char = b['lower']['name']
        trigram_to_num = {v['name']: k for k, v in TRIGRAMS.items()}
        upper = trigram_to_num.get(upper_char, 1)
        lower = trigram_to_num.get(lower_char, 1)
        gua_idx = (upper, lower)
        gua_full_name = GUANAME.get(gua_idx, f"{upper_char}{lower_char}")
        simple_name = bagua_name.get(upper_char, upper_char) + bagua_name.get(lower_char, lower_char)
        ben_gua_name = f"{upper_char}{lower_char}"
        cip = get_gua_ci(upper, lower)
        gua_symbol = GUA_SHENYUN_MAP.get((upper, lower), ["", ""])[0].split()[0] if GUA_SHENYUN_MAP.get((upper, lower)) else "䷫"
        lines.append(f"【主卦】{gua_symbol} {gua_full_name}({ben_gua_name})({result['relation']})")
        lines.append(f"        卦辞「{cip}」")
        h = result['hu']
        hu_upper_name = h['upper']['name']
        hu_lower_name = h['lower']['name']
        hu_upper_num = trigram_to_num.get(hu_upper_name, 1)
        hu_lower_num = trigram_to_num.get(hu_lower_name, 1)
        hu_idx = (hu_upper_num, hu_lower_num)
        hu_full_name = GUANAME.get(hu_idx, f"{hu_upper_name}{hu_lower_name}")
        hu_symbol = GUA_SHENYUN_MAP.get(hu_idx, ["", ""])[0].split()[0] if GUA_SHENYUN_MAP.get(hu_idx) else "䷀"
        lines.append(f"【互卦】{hu_symbol} {hu_full_name}")
        bi = result['bian']
        bian_upper_name = bi['upper']['name']
        bian_lower_name = bi['lower']['name']
        bian_upper_num = trigram_to_num.get(bian_upper_name, 1)
        bian_lower_num = trigram_to_num.get(bian_lower_name, 1)
        bian_idx = (bian_upper_num, bian_lower_num)
        bian_full_name = GUANAME.get(bian_idx, f"{bian_upper_name}{bian_lower_name}")
        bian_cip = get_gua_ci(bian_upper_num, bian_lower_num)
        bian_body = bi['upper']['element']
        bian_use = bi['lower']['element']
        bian_rel, _ = self._wuxing_relation(bian_body, bian_use)
        bian_symbol = GUA_SHENYUN_MAP.get(bian_idx, ["", ""])[0].split()[0] if GUA_SHENYUN_MAP.get(bian_idx) else "䷀"
        lines.append(f"【变卦】{bian_symbol} {bian_full_name}({bian_rel})")
        lines.append(f"        卦辞「{bian_cip}」")

        yao_names = ["初", "二", "三", "四", "五", "六"]
        yao_idx = b['mv']
        yao_ci = get_yao_ci(upper, lower, yao_idx)
        lines.append(f"【动爻】{yao_names[yao_idx-1]}爻动")
        lines.append(f"  「{yao_ci}」")

        lines.append("")
        lines.append("-" * 40)
        lines.append("【体用生克】")
        lines.append(f"  体卦：{result.get('body_gua_name', b['upper']['name'])} ({result['body_elem']})")
        lines.append(f"  用卦：{result.get('use_gua_name', b['lower']['name'])} ({result['use_elem']})")
        lines.append(f"  关系：{result['relation']} → {result['fortune']}")

        lines.append("")
        lines.append("【五行旺衰】")
        month_lunar = ['寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑'][result['month']-1]
        month_wx = WX_STRENGTH.get(month_lunar, {})
        strength_map = {'旺':'旺', '相':'相', '生':'相', '死':'死', '囚':'囚', '休':'休'}
        body_wx = strength_map.get(month_wx.get(result['body_elem'], ''), '平')
        use_wx = strength_map.get(month_wx.get(result['use_elem'], ''), '平')
        lines.append(f"  体卦 {result['body_elem']}：{body_wx}")
        lines.append(f"  用卦 {result['use_elem']}：{use_wx}")

        # 断语
        lines.append("")
        lines.append("-" * 40)
        if result['fortune'] == '吉':
            lines.append("✓ 此卦主吉")
        elif result['fortune'] == '凶':
            lines.append("✗ 此卦主凶")
        else:
            lines.append("○ 此卦平和")

        return "\n".join(lines)

if __name__ == '__main__':
    import sys
    pb = PlumBlossom()
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        if cmd == 'time':
            now = datetime.datetime.now()
            result = pb.time_divination(now.year, now.month, now.day, now.hour)
            print(pb.format_output(result, ""))
        elif cmd == 'text' and len(sys.argv) >= 3:
            result = pb.text_divination(sys.argv[2])
            print(pb.format_output(result, ""))
        elif cmd == 'num' and len(sys.argv) >= 4:
            result = pb.number_divination(int(sys.argv[2]), int(sys.argv[3]))
            print(pb.format_output(result, ""))
    else:
        now = datetime.datetime.now()
        result = pb.time_divination(now.year, now.month, now.day, now.hour)
        print(pb.format_output(result, ""))
