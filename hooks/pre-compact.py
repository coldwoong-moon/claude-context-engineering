#!/usr/bin/env python3
"""PreCompact: 컨텍스트 압축 전 중요 정보 백업

2025-12 신규 Hook - 컨텍스트 압축(compact) 전 트리거

기능:
- 세션 요약 생성 → context.md에 저장
- 미완료 작업 별도 저장
- 중요 결정사항 백업
- 압축에 포함할 핵심 정보 추출
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime


def extract_session_summary(project_dir: str) -> str:
    """세션 요약 생성"""
    claude_dir = Path(project_dir) / ".claude"
    summary_parts = []

    # 1. 현재 미완료 작업
    todo_file = claude_dir / "todo.md"
    if todo_file.exists():
        content = todo_file.read_text(encoding="utf-8")
        pending = []
        for line in content.split('\n'):
            if line.strip().startswith('- [ ]'):
                pending.append(line.strip()[6:])  # '- [ ] ' 제거
        if pending:
            summary_parts.append(f"미완료: {', '.join(pending[:5])}")

    # 2. 최근 결정
    decisions_file = claude_dir / "knowledge" / "decisions.md"
    if decisions_file.exists():
        content = decisions_file.read_text(encoding="utf-8")
        # 첫 번째 ## [ 패턴 찾기
        import re
        match = re.search(r'## \[([^\]]+)\] (.+)', content)
        if match:
            summary_parts.append(f"최근결정: [{match.group(1)}] {match.group(2)[:50]}")

    # 3. 현재 집중
    context_file = claude_dir / "knowledge" / "context.md"
    if context_file.exists():
        content = context_file.read_text(encoding="utf-8")
        for line in content.split('\n'):
            if '집중' in line or '현재' in line:
                summary_parts.append(f"집중: {line.strip()[:60]}")
                break

    return " | ".join(summary_parts) if summary_parts else "세션 정보 없음"


def backup_pending_todos(project_dir: str):
    """미완료 작업 context.md에 백업"""
    try:
        claude_dir = Path(project_dir) / ".claude"
        todo_file = claude_dir / "todo.md"
        context_file = claude_dir / "knowledge" / "context.md"

        if not todo_file.exists():
            return

        todo_content = todo_file.read_text(encoding="utf-8")
        pending = []
        for line in todo_content.split('\n'):
            if line.strip().startswith('- [ ]'):
                pending.append(line.strip())

        if not pending:
            return

        # context.md에 백업 섹션 추가
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        backup_section = f"\n\n## Compact 전 백업 ({timestamp})\n" + '\n'.join(pending)

        if context_file.exists():
            content = context_file.read_text(encoding="utf-8")
            # 이전 백업 섹션 제거
            if "## Compact 전 백업" in content:
                content = content.split("## Compact 전 백업")[0].rstrip()
            content += backup_section
            context_file.write_text(content, encoding="utf-8")

    except Exception:
        pass


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        trigger = input_data.get("trigger", "manual")  # "manual" or "auto"

        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

        # 1. 미완료 작업 백업
        backup_pending_todos(project_dir)

        # 2. 세션 요약 생성
        summary = extract_session_summary(project_dir)

        # 3. 압축에 포함할 컨텍스트 반환
        output = {
            "additionalContext": f"[Pre-Compact Summary ({trigger})]\n{summary}\n\n⚠️ 압축 후에도 이 정보는 유지됩니다."
        }
        print(json.dumps(output, ensure_ascii=False))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()