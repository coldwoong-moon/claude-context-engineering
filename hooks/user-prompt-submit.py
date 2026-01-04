#!/usr/bin/env python3
"""UserPromptSubmit: Ultrathink 철학 기반 사용자 입력 전처리

"Technology alone is not enough. It's technology married with liberal arts."

기능:
- 작업 유형 감지 → 관련 Ultrathink 원칙 주입
- "구현/개발" → Plan Like Da Vinci 리마인드
- "버그/오류" → Obsess Over Details 리마인드
- "리팩토링" → Simplify Ruthlessly 리마인드
- 키워드 기반 knowledge 파일 자동 로드
"""
import json
import os
import re
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# ULTRATHINK PROMPTS - 작업 유형별 철학적 프레이밍
# ═══════════════════════════════════════════════════════════════════════════

ULTRATHINK_PROMPTS = {
    "implementation": """
💡 **Plan Like Da Vinci**: 코드를 쓰기 전, 아키텍처를 스케치하라.
   - 왜 이 방식이어야 하는가?
   - 0에서 시작하면 어떤 모습일까?
   - 가장 우아한 해결책의 형태는?
""",
    "debugging": """
💡 **Obsess Over Details**: 코드의 영혼을 이해하라.
   - 문제의 근본 원인은 무엇인가?
   - 명시된 문제가 진짜 문제인가?
   - 패턴, 철학, 코드의 의도를 읽어라.
""",
    "refactoring": """
💡 **Simplify Ruthlessly**: 더 이상 제거할 것이 없을 때가 우아함이다.
   - 복잡성을 제거하면서 힘을 잃지 않는 방법은?
   - 이 추상화가 정말 필요한가?
   - 코드베이스를 발견했을 때보다 더 나은 상태로 남겨라.
""",
    "feature": """
💡 **Think Different**: 모든 가정에 질문하라.
   - 왜 그렇게 해야 하는가?
   - 더 단순한 방법은 없는가?
   - 사용자의 마음을 노래하게 할 해결책은?
""",
    "review": """
💡 **Iterate Relentlessly**: 첫 번째 버전은 절대 충분하지 않다.
   - 작동하는 것과 '미친 듯이 훌륭한' 것의 차이는?
   - 테스트하고, 비교하고, 다듬어라.
   - 이 코드가 걸작이 될 수 있는가?
"""
}

# 작업 유형 감지 키워드
TASK_KEYWORDS = {
    "implementation": ["구현", "개발", "만들", "생성", "추가", "implement", "develop", "create", "add", "build"],
    "debugging": ["버그", "오류", "에러", "실패", "안됨", "문제", "bug", "error", "fail", "fix", "debug"],
    "refactoring": ["리팩토링", "정리", "개선", "최적화", "refactor", "clean", "improve", "optimize"],
    "feature": ["기능", "피처", "요구사항", "feature", "requirement", "spec"],
    "review": ["리뷰", "검토", "확인", "review", "check", "verify", "test"]
}

# 기존 키워드 → 파일/섹션 매핑 (유지)
KEYWORD_MAPPINGS = {
    "neo4j": ("patterns.md", "Cypher"),
    "cypher": ("patterns.md", "Cypher"),
    "그래프": ("patterns.md", "Cypher"),
    "쿼리": ("patterns.md", "Cypher"),
    "query": ("patterns.md", "Cypher"),

    "오류": ("errors.md", None),
    "에러": ("errors.md", None),
    "error": ("errors.md", None),
    "실패": ("errors.md", None),
    "failed": ("errors.md", None),

    "결정": ("decisions.md", None),
    "아키텍처": ("decisions.md", None),
    "설계": ("decisions.md", None),
    "decision": ("decisions.md", None),

    "패턴": ("patterns.md", None),
    "pattern": ("patterns.md", None),
    "코드": ("patterns.md", "Python"),

    "연구": ("context.md", None),
    "rq": ("context.md", None),
    "research": ("context.md", None),
}


def detect_task_type(prompt: str) -> str | None:
    """프롬프트에서 작업 유형 감지"""
    prompt_lower = prompt.lower()

    for task_type, keywords in TASK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in prompt_lower:
                return task_type
    return None


def extract_section(content: str, section_name: str) -> str:
    """특정 섹션만 추출"""
    pattern = rf"## {section_name}.*?(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(0).strip() if match else ""


def find_relevant_context(prompt: str, claude_dir: Path) -> list[str]:
    """프롬프트 분석하여 관련 컨텍스트 찾기"""
    prompt_lower = prompt.lower()
    context_parts = []
    loaded_files = set()

    for keyword, (filename, section) in KEYWORD_MAPPINGS.items():
        if keyword in prompt_lower and filename not in loaded_files:
            filepath = claude_dir / "knowledge" / filename
            if filepath.exists():
                content = filepath.read_text(encoding="utf-8")
                if section:
                    extracted = extract_section(content, section)
                    if extracted:
                        context_parts.append(f"[{filename} - {section}]\n{extracted[:800]}")
                else:
                    context_parts.append(f"[{filename}]\n{content[:1000]}")
                loaded_files.add(filename)

    return context_parts


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        prompt = input_data.get("prompt", "")

        if not prompt:
            sys.exit(0)

        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        claude_dir = Path(project_dir) / ".claude"
        context_parts = []

        # 1. Ultrathink 철학 주입 (작업 유형 기반)
        task_type = detect_task_type(prompt)
        if task_type and task_type in ULTRATHINK_PROMPTS:
            context_parts.append(ULTRATHINK_PROMPTS[task_type])

        # 2. 관련 knowledge 파일 로드
        if claude_dir.exists():
            relevant = find_relevant_context(prompt, claude_dir)
            context_parts.extend(relevant)

        if context_parts:
            output = {
                "additionalContext": "\n\n---\n\n".join(context_parts)
            }
            print(json.dumps(output, ensure_ascii=False))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()