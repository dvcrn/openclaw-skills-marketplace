"""IdeaScorer - 아이디어 품질 점수화"""

import logging
from datetime import datetime, timedelta
from typing import Dict

logger = logging.getLogger('builder-agent.discovery.scorer')


class IdeaScorer:
    """5차원 아이디어 점수화"""

    # 가중치
    WEIGHTS = {
        'recency': 0.25,
        'severity': 0.20,
        'feasibility': 0.20,
        'novelty': 0.20,
        'demand': 0.15,
    }

    def score(self, idea: Dict, existing_ideas: list = None) -> float:
        """아이디어 종합 점수 계산 (0.0 ~ 1.0)"""
        scores = {
            'recency': self._score_recency(idea),
            'severity': self._score_severity(idea),
            'feasibility': self._score_feasibility(idea),
            'novelty': self._score_novelty(idea, existing_ideas),
            'demand': self._score_demand(idea),
        }

        total = sum(self.WEIGHTS[k] * scores[k] for k in self.WEIGHTS)

        logger.debug("Score %s: %.2f (recency=%.2f, severity=%.2f, feasibility=%.2f, novelty=%.2f, demand=%.2f)",
                    idea['title'][:30], total, scores['recency'], scores['severity'],
                    scores['feasibility'], scores['novelty'], scores['demand'])

        return total

    def _score_recency(self, idea: Dict) -> float:
        """최신성 점수"""
        discovered_at = idea.get('discovered_at', '')
        if not discovered_at:
            return 0.5

        try:
            dt = datetime.fromisoformat(discovered_at)
            age_hours = (datetime.now() - dt).total_seconds() / 3600

            if age_hours < 1:
                return 1.0
            elif age_hours < 24:
                return 0.8
            elif age_hours < 168:  # 7일
                return 0.5
            else:
                return 0.2
        except:
            return 0.5

    def _score_severity(self, idea: Dict) -> float:
        """심각도 점수"""
        severity = idea.get('severity', '').upper()
        cvss_score = idea.get('score', 0)

        # CVE인 경우 CVSS 점수 사용
        if cvss_score:
            return min(cvss_score / 10.0, 1.0)

        # priority 기반
        priority = idea.get('priority', '').lower()
        if priority == 'critical':
            return 1.0
        elif priority == 'high':
            return 0.8
        elif priority == 'medium':
            return 0.5
        else:
            return 0.2

    def _score_feasibility(self, idea: Dict) -> float:
        """구현 가능성 점수"""
        complexity = idea.get('complexity', '').lower()

        if complexity == 'simple':
            return 1.0
        elif complexity == 'medium':
            return 0.7
        elif complexity == 'complex':
            return 0.4
        else:
            return 0.5

    def _score_novelty(self, idea: Dict, existing_ideas: list = None) -> float:
        """새로움 점수 (기존 아이디어와 중복 여부)"""
        if not existing_ideas:
            return 1.0

        title = idea.get('title', '').lower()
        description = idea.get('description', '').lower()

        # 간단한 중복 체크 (Sprint 4에서 semantic dedup으로 개선)
        for existing in existing_ideas:
            existing_title = existing.get('title', '').lower()
            # 제목 유사도 70% 이상이면 중복
            if self._similar(title, existing_title):
                return 0.3

        return 1.0

    def _score_demand(self, idea: Dict) -> float:
        """수요 점수"""
        # GitHub stars가 있으면 사용
        url = idea.get('url', '')
        if 'github.com' in url:
            # 현재는 stars 정보 없음, Sprint 2-3에서 개선
            return 0.5

        # CVE는 높은 수요
        if idea.get('source') == 'cve_database':
            return 0.8

        return 0.5

    def _similar(self, a: str, b: str) -> bool:
        """간단한 유사도 체크"""
        if a == b:
            return True
        if a in b or b in a:
            return True
        return False
