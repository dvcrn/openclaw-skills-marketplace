#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QST Memory v1.8.4 - Phase 2: 自動完成檢測器

功能:
1. 檢測所有必選子任務是否完成
2. 檢測進度是否達到 100%
3. 檢測版本是否已發布（開發任務）
4. 在 Heartbeat 時自動檢測

作者: Zhuangzi
版本: v1.8.4 Phase 2
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional, List
import sys

# 導入 existing 模塊
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from subtask_manager import SubtaskManager


class CompletionDetector:
    """任務自動完成檢測器"""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.subtask_manager = SubtaskManager(state_file)
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """加載狀態文件"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_state(self) -> None:
        """保存狀態文件"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    # ========== 自動完成檢測核心 ==========

    def detect_completion(self) -> bool:
        """
        檢測任務是否應該完成

        Returns:
            是否應該完成
        """

        # 1. 檢查狀態是否為 DOING
        status = self.state.get('status', '')
        if status != 'doing':
            return False

        # 2. 檢查所有必選子任務是否完成
        if not self._all_required_subtasks_complete():
            return False

        # 3. 檢查進度是否達到 100%
        progress = self.subtask_manager.calculate_progress()
        if progress < 100:
            return False

        # 4. 檢查是否有未完成的必選子任務
        pending_required = self._count_pending_required_subtasks()
        if pending_required > 0:
            return False

        # 5. 時間檢查（如果是開發任務，確認版本已發布）
        task_type = self.state.get('type', '')
        if task_type == 'Development':
            if not self._version_released():
                return False

        return True

    def _all_required_subtasks_complete(self) -> bool:
        """
        檢查所有必選子任務是否完成

        Returns:
            是否所有必選子任務都完成
        """

        subtasks = self.state.get('subtasks', [])

        if not subtasks:
            # 沒有子任務時，檢查原始進度
            return self.state.get('progress', 0) >= 100

        # 只檢查頂層必選子任務
        required_subtasks = [
            st for st in subtasks
            if st.get('required', True) and st.get('parent_id') is None
        ]

        return all(st['status'] == 'completed' for st in required_subtasks)

    def _count_pending_required_subtasks(self) -> int:
        """
        計算未完成的必選子任務數量

        Returns:
            未完成的必選子任務數量
        """

        subtasks = self.state.get('subtasks', [])

        if not subtasks:
            return 0

        # 只計算頂層必選子任務
        required_subtasks = [
            st for st in subtasks
            if st.get('required', True) and st.get('parent_id') is None
        ]

        return len([
            st for st in required_subtasks
            if st['status'] != 'completed'
        ])

    def _version_released(self) -> bool:
        """
        檢查任務對應的版本是否已發布（針對開發任務）

        Returns:
            版本是否已發布
        """

        task_name = self.state.get('task', '')

        # 嘗試從任務名稱中提取版本號
        # 例如: "開發 QST Memory v1.8.4" -> "v1.8.4"
        version_match = None
        if 'v1.' in task_name or 'v2.' in task_name:
            # 尋找版本號格式 v{major}.{minor}
            import re
            matches = re.findall(r'v\d+\.\d+(\.\d+)?', task_name)
            if matches:
                version_match = matches[0]

        if not version_match:
            # 無版本號，假設已完成
            return True

        # 檢查 git tag
        try:
            result = subprocess.run(
                ['git', 'tag', '-l', version_match],
                capture_output=True,
                text=True,
                cwd=self.state_file.parent.parent
            )
            return bool(result.stdout.strip())
        except:
            # 如果無法檢查 git，假設已完成
            return True

    # ========== 事件發布 ==========

    def publish_can_complete_event(self) -> Dict:
        """
        發布「可以完成」事件

        Returns:
            事件字典
        """

        event = {
            'type': 'CAN_COMPLETE',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'message': f'任務 「{self.state.get("task", "")}」 已滿足完成條件，請標記為完成',
            'data': {
                'task': self.state.get('task'),
                'type': self.state.get('type'),
                'progress': self.subtask_manager.calculate_progress(),
                'subtasks_completed': self._count_completed_subtasks(),
                'subtasks_total': self._count_total_required_subtasks()
            }
        }

        # 保存到事件文件
        self._add_event(event)

        return event

    def _add_event(self, event: Dict) -> None:
        """添加事件到事件文件"""

        events_file = self.state_file.parent / 'qst_events.json'

        # 載入現有事件
        events = []
        if events_file.exists():
            with open(events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)

        # 添加新事件
        events.append(event)

        # 保存事件
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)

    # ========== 輔助方法 ==========

    def _count_completed_subtasks(self) -> int:
        """統計完成的子任務數量"""
        subtasks = self.state.get('subtasks', [])
        required = [st for st in subtasks if st.get('required', True) and st.get('parent_id') is None]
        return len([st for st in required if st['status'] == 'completed'])

    def _count_total_required_subtasks(self) -> int:
        """統計總必選子任務數量"""
        subtasks = self.state.get('subtasks', [])
        return len([st for st in subtasks if st.get('required', True) and st.get('parent_id') is None])


# ========== 主程序入口 ==========

if __name__ == '__main__':
    # 測試代碼
    state_file = Path('/home/node/.openclaw/workspace/skills/qst-memory/data/qst_doing-state.json')
    detector = CompletionDetector(state_file)

    print("🧪 自動完成檢測器測試")
    print()

    # 顯示當前狀態
    print("📊 當前狀態:")
    print(f"   任務: {detector.state.get('task', 'N/A')}")
    print(f"   狀態: {detector.state.get('status', 'N/A')}")
    print(f"   類型: {detector.state.get('type', 'N/A')}")
    print()

    # 檢測是否可以完成
    can_complete = detector.detect_completion()
    print(f"✅ 可以完成: {can_complete}")

    # 顯示詳細信息
    print()
    print("📋 詳細信息:")
    print(f"   進度: {detector.subtask_manager.calculate_progress()}%")
    print(f"   完成子任務: {detector._count_completed_subtasks()}/{detector._count_total_required_subtasks()}")
    print(f"   待處理子任務: {detector._count_pending_required_subtasks()}")
    print(f"   所有必選完成: {detector._all_required_subtasks_complete()}")
    print(f"   版本已發布: {detector._version_released()}")

    # 如果可以完成，發布事件
    if can_complete:
        print()
        print("📢 發布「可以完成」事件:")
        event = detector.publish_can_complete_event()
        print(f"   類型: {event['type']}")
        print(f"   時間: {event['timestamp']}")
        print(f"   消息: {event['message']}")

    print()
    print("🐲 測試完成！")
