#!/usr/bin/env python3
"""
Discovery Layer Runner (New Architecture)
Sprint 2: 패키지 구조 기반 실행
"""

import sys
import json
import logging
import time
from pathlib import Path

# Add builder-agent to path
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config, setup_logging
from builder.pipeline import BuilderPipeline
from builder.integration.notion_sync import NotionSync
from health_check import check_health, log_health_report

logger = logging.getLogger('builder-agent.runner')


def main():
    """Discovery 파이프라인 실행"""

    # 설정 로드
    config = load_config()
    setup_logging(config)

    logger.info("=" * 50)
    logger.info("DISCOVERY LAYER - SPRINT 2 ARCHITECTURE")
    logger.info("=" * 50)

    # 헬스체크
    health = check_health()
    if not log_health_report(health):
        logger.warning("Health check degraded, proceeding with available sources")

    start_time = time.time()

    # 파이프라인 초기화
    pipeline = BuilderPipeline(config)

    # Discovery 실행
    result = pipeline.run_discovery_pipeline()

    elapsed = time.time() - start_time
    logger.info("Total elapsed: %.1fs", elapsed)

    # Notion 큐 등록
    notion_db_id = config.notion.database_id
    if notion_db_id and not notion_db_id.startswith('${'):
        try:
            notion = NotionSync(notion_db_id)
            max_queue = config.notion.max_queue_per_run
            queued = notion.queue_ideas(result['ideas'], max_queue)
            logger.info("Queued %d ideas to Notion", queued)
        except Exception as e:
            logger.error("Notion queue failed: %s", e)
    else:
        logger.info("Notion DB ID not configured, saving locally only")

    # 리포트 저장
    report_path = Path(config.discovery.output_dir) / "latest_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        'timestamp': time.time(),
        'total': result['count'],
        'elapsed_seconds': round(elapsed, 1),
        'health': health,
        'ideas': result['ideas'][:10]  # 상위 10개만 저장
    }

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info("Report saved to %s", report_path)
    logger.info("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
