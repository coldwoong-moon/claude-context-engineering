---
description: 애플리케이션 검증 워크플로우 (lint, test, build)
argument-hint: [--skip-tests] [--skip-build]
---

애플리케이션 검증 워크플로우

## 사전 정보 수집

```bash
# 패키지 매니저 감지
if [ -f "package.json" ]; then
    PKG_MANAGER="npm"
    [ -f "pnpm-lock.yaml" ] && PKG_MANAGER="pnpm"
    [ -f "yarn.lock" ] && PKG_MANAGER="yarn"
    [ -f "bun.lockb" ] && PKG_MANAGER="bun"
elif [ -f "pyproject.toml" ]; then
    PKG_MANAGER="uv"
elif [ -f "Cargo.toml" ]; then
    PKG_MANAGER="cargo"
fi
echo "Package Manager: $PKG_MANAGER"
```

## 검증 단계

### 1. 린터/포매터
```bash
# JavaScript/TypeScript
$PKG_MANAGER run lint
$PKG_MANAGER run format:check

# Python
uv run ruff check .
uv run ruff format --check .

# Rust
cargo fmt --check
cargo clippy
```

### 2. 타입 체크
```bash
# TypeScript
$PKG_MANAGER run typecheck

# Python
uv run mypy .
```

### 3. 테스트
```bash
# JavaScript/TypeScript
$PKG_MANAGER run test

# Python
uv run pytest

# Rust
cargo test
```

### 4. 빌드
```bash
# JavaScript/TypeScript
$PKG_MANAGER run build

# Python (패키지)
uv build

# Rust
cargo build --release
```

## 결과 보고

각 단계의 결과를 요약하고 실패 시 원인 분석 제공.

## 사용 예시

```
/verify-app
/verify-app --skip-tests
/verify-app --only lint,typecheck
```
