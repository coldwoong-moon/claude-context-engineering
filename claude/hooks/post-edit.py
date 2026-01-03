#!/usr/bin/env python3
"""PostToolUse:Edit|Write|MultiEdit - 프로젝트별 수정 파일 추적

파일 수정 시 프로젝트의 todo.md에 최근 수정 목록을 자동으로 기록합니다.

개선 사항:
- 최근 10개 항목만 유지 (컨텍스트 오염 방지)
- 같은 파일 중복 방지 (가장 최근 시간으로 업데이트)
- .claude/ 내부 파일은 추적하지 않음
"""
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        file_path = input_data.get("tool_input", {}).get("file_path", "")

        if not file_path:
            sys.exit(0)

        # 프로젝트 디렉토리
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

        # .claude/ 내부 파일은 추적하지 않음
        if "/.claude/" in file_path or file_path.endswith("/.claude"):
            sys.exit(0)

        todo_file = Path(project_dir) / ".claude" / "todo.md"

        # todo.md가 없으면 기록하지 않음
        if not todo_file.exists():
            sys.exit(0)

        content = todo_file.read_text(encoding="utf-8")

        timestamp = datetime.now().strftime("%H:%M")

        # 상대 경로로 변환 (가능한 경우)
        try:
            rel_path = str(Path(file_path).relative_to(project_dir))
        except ValueError:
            rel_path = file_path

        new_entry = f"- `{rel_path}` ({timestamp})"

        # "## 최근 수정" 섹션 처리
        if "## 최근 수정" in content:
            parts = content.split("## 최근 수정", 1)
            before = parts[0]
            after = parts[1].lstrip('\n') if len(parts) > 1 else ""

            # 기존 항목들 파싱
            lines = after.split('\n')
            existing_entries = []
            remaining = []
            in_entries = True

            for line in lines:
                if in_entries and line.startswith("- `"):
                    existing_entries.append(line)
                elif in_entries and (line.startswith("##") or line.startswith("---")):
                    in_entries = False
                    remaining.append(line)
                elif not in_entries:
                    remaining.append(line)
                elif line.strip() == "" and in_entries:
                    continue
                elif in_entries and line.startswith("<!--"):
                    continue
                elif in_entries and not line.startswith("- `"):
                    in_entries = False
                    remaining.append(line)

            # 중복 제거: 같은 파일이 이미 있으면 제거
            filtered_entries = []
            for entry in existing_entries:
                # 경로 추출: - `path` (time) 패턴
                match = re.match(r"- `([^`]+)`", entry)
                if match:
                    existing_path = match.group(1)
                    if existing_path != rel_path:
                        filtered_entries.append(entry)

            # 새 항목 추가 + 최근 9개만 유지 (새 항목 포함 10개)
            all_entries = [new_entry] + filtered_entries[:9]

            # 재구성
            new_content = before + "## 최근 수정\n" + '\n'.join(all_entries)
            if remaining:
                # 빈 줄 정리
                remaining_text = '\n'.join(remaining).strip()
                if remaining_text:
                    new_content += '\n\n' + remaining_text

            content = new_content
        else:
            # 섹션이 없으면 끝에 추가
            content = content.rstrip() + f"\n\n## 최근 수정\n{new_entry}"

        todo_file.write_text(content, encoding="utf-8")

    except Exception:
        pass  # 추적 실패는 무시

    sys.exit(0)


if __name__ == "__main__":
    main()