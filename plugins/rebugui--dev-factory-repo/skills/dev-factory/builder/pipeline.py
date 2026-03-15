"""BuilderPipeline - 전체 파이프라인 오케스트레이션"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Optional

from builder.models import ProjectIdea, BuildResult, PipelineStage, DiscoverySource
from builder.discovery.github_trending import GitHubTrendingSource
from builder.discovery.cve_database import CVEDatabaseSource
from builder.discovery.security_news import SecurityNewsSource
from builder.discovery.cache import DiscoveryCache
from builder.discovery.scorer import IdeaScorer
from builder.discovery.dedup import SemanticDeduplicator
from builder.orchestrator import HybridOrchestrator
from builder.correction.base import BaseCorrectionEngine
from builder.correction.analyzer import ErrorAnalyzer
from builder.correction.fixer import CodeFixer

logger = logging.getLogger('builder-agent.pipeline')


class BuilderPipeline:
    """Builder Agent 통합 파이프라인

    Discovery -> Dedup -> Score -> Queue -> Build -> Test -> Fix -> Publish
    """

    def __init__(self, config=None):
        self.config = config

        # Discovery
        cache_dir = Path(config.discovery.output_dir) / "cache" if config else Path("/tmp/builder-discovery/cache")
        self.cache = DiscoveryCache(cache_dir, ttl_seconds=config.discovery.cache_ttl_seconds if config else 3600)

        self.sources = [
            GitHubTrendingSource(config.discovery.github if config else None),
            CVEDatabaseSource(config.discovery.cve if config else None),
            SecurityNewsSource(config.discovery.security_news if config else None),
        ]
        self.scorer = IdeaScorer()
        self.deduplicator = SemanticDeduplicator(similarity_threshold=0.7)

        # Build
        self.orchestrator = HybridOrchestrator(config)
        self.analyzer = ErrorAnalyzer()
        self.fixer = CodeFixer()

        # State
        self.state = PipelineState()
        self.output_dir = Path(config.discovery.output_dir) if config else Path("/tmp/builder-discovery")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ──────────────────────────────────────────────
    # Discovery Pipeline
    # ──────────────────────────────────────────────

    def run_discovery_pipeline(self) -> Dict:
        """Discovery -> Dedup -> Score -> Queue"""
        self.state.set_stage(PipelineStage.DISCOVERING.value)
        start_time = time.time()

        logger.info("Starting discovery pipeline...")

        # 1. 병렬 Discovery
        ideas = self._discover_all()
        logger.info("Discovered %d raw ideas", len(ideas))

        # 2. 중복 제거
        unique_ideas = self._deduplicate(ideas)
        logger.info("After dedup: %d ideas", len(unique_ideas))

        # 3. 점수화
        scored_ideas = self._score_and_rank(unique_ideas)
        logger.info("Scored ideas: top=%.2f, bottom=%.2f",
                   scored_ideas[0]['score'] if scored_ideas else 0,
                   scored_ideas[-1]['score'] if scored_ideas else 0)

        # 4. 저장
        self._save_discovered(scored_ideas)

        elapsed = time.time() - start_time
        logger.info("Discovery pipeline completed in %.1fs", elapsed)

        return {
            'success': True,
            'ideas': scored_ideas,
            'count': len(scored_ideas),
            'elapsed_seconds': round(elapsed, 1)
        }

    def _discover_all(self) -> List[Dict]:
        """병렬 Discovery"""
        all_ideas = []

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(source.discover): source.__class__.__name__
                for source in self.sources if source.enabled
            }

            for future in as_completed(futures, timeout=60):
                source_name = futures[future]
                try:
                    ideas = future.result(timeout=30)
                    all_ideas.extend(ideas)
                    logger.info("%s: %d ideas", source_name, len(ideas))
                except Exception as e:
                    logger.warning("%s failed: %s", source_name, e)

        return all_ideas

    def _deduplicate(self, ideas: List[Dict]) -> List[Dict]:
        """의미론적 중복 제거 (Sprint 4: difflib fuzzy matching)"""
        return self.deduplicator.deduplicate(ideas)

    def _score_and_rank(self, ideas: List[Dict]) -> List[Dict]:
        """점수화 및 정렬"""
        for idea in ideas:
            idea['score'] = self.scorer.score(idea, ideas)

        return sorted(ideas, key=lambda x: x['score'], reverse=True)

    def _save_discovered(self, ideas: List[Dict]):
        """발굴 결과 저장"""
        output_file = self.output_dir / "discovered_ideas.json"
        with open(output_file, 'w') as f:
            json.dump(ideas, f, indent=2, ensure_ascii=False)
        logger.info("Saved %d ideas to %s", len(ideas), output_file)

    # ──────────────────────────────────────────────
    # Build Pipeline
    # ──────────────────────────────────────────────

    def run_build_pipeline(self, idea: Dict, project_path: Path) -> Dict:
        """Build -> Test -> Fix"""
        self.state.set_stage(PipelineStage.BUILDING.value)
        self.state.current_project = idea['title']

        # ProjectIdea로 변환
        project = ProjectIdea.from_dict(idea)

        # 개발
        build_result = self.orchestrator.develop(project, project_path)

        if build_result.success:
            # 테스트
            self.state.set_stage(PipelineStage.TESTING.value)
            test_result = self._run_tests(project_path)

            if test_result['success']:
                self.state.set_stage(PipelineStage.COMPLETED.value)
                logger.info("Build completed: %s", project.title)
            else:
                # 수정 시도
                self.state.set_stage(PipelineStage.FIXING.value)
                error = self.analyzer.analyze(test_result['output'])
                fixed = self.fixer.fix(error, project_path, project.complexity)

                if fixed:
                    # 재테스트
                    test_result = self._run_tests(project_path)
                    build_result.success = test_result['success']

        self.state.current_project = None
        return build_result.to_dict()

    def _run_tests(self, project_path: Path) -> Dict:
        """테스트 실행"""
        import subprocess
        import os

        try:
            result = subprocess.run(
                ['python3', '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, 'PYTHONPATH': 'src'}
            )

            return {
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr
            }

        except subprocess.TimeoutExpired:
            return {'success': False, 'output': 'Test timeout'}
        except Exception as e:
            return {'success': False, 'output': str(e)}


class PipelineState:
    """파이프라인 상태 관리"""

    def __init__(self):
        self.stage = "idle"
        self.current_project: Optional[str] = None
        self.started_at: Optional[str] = None
        self.last_checkpoint: Optional[str] = None
        self.errors: List[str] = []

    def set_stage(self, stage: str):
        """스테이지 변경"""
        self.stage = stage
        self.last_checkpoint = time.time()

    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        return {
            'stage': self.stage,
            'current_project': self.current_project,
            'last_checkpoint': self.last_checkpoint,
            'errors': self.errors
        }
