#!/usr/bin/env python3
"""Cross-Platform Hook Runner - 크로스 플랫폼 훅 실행기

Windows, macOS, Linux에서 동일하게 동작하는 hook 실행기입니다.

사용법:
    python run-hook.py <hook-name>
    python run-hook.py magic-keywords
    python run-hook.py session-recovery

이 스크립트는 settings.json에서 사용됩니다:
    Windows: python "%USERPROFILE%\\.claude\\hooks\\run-hook.py" <hook-name>
    Unix:    python ~/.claude/hooks/run-hook.py <hook-name>
"""
import os
import sys
import importlib.util
from pathlib import Path


def get_hooks_dir() -> Path:
    """hooks 디렉토리 경로 반환"""
    return Path(__file__).parent.resolve()


def run_hook(hook_name: str) -> int:
    """지정된 hook 실행

    Args:
        hook_name: hook 파일명 (확장자 제외)

    Returns:
        종료 코드
    """
    hooks_dir = get_hooks_dir()
    hook_file = hooks_dir / f"{hook_name}.py"

    if not hook_file.exists():
        print(f"Error: Hook not found: {hook_file}", file=sys.stderr)
        return 1

    try:
        # 동적으로 hook 모듈 로드 및 실행
        spec = importlib.util.spec_from_file_location(hook_name, hook_file)
        if spec is None or spec.loader is None:
            print(f"Error: Cannot load hook: {hook_file}", file=sys.stderr)
            return 1

        module = importlib.util.module_from_spec(spec)
        sys.modules[hook_name] = module
        spec.loader.exec_module(module)

        # main() 함수가 있으면 실행
        if hasattr(module, "main"):
            module.main()

        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 0
    except Exception as e:
        print(f"Error running hook {hook_name}: {e}", file=sys.stderr)
        return 1


def main():
    if len(sys.argv) < 2:
        print("Usage: python run-hook.py <hook-name>", file=sys.stderr)
        print("Example: python run-hook.py magic-keywords", file=sys.stderr)
        sys.exit(1)

    hook_name = sys.argv[1]

    # .py 확장자가 있으면 제거
    if hook_name.endswith(".py"):
        hook_name = hook_name[:-3]

    exit_code = run_hook(hook_name)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
