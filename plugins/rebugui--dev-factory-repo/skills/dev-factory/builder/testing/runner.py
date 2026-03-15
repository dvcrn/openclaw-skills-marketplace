"""TestRunner - 통합 테스트 실행 및 리포팅"""

import logging
import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger('builder-agent.testing')


class TestRunner:
    """프로젝트 테스트 실행 및 결과 분석"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def run(self, project_path: Path) -> Dict:
        """프로젝트 테스트 실행"""
        if not project_path.exists():
            return {
                'success': False,
                'output': f'Project path not found: {project_path}',
                'tests_run': 0,
                'failures': 0,
                'errors': 0
            }

        logger.info("Running tests in %s", project_path)

        try:
            result = subprocess.run(
                ['python3', '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**os.environ, 'PYTHONPATH': 'src'}
            )

            output = result.stdout + result.stderr
            parsed = self._parse_unittest_output(output)

            return {
                'success': result.returncode == 0,
                'output': output,
                'returncode': result.returncode,
                **parsed
            }

        except subprocess.TimeoutExpired:
            logger.warning("Test timeout in %s", project_path)
            return {
                'success': False,
                'output': 'Test timeout',
                'tests_run': 0,
                'failures': 0,
                'errors': 0
            }
        except Exception as e:
            logger.warning("Test error: %s", e)
            return {
                'success': False,
                'output': str(e),
                'tests_run': 0,
                'failures': 0,
                'errors': 0
            }

    def run_specific(self, project_path: Path, test_file: str) -> Dict:
        """특정 테스트 파일만 실행"""
        try:
            result = subprocess.run(
                ['python3', '-m', 'unittest', test_file, '-v'],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**os.environ, 'PYTHONPATH': 'src'}
            )

            output = result.stdout + result.stderr
            parsed = self._parse_unittest_output(output)

            return {
                'success': result.returncode == 0,
                'output': output,
                **parsed
            }

        except Exception as e:
            return {
                'success': False,
                'output': str(e),
                'tests_run': 0,
                'failures': 0,
                'errors': 0
            }

    def _parse_unittest_output(self, output: str) -> Dict:
        """unittest 출력 파싱"""
        tests_run = 0
        failures = 0
        errors = 0

        # "Ran X tests in Ys" 패턴
        import re
        match = re.search(r'Ran (\d+) tests?', output)
        if match:
            tests_run = int(match.group(1))

        # "FAILED (failures=X, errors=Y)" 패턴
        match = re.search(r'FAILED \(failures=(\d+), errors=(\d+)\)', output)
        if match:
            failures = int(match.group(1))
            errors = int(match.group(2))

        # "OK" 또는 "FAILED" 확인
        success = 'OK' in output.split('\n')[-1] if output else False

        return {
            'tests_run': tests_run,
            'failures': failures,
            'errors': errors,
            'parsed_success': success
        }

    def save_report(self, result: Dict, report_path: Path):
        """테스트 결과 리포트 저장"""
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            'timestamp': datetime.now().isoformat(),
            'success': result['success'],
            'tests_run': result['tests_run'],
            'failures': result['failures'],
            'errors': result['errors'],
            'output': result['output'][-1000:] if len(result['output']) > 1000 else result['output']
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info("Test report saved to %s", report_path)
