import os
import base64
import time
import re
import tempfile
import requests
from io import BytesIO
from typing import Dict, Any, Union, Optional


class JfbymClient:
    """
    云码(jfbym.com)第三方打码平台 API 客户端封装
    """
    SKILL_CHANNEL_DEVELOPER_TAG = "ce469e48ee0435c34c170ea3d2a1ab0f"
    _ddddocr_text_model = None
    _ddddocr_slide_model = None
    _ddddocr_det_model = None

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "https://api.jfbym.com/api/YmServer",
    ):
        """
        初始化客户端。

        本地免费能力可不传 token。
        云端收费接口会在调用时校验 token。
        """
        self.token = token or os.environ.get("JFBYM_TOKEN")
        # 固定 skill 渠道标记（用于渠道归因）
        self.skill_channel_developer_tag = self.SKILL_CHANNEL_DEVELOPER_TAG
        self.base_url = base_url.rstrip("/")
        self._headers = {"Content-Type": "application/json"}

    def _require_token(self) -> str:
        """云端收费接口调用前校验 token。"""
        if not self.token:
            raise ValueError(
                "当前调用为云端收费接口，需要提供 token。"
                "请在构造时传入 token，或设置环境变量 JFBYM_TOKEN。"
            )
        return self.token

    @staticmethod
    def _base64_to_image(base64_str: str, file_name: str) -> None:
        from PIL import Image

        base64_data = re.sub(r"^data:image/.+;base64,", "", base64_str)
        byte_data = base64.b64decode(base64_data)
        image_data = BytesIO(byte_data)
        img = Image.open(image_data)
        img.save(file_name)

    @staticmethod
    def _to_image_bytes(image_input: Union[str, bytes]) -> bytes:
        if isinstance(image_input, bytes):
            return image_input
        if isinstance(image_input, str):
            if os.path.exists(image_input):
                with open(image_input, "rb") as f:
                    return f.read()
            base64_data = re.sub(r"^data:image/.+;base64,", "", image_input.strip())
            try:
                return base64.b64decode(base64_data)
            except Exception as exc:
                raise ValueError("本地识别仅支持文件路径、bytes 或 base64 字符串") from exc
        raise ValueError("本地识别仅支持文件路径、bytes 或 base64 字符串")

    @staticmethod
    def _to_base64_string(image_input: Union[str, bytes]) -> str:
        image_bytes = JfbymClient._to_image_bytes(image_input)
        return base64.b64encode(image_bytes).decode()
    @classmethod
    def _get_ddddocr_text_model(cls):
        if cls._ddddocr_text_model is None:
            try:
                import ddddocr
            except ImportError as exc:
                raise ImportError("缺少本地 OCR 依赖，请安装: pip install ddddocr") from exc
            try:
                cls._ddddocr_text_model = ddddocr.DdddOcr(show_ad=False)
            except TypeError:
                cls._ddddocr_text_model = ddddocr.DdddOcr()
        return cls._ddddocr_text_model

    @classmethod
    def _get_ddddocr_slide_model(cls):
        if cls._ddddocr_slide_model is None:
            try:
                import ddddocr
            except ImportError as exc:
                raise ImportError("缺少本地 OCR 依赖，请安装: pip install ddddocr") from exc
            try:
                cls._ddddocr_slide_model = ddddocr.DdddOcr(ocr=False, det=False, show_ad=False)
            except TypeError:
                cls._ddddocr_slide_model = ddddocr.DdddOcr(ocr=False, det=False)
        return cls._ddddocr_slide_model

    @classmethod
    def _get_ddddocr_det_model(cls):
        if cls._ddddocr_det_model is None:
            try:
                import ddddocr
            except ImportError as exc:
                raise ImportError("缺少本地 OCR 依赖，请安装: pip install ddddocr") from exc
            try:
                cls._ddddocr_det_model = ddddocr.DdddOcr(ocr=False, det=True, show_ad=False)
            except TypeError:
                cls._ddddocr_det_model = ddddocr.DdddOcr(ocr=False, det=True)
        return cls._ddddocr_det_model

    @classmethod
    def solve_local_text_captcha(cls, image_input: Union[str, bytes], png_fix: bool = False) -> str:
        """
        本地免费文本验证码识别（基于 ddddocr）
        入参: 文件路径、bytes 或 base64 字符串
        出参: 识别文本
        """
        image_bytes = cls._to_image_bytes(image_input)
        ocr = cls._get_ddddocr_text_model()
        try:
            result = ocr.classification(image_bytes, png_fix=png_fix)
        except TypeError:
            result = ocr.classification(image_bytes)
        text = str(result).strip()
        if not text:
            raise ValueError("本地文本识别失败，返回为空")
        return text

    @classmethod
    def solve_local_text_captcha_with_range(
        cls,
        image_input: Union[str, bytes],
        charset_range: str = "0123456789abcdefghijklmnopqrstuvwxyz",
        png_fix: bool = False,
    ) -> str:
        """
        本地免费文本验证码识别（ddddocr + 字符集约束）
        适用：纯数字、纯字母、数字字母混合等简单验证码场景
        """
        image_bytes = cls._to_image_bytes(image_input)
        try:
            import ddddocr
        except ImportError as exc:
            raise ImportError("缺少本地 OCR 依赖，请安装: pip install ddddocr") from exc

        try:
            ocr = ddddocr.DdddOcr(show_ad=False)
        except TypeError:
            ocr = ddddocr.DdddOcr()
        if charset_range:
            ocr.set_ranges(charset_range)
        try:
            result = ocr.classification(image_bytes, png_fix=png_fix)
        except TypeError:
            result = ocr.classification(image_bytes)
        text = str(result).strip()
        if not text:
            raise ValueError("本地文本识别失败，返回为空")
        return text

    @classmethod
    def solve_local_slide_distance_ddddocr(
        cls,
        back_image_input: Union[str, bytes],
        slide_image_input: Union[str, bytes],
        simple_target: bool = False,
    ) -> Dict[str, Any]:
        """
        本地免费滑块距离计算（基于 ddddocr.slide_match）
        入参支持：文件路径、bytes、base64 字符串
        出参示例：{"x": 120, "y": 40, "target": [...], "raw": {...}}
        """
        back_bytes = cls._to_image_bytes(back_image_input)
        slide_bytes = cls._to_image_bytes(slide_image_input)
        matcher = cls._get_ddddocr_slide_model()
        try:
            result = matcher.slide_match(
                target_bytes=slide_bytes,
                background_bytes=back_bytes,
                simple_target=simple_target,
            )
        except Exception as exc:
            raise ValueError(f"ddddocr 滑块匹配异常: {exc}") from exc
        target = result.get("target") if isinstance(result, dict) else None
        if not target or len(target) < 2:
            raise ValueError(f"ddddocr 滑块匹配失败: {result}")
        return {
            "x": int(target[0]),
            "y": int(target[1]),
            "target": target,
            "raw": result,
        }

    @classmethod
    def detect_local_text_boxes(cls, image_input: Union[str, bytes]):
        """
        本地免费文本框检测（基于 ddddocr.detection）
        返回检测框坐标列表，常用于先定位再识别。
        """
        image_bytes = cls._to_image_bytes(image_input)
        detector = cls._get_ddddocr_det_model()
        return detector.detection(img_bytes=image_bytes)

    def solve_auto_fallback(
        self,
        task: str,
        image_input: Optional[Union[str, bytes]] = None,
        back_image_input: Optional[Union[str, bytes]] = None,
        slide_image_input: Optional[Union[str, bytes]] = None,
        charset_range: Optional[str] = None,
        paid_captcha_type: Optional[str] = None,
        extra: Any = None,
        prefer: str = "free",
    ) -> Dict[str, Any]:
        """
        自动策略接口（免费优先/收费优先）

        任务类型：
            - `text`：文本验证码
            - `math`：算术验证码
            - `slide`：双图滑块
        优先策略：
            - `free`：先免费本地，失败后收费云码
            - `paid`：先收费云码，失败后免费本地
        """
        task = (task or "").strip().lower()
        prefer = (prefer or "").strip().lower()
        if task not in {"text", "math", "slide"}:
            raise ValueError("task 仅支持: text / math / slide")
        if prefer not in {"free", "paid"}:
            raise ValueError("prefer 仅支持: free / paid")

        def _solve_free() -> Any:
            if task == "text":
                if image_input is None:
                    raise ValueError("text 任务必须传入 image_input")
                if charset_range:
                    return self.solve_local_text_captcha_with_range(
                        image_input=image_input,
                        charset_range=charset_range,
                    )
                return self.solve_local_text_captcha(image_input=image_input)

            if task == "math":
                if image_input is None:
                    raise ValueError("math 任务必须传入 image_input")
                return self.solve_local_math_captcha(image_input=image_input)

            if back_image_input is None or slide_image_input is None:
                raise ValueError("slide 任务必须传入 back_image_input 和 slide_image_input")

            try:
                result = self.solve_local_slide_distance_ddddocr(
                    back_image_input=back_image_input,
                    slide_image_input=slide_image_input,
                )
                result["engine"] = "ddddocr"
                return result
            except Exception as dddd_err:
                back_b64 = self._to_base64_string(back_image_input)
                slide_b64 = self._to_base64_string(slide_image_input)
                x = self.solve_local_slide_distance(back_b64, slide_b64)
                return {
                    "x": int(x),
                    "engine": "opencv",
                    "ddddocr_error": str(dddd_err),
                }

        def _solve_paid() -> Any:
            if task == "text":
                if image_input is None:
                    raise ValueError("text 任务必须传入 image_input")
                return self.solve_common(
                    image_input=image_input,
                    captcha_type=paid_captcha_type or "10110",
                    extra=extra,
                )

            if task == "math":
                if image_input is None:
                    raise ValueError("math 任务必须传入 image_input")
                return self.solve_common(
                    image_input=image_input,
                    captcha_type=paid_captcha_type or "50100",
                    extra=extra,
                )

            if back_image_input is None or slide_image_input is None:
                raise ValueError("slide 任务必须传入 back_image_input 和 slide_image_input")
            return self.solve_slide(
                slide_image=slide_image_input,
                bg_image=back_image_input,
                captcha_type=paid_captcha_type or "20111",
                extra=extra,
            )

        attempts = [
            ("free", _solve_free),
            ("paid", _solve_paid),
        ] if prefer == "free" else [
            ("paid", _solve_paid),
            ("free", _solve_free),
        ]

        errors = []
        for mode, fn in attempts:
            try:
                result = fn()
                payload: Dict[str, Any] = {
                    "task": task,
                    "mode": mode,
                    "result": result,
                }
                if errors:
                    payload["fallback_reason"] = errors[-1]
                return payload
            except Exception as exc:
                errors.append(f"{mode}: {exc}")

        raise Exception(f"自动识别失败(task={task}) -> {' | '.join(errors)}")

    @staticmethod
    def _normalize_math_expression(text: str) -> str:
        expr = text.strip()
        replacements = {
            "×": "*",
            "x": "*",
            "X": "*",
            "÷": "/",
            "＋": "+",
            "－": "-",
            "—": "-",
            "＝": "",
            "=": "",
            "？": "",
            "?": "",
        }
        for src, dst in replacements.items():
            expr = expr.replace(src, dst)
        expr = re.sub(r"\s+", "", expr)
        expr = re.sub(r"[^0-9+\-*/()]", "", expr)
        return expr

    @staticmethod
    def _safe_eval_math_expression(expression: str) -> Union[int, float]:
        import ast
        import operator as op

        operators = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.USub: op.neg,
            ast.UAdd: op.pos,
        }

        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.Num):
                return node.n
            if isinstance(node, ast.BinOp) and type(node.op) in operators:
                return operators[type(node.op)](_eval(node.left), _eval(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in operators:
                return operators[type(node.op)](_eval(node.operand))
            raise ValueError("不支持的数学表达式")

        parsed = ast.parse(expression, mode="eval")
        value = _eval(parsed)
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value

    @classmethod
    def solve_local_math_captcha(cls, image_input: Union[str, bytes]) -> Dict[str, str]:
        """
        本地免费算术验证码识别（基于 ddddocr + 安全表达式计算）
        入参: 文件路径、bytes 或 base64 字符串
        出参: {"raw_text": 原始OCR文本, "expression": 归一化表达式, "result": 计算结果}
        """
        raw_text = cls.solve_local_text_captcha(image_input, png_fix=True)
        expression = cls._normalize_math_expression(raw_text)
        if not expression:
            raise ValueError(f"无法提取算术表达式，OCR原文: {raw_text}")
        result = cls._safe_eval_math_expression(expression)
        return {
            "raw_text": raw_text,
            "expression": expression,
            "result": str(result),
        }

    @staticmethod
    def _trim_slide_image(slideimg: str) -> None:
        from PIL import Image, ImageChops

        im = Image.open(slideimg)
        bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            new_im = im.crop(bbox)
            new_im.save(slideimg)

    @staticmethod
    def solve_local_slide_distance(back_img_base64: str, slide_img_base64: str) -> int:
        """
        本地免费滑块距离计算（不调用云码 API，不消耗积分）
        入参: 背景大图 base64、滑块图 base64
        出参: x 方向偏移量 (int)
        """
        try:
            import cv2
            import numpy as np
        except ImportError as exc:
            raise ImportError(
                "缺少本地滑块依赖，请安装: pip install opencv-python-headless numpy Pillow"
            ) from exc

        with tempfile.TemporaryDirectory() as tmp_dir:
            backimg = os.path.join(tmp_dir, "backimg.png")
            slideimg = os.path.join(tmp_dir, "slideimg.png")
            block_name = os.path.join(tmp_dir, "block.jpg")
            template_name = os.path.join(tmp_dir, "template.jpg")

            JfbymClient._base64_to_image(back_img_base64, backimg)
            JfbymClient._base64_to_image(slide_img_base64, slideimg)

            JfbymClient._trim_slide_image(slideimg)
            template = cv2.imread(slideimg, 0)
            block = cv2.imread(backimg, 0)
            if block is None or template is None:
                raise ValueError("滑块图片解析失败，请检查 base64 输入")

            cv2.imwrite(block_name, block)
            cv2.imwrite(template_name, template)

            block = cv2.imread(block_name)
            block = cv2.GaussianBlur(block, (3, 3), 0)
            block = cv2.cvtColor(block, cv2.COLOR_RGB2GRAY)
            block = abs(255 - block)
            cv2.imwrite(block_name, block)
            block = cv2.imread(block_name)

            template = cv2.imread(template_name)
            template = cv2.GaussianBlur(template, (3, 3), 0)
            template = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)
            template = abs(255 - template)
            cv2.imwrite(template_name, template)
            template = cv2.imread(template_name)

            result = cv2.matchTemplate(block, template, cv2.TM_CCOEFF_NORMED)
            _, y = np.unravel_index(result.argmax(), result.shape)
            return int(y)

    def get_balance(self) -> str:
        """获取当前账户的积分余额"""
        url = f"{self.base_url}/getUserInfoApi"
        res = requests.post(url, json={"token": self._require_token()}, headers=self._headers).json()
        if res.get("code") == 10001:
            return res["data"]["score"]
        raise Exception(f"获取余额失败: {res}")

    def report_error(self, record_id: str) -> bool:
        """报错返分接口"""
        url = f"{self.base_url}/refundApi"
        # 文档提及参数不定，具体视官方接口为准，通常包含 record_id 作为标记
        res = requests.post(url, json={"token": self._require_token(), "recordId": record_id}, headers=self._headers).json()
        if res.get("code") == 200:
            return True
        return False

    def _prepare_image(self, img_input: Union[str, bytes]) -> str:
        if isinstance(img_input, str):
            if os.path.exists(img_input):
                with open(img_input, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            return img_input  # 假设是已被base64编码的串
        elif isinstance(img_input, bytes):
            return base64.b64encode(img_input).decode()
        raise ValueError("不支持的图片输入格式")

    def solve_common(
        self,
        image_input: Optional[Union[str, bytes]] = None,
        captcha_type: str = "10110",
        extra: Any = None,
        **kwargs,
    ) -> Dict:
        """
        通用单图打码接口。
        适用于文本、点选、推理、旋转等场景。

        参数：
            image_input: 本地路径 / bytes / base64 字符串（部分类型可为空）
            captcha_type: 云码类型编号
            extra: 点选/推理类任务的说明文字
            **kwargs: 透传给 API 的扩展字段，例如 out_ring_image/inner_circle_image
        返回：
            云码接口返回的 data 数据
        """
        payload = {
            "token": self._require_token(),
            "type": str(captcha_type),
            "developer_tag": self.skill_channel_developer_tag
        }
        if image_input is not None:
            payload["image"] = self._prepare_image(image_input)
        if extra is not None:
            payload["extra"] = extra
        if kwargs:
            payload.update(kwargs)

        url = f"{self.base_url}/customApi"
        res = requests.post(url, json=payload, headers=self._headers).json()

        if res.get("code") == 10000:
            return res["data"]
        raise Exception(f"打码失败: {res}")

    def solve_slide(
        self,
        slide_image: Union[str, bytes],
        bg_image: Union[str, bytes],
        captcha_type: str = "20111",
        extra: Any = None,
        **kwargs,
    ) -> Dict:
        """
        双图滑块打码接口。
        适用于需要同时传滑块图和背景图的场景。
        """
        payload = {
            "token": self._require_token(),
            "type": str(captcha_type),
            "slide_image": self._prepare_image(slide_image),
            "background_image": self._prepare_image(bg_image),
            "developer_tag": self.skill_channel_developer_tag
        }
        if extra is not None:
            payload["extra"] = extra
        if kwargs:
            payload.update(kwargs)

        url = f"{self.base_url}/customApi"
        res = requests.post(url, json=payload, headers=self._headers).json()

        if res.get("code") == 10000:
            return res["data"]
        raise Exception(f"滑块打码失败: {res}")

    def solve_recaptcha(
        self, googlekey: str, pageurl: str, captcha_type: str = "40010", **kwargs
    ) -> str:
        """
        Google ReCaptcha / hCaptcha 异步队列打码
        类型 40010：recaptcha v2
        类型 40011：recaptcha v3
        """
        create_url = f"{self.base_url}/funnelApi"
        payload = {
            "token": self._require_token(),
            "type": str(captcha_type),
            "googlekey": googlekey,
            "pageurl": pageurl,
            "enterprise": kwargs.get("enterprise", 0),
            "invisible": kwargs.get("invisible", 0),
            "developer_tag": self.skill_channel_developer_tag,
        }
        if captcha_type == "40011":
            payload["action"] = kwargs.get("action", "")
            payload["min_score"] = kwargs.get("min_score", "0.8")

        res = requests.post(create_url, json=payload, headers=self._headers).json()
        if res.get("code") != 10000:
            raise Exception(f"创建 ReCAPTCHA 任务失败: {res}")

        captcha_id = res["data"]["captchaId"]
        record_id = res["data"]["recordId"]

        # 轮询获取结果
        result_url = f"{self.base_url}/funnelApiResult"
        result_payload = {
            "token": self._require_token(),
            "captchaId": captcha_id,
            "recordId": record_id
        }

        for _ in range(24):  # 最长等待二分钟 (24 * 5s)
            time.sleep(5)
            poll_res = requests.post(result_url, json=result_payload, headers=self._headers).json()
            if poll_res.get("code") == 10001:  # 请求成功且识别完成
                return poll_res["data"]["data"]
            elif poll_res.get("code") in [10004, 10009]:  # 继续等待
                continue
            elif poll_res.get("code") == 10010:  # 失败结束
                raise Exception(f"服务层识别任务结束，状态失败: {poll_res}")

        raise Exception("等待 ReCAPTCHA 结果超时")

    @staticmethod
    def guess_captcha_type(description: str) -> str:
        """
        根据自然语言描述，猜测更合适的云码类型编号。
        用于常见场景快速映射，最终以官方文档为准。
        """
        desc = (description or "").lower()

        # 复杂付费场景优先匹配
        if any(k in desc for k in ["空间推理", "方位", "大写", "小写", "上方", "下方","朝向", "侧对", "空间关系"]):
            if any(k in desc for k in ["无确定", "无按钮", "不需要确定"]):
                return "50009"
            if any(k in desc for k in ["有确定", "确定按钮", "按钮确认"]):
                return "30340"
            return "50009"

        if any(k in desc for k in ["推理拼图", "拼图", "交换图块"]):
            return "30108"

        if "九宫格" in desc or "宫格" in desc:
            return "30008"

        if "轨迹" in desc:
            return "22222"

        if "旋转" in desc:
            if any(k in desc for k in ["双图", "内圈", "外圈"]):
                return "90015"
            return "90007"

        if "问答" in desc:
            return "50103"

        if "滑块" in desc:
            if "单图" in desc or "截图" in desc or "轨迹" in desc:
                return "22222"
            return "20111"

        if "点选" in desc or "点击" in desc:
            if "文字" in desc or "字" in desc:
                return "30100"
            if "图标" in desc or "icon" in desc:
                if "有确定" in desc or "确定按钮" in desc:
                    return "30340"
                return "30104"
            if "成语" in desc or "语序" in desc:
                return "30106"
            if "九宫格" in desc or "宫格" in desc:
                return "30008"
            return "30009"

        if "计算" in desc or "算术" in desc:
            if "中文" in desc:
                return "50101"
            return "50100"

        if "汉字" in desc or "中文" in desc:
            return "10114"

        if "recaptcha" in desc or "谷歌" in desc:
            if "v3" in desc:
                return "40011"
            return "40010"

        if "hcaptcha" in desc:
            return "50013"

        return "10110"
