#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面相学 AI 图像识别工具 v1.0
基于 dlib 68 点面部特征检测，实现面相自动分析

依赖安装:
    pip install dlib opencv-python numpy scipy
    # dlib 需要 CMake 和编译环境
    # 或者使用预编译版本：pip install dlib-bin

使用方法:
    python ai-face-analysis.py image.jpg
    python ai-face-analysis.py image.jpg --output report.json
"""

import cv2
import dlib
import numpy as np
import json
import sys
import os
from scipy.spatial import distance as dist

# 检查依赖
try:
    import dlib
except ImportError:
    print("❌ 错误：需要安装 dlib")
    print("   pip install dlib 或 pip install dlib-bin")
    sys.exit(1)

try:
    import cv2
except ImportError:
    print("❌ 错误：需要安装 opencv-python")
    print("   pip install opencv-python")
    sys.exit(1)


class FaceAnalyzer:
    """面相学 AI 分析器"""
    
    def __init__(self, predictor_path=None):
        """
        初始化分析器
        
        Args:
            predictor_path: dlib 68 点预测模型路径
                           默认使用预训练模型或自动下载
        """
        # 加载 dlib 人脸检测器
        self.detector = dlib.get_frontal_face_detector()
        
        # 加载 68 点预测模型
        if predictor_path is None:
            # 尝试常见路径
            common_paths = [
                "shape_predictor_68_face_landmarks.dat",
                "./models/shape_predictor_68_face_landmarks.dat",
                os.path.expanduser("~/.dlib/shape_predictor_68_face_landmarks.dat"),
            ]
            for path in common_paths:
                if os.path.exists(path):
                    predictor_path = path
                    break
        
        if predictor_path and os.path.exists(predictor_path):
            self.predictor = dlib.shape_predictor(predictor_path)
            print(f"✅ 加载预测模型：{predictor_path}")
        else:
            print("⚠️  未找到预测模型，请下载：")
            print("   http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
            print("   解压后放到当前目录或指定路径")
            self.predictor = None
    
    def detect_face(self, image):
        """
        检测人脸
        
        Args:
            image: OpenCV 图像 (BGR)
        
        Returns:
            faces: 检测到的人脸列表
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸
        faces = self.detector(gray, 1)
        
        return faces, gray
    
    def get_landmarks(self, image, face):
        """
        获取 68 个面部特征点
        
        Args:
            image: OpenCV 图像
            face: dlib 人脸矩形框
        
        Returns:
            landmarks: 68 个特征点坐标
        """
        if self.predictor is None:
            return None
        
        landmarks = self.predictor(image, face)
        points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(68)]
        
        return points
    
    def analyze_face_shape(self, landmarks):
        """
        分析脸型（五行分类）
        
        Args:
            landmarks: 68 个特征点
        
        Returns:
            shape_type: 脸型（金/木/水/火/土）
            ratios: 比例数据
        """
        if landmarks is None:
            return "未知", {}
        
        # 计算面部尺寸
        jaw_width = dist.euclidean(landmarks[1], landmarks[15])  # 下颌宽度
        cheek_width = dist.euclidean(landmarks[2], landmarks[14])  # 颧骨宽度
        forehead_width = dist.euclidean(landmarks[20], landmarks[23])  # 额头宽度
        face_height = dist.euclidean(
            landmarks[8],  # 下巴
            (landmarks[20][0] + landmarks[23][0]) // 2, landmarks[20][1]  # 额头中点
        )
        
        # 计算比例
        width_ratio = face_height / (jaw_width + 0.01)
        cheek_ratio = cheek_width / (face_height + 0.01)
        forehead_ratio = forehead_width / (jaw_width + 0.01)
        
        # 判断脸型
        if width_ratio > 1.5:
            shape_type = "木"  # 长脸
            shape_name = "长形"
        elif cheek_ratio > 1.1 and forehead_ratio < 0.9:
            shape_type = "水"  # 圆脸
            shape_name = "圆形"
        elif jaw_width > cheek_width * 0.9:
            shape_type = "金"  # 方脸
            shape_name = "方形"
        elif forehead_width > cheek_width * 1.1:
            shape_type = "火"  # 尖脸
            shape_name = "尖形"
        else:
            shape_type = "土"  # 厚脸
            shape_name = "厚重"
        
        return shape_type, {
            "face_height": face_height,
            "jaw_width": jaw_width,
            "cheek_width": cheek_width,
            "forehead_width": forehead_width,
            "width_ratio": width_ratio,
            "cheek_ratio": cheek_ratio,
            "forehead_ratio": forehead_ratio,
            "shape_name": shape_name
        }
    
    def analyze_eyes(self, landmarks):
        """
        分析眼睛特征
        
        Args:
            landmarks: 68 个特征点
        
        Returns:
            eye_features: 眼睛特征字典
        """
        if landmarks is None:
            return {}
        
        # 左眼特征点 (36-41)
        left_eye = landmarks[36:42]
        # 右眼特征点 (42-47)
        right_eye = landmarks[42:48]
        
        # 计算眼睛大小
        left_eye_width = dist.euclidean(left_eye[0], left_eye[3])
        left_eye_height = dist.euclidean(left_eye[1], left_eye[5])
        right_eye_width = dist.euclidean(right_eye[0], right_eye[3])
        right_eye_height = dist.euclidean(right_eye[1], right_eye[5])
        
        # 平均眼睛大小
        avg_width = (left_eye_width + right_eye_width) / 2
        avg_height = (left_eye_height + right_eye_height) / 2
        eye_ratio = avg_height / (avg_width + 0.01)
        
        # 判断眼睛大小
        if avg_width > 50:  # 阈值可根据实际情况调整
            eye_size = "大"
        elif avg_width < 35:
            eye_size = "小"
        else:
            eye_size = "中"
        
        # 判断眼尾方向
        left_eye_tail = left_eye[3][1] - left_eye[0][1]
        right_eye_tail = right_eye[3][1] - right_eye[0][1]
        avg_tail = (left_eye_tail + right_eye_tail) / 2
        
        if avg_tail < -5:
            eye_direction = "上扬"
        elif avg_tail > 5:
            eye_direction = "下垂"
        else:
            eye_direction = "平"
        
        return {
            "eye_size": eye_size,
            "eye_width": avg_width,
            "eye_height": avg_height,
            "eye_ratio": eye_ratio,
            "eye_direction": eye_direction,
            "left_eye": {"width": left_eye_width, "height": left_eye_height},
            "right_eye": {"width": right_eye_width, "height": right_eye_height}
        }
    
    def analyze_eyebrows(self, landmarks):
        """
        分析眉毛特征
        
        Args:
            landmarks: 68 个特征点
        
        Returns:
            eyebrow_features: 眉毛特征字典
        """
        if landmarks is None:
            return {}
        
        # 左眉特征点 (17-21)
        left_brow = landmarks[17:22]
        # 右眉特征点 (22-26)
        right_brow = landmarks[22:27]
        
        # 计算眉毛密度（基于特征点分布）
        left_brow_length = sum(dist.euclidean(left_brow[i], left_brow[i+1]) for i in range(4))
        right_brow_length = sum(dist.euclidean(right_brow[i], right_brow[i+1]) for i in range(4))
        
        # 判断眉毛浓密度（简化版）
        brow_density = "中"  # 实际需要图像分析
        
        # 判断眉毛形状
        left_brow_slope = left_brow[0][1] - left_brow[4][1]
        right_brow_slope = right_brow[0][1] - right_brow[4][1]
        
        if left_brow_slope > 10 or right_brow_slope > 10:
            brow_shape = "上扬"
        elif left_brow_slope < -10 or right_brow_slope < -10:
            brow_shape = "下垂"
        else:
            brow_shape = "平"
        
        return {
            "brow_density": brow_density,
            "brow_shape": brow_shape,
            "left_brow_length": left_brow_length,
            "right_brow_length": right_brow_length
        }
    
    def analyze_nose(self, landmarks):
        """
        分析鼻子特征
        
        Args:
            landmarks: 68 个特征点
        
        Returns:
            nose_features: 鼻子特征字典
        """
        if landmarks is None:
            return {}
        
        # 鼻子特征点 (27-35)
        nose = landmarks[27:36]
        
        # 计算鼻子高度和宽度
        nose_height = dist.euclidean(nose[0], nose[8])
        nose_width = dist.euclidean(nose[4], nose[12]) if len(nose) > 12 else nose_height * 0.3
        
        # 判断鼻子高低
        if nose_height > 60:
            nose_height_type = "高"
        elif nose_height < 40:
            nose_height_type = "低"
        else:
            nose_height_type = "中"
        
        return {
            "nose_height": nose_height,
            "nose_width": nose_width,
            "nose_height_type": nose_height_type
        }
    
    def analyze_mouth(self, landmarks):
        """
        分析嘴巴特征
        
        Args:
            landmarks: 68 个特征点
        
        Returns:
            mouth_features: 嘴巴特征字典
        """
        if landmarks is None:
            return {}
        
        # 嘴巴特征点 (48-67)
        mouth = landmarks[48:68]
        
        # 计算嘴巴宽度
        mouth_width = dist.euclidean(mouth[0], mouth[6])
        
        # 判断嘴巴大小
        if mouth_width > 60:
            mouth_size = "大"
        elif mouth_width < 40:
            mouth_size = "小"
        else:
            mouth_size = "中"
        
        # 判断嘴角方向
        mouth_left = mouth[0]
        mouth_right = mouth[6]
        mouth_slope = mouth_right[1] - mouth_left[1]
        
        if mouth_slope < -5:
            mouth_corner = "上扬"
        elif mouth_slope > 5:
            mouth_corner = "下垂"
        else:
            mouth_corner = "平"
        
        return {
            "mouth_width": mouth_width,
            "mouth_size": mouth_size,
            "mouth_corner": mouth_corner
        }
    
    def analyze_ears(self, image, face):
        """
        分析耳朵特征（简化版，实际需要侧面图像）
        
        Args:
            image: OpenCV 图像
            face: dlib 人脸矩形框
        
        Returns:
            ear_features: 耳朵特征字典
        """
        # 正面图像难以准确分析耳朵
        # 这里返回估计值
        face_width = face.right() - face.left()
        
        # 简化判断
        ear_size = "中"  # 实际需要更复杂的分析
        
        return {
            "ear_size": ear_size,
            "note": "正面图像难以准确分析耳朵，需要侧面图像"
        }
    
    def generate_analysis(self, image_path, output_path=None):
        """
        生成完整面相分析报告
        
        Args:
            image_path: 输入图像路径
            output_path: 输出报告路径（可选）
        
        Returns:
            report: 分析报告字典
        """
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            return {"error": f"无法读取图像：{image_path}"}
        
        # 检测人脸
        faces, gray = self.detect_face(image)
        
        if len(faces) == 0:
            return {"error": "未检测到人脸"}
        
        if len(faces) > 1:
            print(f"⚠️  检测到 {len(faces)} 张人脸，分析第一张")
        
        face = faces[0]
        
        # 获取特征点
        landmarks = self.get_landmarks(image, face)
        
        if landmarks is None:
            return {"error": "无法获取面部特征点"}
        
        # 分析各个部位
        shape_type, shape_data = self.analyze_face_shape(landmarks)
        eye_features = self.analyze_eyes(landmarks)
        eyebrow_features = self.analyze_eyebrows(landmarks)
        nose_features = self.analyze_nose(landmarks)
        mouth_features = self.analyze_mouth(landmarks)
        ear_features = self.analyze_ears(image, face)
        
        # 生成面相学解读
        interpretation = self.generate_interpretation(
            shape_type, shape_data, eye_features, eyebrow_features,
            nose_features, mouth_features, ear_features
        )
        
        # 生成报告
        report = {
            "image": image_path,
            "face_detected": True,
            "landmarks": landmarks,
            "analysis": {
                "face_shape": {
                    "type": shape_type,
                    "name": shape_data.get("shape_name", ""),
                    "data": shape_data
                },
                "eyes": eye_features,
                "eyebrows": eyebrow_features,
                "nose": nose_features,
                "mouth": mouth_features,
                "ears": ear_features
            },
            "interpretation": interpretation,
            "disclaimer": "本分析仅供娱乐参考，不具备科学依据"
        }
        
        # 保存报告
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"✅ 报告已保存：{output_path}")
        
        return report
    
    def generate_interpretation(self, shape_type, shape_data, eye_features, 
                                 eyebrow_features, nose_features, mouth_features, ear_features):
        """
        生成面相学解读
        
        Returns:
            interpretation: 解读文本
        """
        interpretations = []
        
        # 脸型解读
        shape_meanings = {
            "金": "方脸，性格刚毅果断，有正义感",
            "木": "长脸，仁慈善良，有上进心",
            "水": "圆脸，聪明智慧，适应力强",
            "火": "尖脸，热情外向，行动力强",
            "土": "厚重，诚信稳重，务实可靠"
        }
        if shape_type in shape_meanings:
            interpretations.append(f"脸型（{shape_type}形）: {shape_meanings[shape_type]}")
        
        # 眼睛解读
        if eye_features:
            eye_size = eye_features.get("eye_size", "")
            eye_dir = eye_features.get("eye_direction", "")
            if eye_size == "大":
                interpretations.append("眼睛：大而明亮，性格开朗，表达力强")
            elif eye_size == "小":
                interpretations.append("眼睛：小而专注，心思细腻，观察力强")
            if eye_dir == "上扬":
                interpretations.append("眼尾上扬，性格外向，有魅力")
            elif eye_dir == "下垂":
                interpretations.append("眼尾下垂，性格温和，体贴")
        
        # 鼻子解读
        if nose_features:
            nose_h = nose_features.get("nose_height_type", "")
            if nose_h == "高":
                interpretations.append("鼻子高挺，财运较好，有领导能力")
            elif nose_h == "低":
                interpretations.append("鼻子较低，性格温和，需努力积累")
        
        # 嘴巴解读
        if mouth_features:
            mouth_s = mouth_features.get("mouth_size", "")
            mouth_c = mouth_features.get("mouth_corner", "")
            if mouth_s == "大":
                interpretations.append("嘴巴大，表达能力强，社交能力好")
            elif mouth_s == "小":
                interpretations.append("嘴巴小，谨慎细心，言语保守")
            if mouth_c == "上扬":
                interpretations.append("嘴角上扬，乐观积极，人缘好")
            elif mouth_c == "下垂":
                interpretations.append("嘴角下垂，需注意心态调整")
        
        return interpretations


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("👤 面相学 AI 图像识别工具 v1.0")
        print("\n使用方法:")
        print("  python ai-face-analysis.py <图片路径> [输出文件]")
        print("\n示例:")
        print("  python ai-face-analysis.py face.jpg")
        print("  python ai-face-analysis.py face.jpg output.json")
        print("\n依赖安装:")
        print("  pip install dlib opencv-python numpy scipy")
        print("\n模型下载:")
        print("  http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
        sys.exit(0)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 创建分析器
    analyzer = FaceAnalyzer()
    
    if analyzer.predictor is None:
        print("\n❌ 无法继续分析，请先下载预测模型")
        sys.exit(1)
    
    # 分析图像
    print(f"\n🔍 分析图像：{image_path}")
    report = analyzer.generate_analysis(image_path, output_path)
    
    if "error" in report:
        print(f"❌ 错误：{report['error']}")
        sys.exit(1)
    
    # 输出结果
    print("\n" + "="*60)
    print("📊 面相分析报告")
    print("="*60 + "\n")
    
    print(f"✅ 人脸检测：成功")
    print(f"📍 特征点：68 个\n")
    
    print("🎯 分析结果:")
    for item in report["interpretation"]:
        print(f"  • {item}")
    
    print("\n" + "="*60)
    print("⚠️  免责声明：本分析仅供娱乐参考，不具备科学依据")
    print("="*60 + "\n")
    
    # 如果保存了文件，提示
    if output_path:
        print(f"📄 详细报告已保存到：{output_path}")


if __name__ == "__main__":
    main()
