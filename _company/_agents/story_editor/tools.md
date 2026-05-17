# 📑 story_editor — 도구 매니페스트

_story_editor 에이전트가 어떤 도구를 어디까지 자율적으로 쓸 수 있는지 정의합니다._

---

## 자율도 레벨

AUTONOMY_LEVEL: 2

| 값 | 의미 |
|---|---|
| 0 | Off — 도구 전체 비활성 |
| 1 | Read-only — 읽기·분석·보고만 |
| 2 | Draft — 초안 작성 후 사용자 승인 필요 |
| 3 | Auto — 사용자 승인 없이 실행 |

---

## 사용 가능한 도구

_⚠️ 이 에이전트의 도구는 모두 로드맵 단계입니다._

### `grammar_check` _(예정)_
맞춤법 및 문장 교정

### `market_analyzer` _(예정)_
작품의 키워드 기반 시장성 분석

---

## 안전 규칙

- 외부 행동은 `_agents/story_editor/activity.log`에 기록.
- 승인 대기 액션은 `approvals/pending/` 에 저장.
