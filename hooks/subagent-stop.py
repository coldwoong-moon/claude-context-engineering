#!/usr/bin/env python3
"""SubagentStop: 서브에이전트 완료 시 결과 검증

2025-12 신규 Hook - 서브에이전트(Task tool) 완료 시 트리거

기능:
- 8개 이상 항목 나열 시 경고 (날조 임계점)
- 결과 품질 간단 검증
- 완료된 작업을 todo.md에 기록
"""
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime


def count_list_items(text: str) -> int:
    """텍스트에서 리스트 항목 수 세기"""
    patterns = [
        r'^[-*+]\s+',           # - item, * item, + item
        r'^\d+\.\s+',           # 1. item, 2. item
        r'^[a-z]\)\s+',         # a) item, b) item
    ]
    lines = text.split('\n')
    count = 0
    for line in lines:
        for pattern in patterns:
            if re.match(pattern, line.strip()):
                count += 1
                break
    return count


def detect_fabrication_risk(result: str) -> dict:
    """날조 위험 감지"""
    list_count = count_list_items(result)

    if list_count >= 10:
        return {
            "risk": "HIGH",
            "message": f"⚠️ 경고: {list_count}개 항목 나열됨 (임계점: 8개). 검증 필요!",
            "action": "verify"
        }
    elif list_count >= 8:
        return {
            "risk": "MEDIUM",
            "message": f"⚠️ 주의: {list_count}개 항목 나열됨. 정확성 확인 권장.",
            "action": "review"
        }
    return {"risk": "LOW", "message": "", "action": "none"}


def log_subagent_completion(agent_name: str, project_dir: str):
    """서브에이전트 완료를 todo.md에 기록"""
    try:
        todo_file = Path(project_dir) / ".claude" / "todo.md"
        if not todo_file.exists():
            return

        content = todo_file.read_text(encoding="utf-8")
        timestamp = datetime.now().strftime("%H:%M")

        # "## 최근 수정" 섹션에 서브에이전트 완료 기록
        entry = f"- `[Agent: {agent_name}]` ({timestamp})"

        if "## 최근 수정" in content:
            parts = content.split("## 최근 수정", 1)
            new_content = parts[0] + "## 최근 수정\n" + entry + "\n" + parts[1].lstrip('\n')
            todo_file.write_text(new_content, encoding="utf-8")
    except Exception:
        pass


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        # 서브에이전트 정보
        agent_type = input_data.get("agent_type", "unknown")
        result = input_data.get("result", "")

        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

        # 1. 날조 위험 감지
        risk = detect_fabrication_risk(result)

        # 2. 완료 기록
        log_subagent_completion(agent_type, project_dir)

        # 3. 경고 출력
        if risk["risk"] != "LOW":
            output = {"additionalContext": risk["message"]}
            print(json.dumps(output, ensure_ascii=False))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()