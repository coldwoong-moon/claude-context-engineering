# Context Engineering 사용법

## 빠른 시작

### 설치

```bash
# 저장소 클론
git clone https://github.com/your-repo/claude-context-engineering.git
cd claude-context-engineering

# 설치 (hooks + settings)
python scripts/setup.py install

# 설치 확인
python scripts/setup.py doctor
```

### 핵심 매직 키워드

대화 중 다음 키워드를 사용하면 해당 모드가 활성화됩니다:

| 키워드 | 기능 | 사용 예시 |
|--------|------|----------|
| `스펙:` | 구현 전 스펙 세분화 | `스펙: 사용자 로그인 기능` |
| `원자화:` | 작업을 작은 단위로 분해 | `원자화: API 엔드포인트 추가` |
| `연구:` | 심층 연구 (학술 + 웹) | `연구: React Server Components` |
| `리뷰:` | 비판적 코드 리뷰 | `리뷰: src/auth/` |
| `루프:` | 목표 달성까지 연속 실행 | `루프: 테스트 커버리지 80% 달성` |
| `gemini:` | 대규모 분석 위임 | `gemini: 전체 코드베이스 패턴 분석` |

---

## 주요 워크플로우

### 1. 스펙 우선 개발 (권장)

새 기능 구현 전 반드시 스펙부터:

```
스펙: 사용자 인증 기능 추가
```

**자동 실행 단계:**
1. 요구사항 추출 (명시적 + 암묵적)
2. 설계 분석 (기존 패턴, 영향, 리스크)
3. 작업 원자화 (≤3 파일, ≤30분 단위)
4. 승인 후 구현

### 2. 연속 실행 모드

목표 달성까지 자동 반복:

```
루프: 모든 TODO 주석 해결
```

또는 스크립트로:

```bash
./scripts/continuous-claude.sh "테스트 커버리지 80% 달성" --max-runs 10
```

### 3. 멀티 AI 오케스트레이션

작업 특성에 따른 AI 분배:

| 상황 | 사용할 AI | 키워드 |
|------|----------|--------|
| 대규모 코드 분석 | Gemini CLI | `gemini:` |
| 빠른 프로토타입 | Codex CLI | `codex:` |
| 복잡한 추론/리뷰 | Claude (기본) | - |

예시:
```
gemini: src/ 디렉토리 전체에서 보안 취약점 분석
```

### 4. 심층 연구 모드

학술 논문 + 웹 리서치:

```
연구: GraphQL vs REST 2024 비교 분석
```

---

## 자동화된 기능

### 진화 피드백 루프

세션 종료 시 자동으로:
- 작업 메트릭 수집
- 예측 vs 실제 비교
- 패턴 학습 및 저장
- 개선 권장사항 제시

저장 위치: `.claude/knowledge/evolution/`

### 스펙 체크 훅

중요한 파일 수정 시:
- 활성 스펙 존재 여부 확인
- 없으면 스펙 작성 권장
- 세션당 1회만 알림

### 품질 게이트

각 작업 완료 후:
- [ ] Lint/타입 체크
- [ ] 테스트 통과
- [ ] 보안 취약점 검사
- [ ] 스펙 일치 확인

---

## 디렉토리 구조

```
claude/
├── CLAUDE.md           # 진입점 (핵심 원칙 + 매직 키워드)
├── USAGE.md            # 이 파일
│
├── commands/           # 슬래시 명령어
│   ├── spec.md         # /spec - 스펙 워크플로우
│   ├── research.md     # /research - 연구 모드
│   ├── continuous.md   # /continuous - 연속 실행
│   └── ...
│
├── hooks/              # 자동화 훅
│   ├── evolution-feedback.py  # 진화 피드백
│   ├── spec-check.py          # 스펙 체크
│   ├── magic-keywords.py      # 매직 키워드
│   └── ...
│
├── agents/             # 서브에이전트
│   ├── oracle.md       # 심층 분석
│   └── librarian.md    # 증거 조사
│
└── settings.json       # Claude Code 설정
```

---

## 팁

### 효율적인 작업

1. **스펙부터**: 큰 기능은 `스펙:`으로 시작
2. **원자 단위**: 작업은 ≤3 파일, ≤30분 단위로
3. **증거 기반**: 주장에는 파일:라인 참조
4. **진화 활용**: 세션 종료 시 피드백 확인

### 문제 해결

```bash
# 설치 진단
python scripts/setup.py doctor

# 훅 테스트
python ~/.claude/hooks/magic-keywords.py

# 로그 확인
cat .claude/knowledge/evolution/session-metrics.json
```

### 커스터마이징

- 매직 키워드 추가: `hooks/magic-keywords.py`
- 새 명령어: `commands/` 디렉토리에 `.md` 파일 추가
- 품질 게이트 수정: `hooks/` 훅 파일 수정

---

## 참고 문서

- [SPEC-ATOMIZATION.md](./SPEC-ATOMIZATION.md) - 스펙 세분화 상세
- [MULTI-AI-ORCHESTRATION.md](./MULTI-AI-ORCHESTRATION.md) - 멀티 AI 조율
- [CONTINUOUS-CLAUDE.md](./CONTINUOUS-CLAUDE.md) - 연속 실행 시스템
- [RESEARCH-MODE.md](./RESEARCH-MODE.md) - 심층 연구 모드
