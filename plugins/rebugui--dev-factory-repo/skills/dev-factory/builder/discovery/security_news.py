"""Security News 발굴 (Sprint 3에서 brave-search로 업그레이드 예정)"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from builder.discovery.base import DiscoverySource
from builder.models import DiscoverySource as DS

logger = logging.getLogger('builder-agent.discovery.news')


class SecurityNewsSource(DiscoverySource):
    """보안 뉴스 기반 아이디어 발굴

    Sprint 1: 키워드 시뮬레이션
    Sprint 3: brave-search 스킬 연동으로 실제 구현
    """

    def __init__(self, config=None):
        super().__init__(config)
        self.keywords = config.keywords if config else [
            'ransomware', 'vulnerability', 'malware', 'phishing',
            'zero-day', 'supply-chain'
        ]
        self.brave_search_path = None
        self._init_brave_search()

    def _init_brave_search(self):
        """brave-search 스킬 경로 확인"""
        from pathlib import Path
        brave_path = Path.home() / '.openclaw' / 'workspace' / 'skills' / 'brave-search' / 'search.js'
        if brave_path.exists():
            self.brave_search_path = str(brave_path)

    def discover(self) -> List[Dict]:
        """보안 뉴스에서 아이디어 발굴"""
        if not self.enabled:
            return []

        # Sprint 3: brave-search가 있으면 실제 검색 사용
        if self.brave_search_path:
            return self._discover_via_brave()

        # Sprint 1: 키워드 기반 시뮬레이션
        return self._discover_simulation()

    def _discover_simulation(self) -> List[Dict]:
        """키워드 기반 시뮬레이션 (임시 구현)"""
        ideas = []

        for keyword in self.keywords:
            ideas.append({
                'title': f"Security Tool: {keyword.replace('-', ' ').title()} Detector",
                'description': f"Tool to detect and analyze {keyword} threats",
                'source': DS.SECURITY_NEWS.value,
                'keyword': keyword,
                'complexity': 'medium',
                'priority': 'medium',
                'tech_stack': ['python'],
                'discovered_at': datetime.now().isoformat()
            })

        logger.info("Security News (simulation): %d ideas", len(ideas))
        return ideas

    def _discover_via_brave(self) -> List[Dict]:
        """brave-search 스킬로 실제 보안 뉴스 검색"""
        import subprocess
        import json

        ideas = []
        search_path = Path(self.brave_search_path).parent

        for keyword in self.keywords[:3]:  # 상위 3개 키워드만
            try:
                query = f"{keyword} security tool 2026"
                result = subprocess.run([
                    'node', str(self.brave_search_path),
                    query, '-n', '3'
                ], cwd=str(search_path), capture_output=True, text=True,
                   timeout=20, env={'BRAVE_API_KEY': ''})  # 환경 변수에서 키 없이도 시도

                if result.returncode != 0:
                    logger.debug("Brave search failed for %s: %s", keyword, result.stderr[:100])
                    continue

                # 결과 파싱 (JSON 출력이라고 가정)
                try:
                    # 결과가 텍스트 형식일 수 있으므로 URL 추출 시도
                    lines = result.stdout.split('\n')
                    for line in lines[:3]:
                        if 'http' in line and ('title' in line.lower() or 'url' in line.lower()):
                            # 간단히 키워드 기반 아이디어 생성
                            ideas.append({
                                'title': f"Security Tool: {keyword.replace('-', ' ').title()} Analyzer",
                                'description': f"Tool to analyze and detect {keyword} threats based on latest security news",
                                'source': DS.SECURITY_NEWS.value,
                                'keyword': keyword,
                                'url': line.strip() if line.startswith('http') else None,
                                'complexity': 'medium',
                                'priority': 'medium',
                                'tech_stack': ['python'],
                                'discovered_at': datetime.now().isoformat()
                            })
                            break

                except json.JSONDecodeError:
                    pass

            except subprocess.TimeoutExpired:
                logger.debug("Brave search timeout for %s", keyword)
            except FileNotFoundError:
                logger.warning("brave-search not found, using simulation")
                return self._discover_simulation()
            except Exception as e:
                logger.debug("Brave search error for %s: %s", keyword, e)

        if ideas:
            logger.info("Security News (brave-search): %d ideas", len(ideas))
        else:
            logger.info("Brave search returned no results, using simulation")
            return self._discover_simulation()

        return ideas
