# 🧬 1인 기업 OS — 자가 매뉴얼

## 이 폴더는 무엇인가요?
당신의 1인 기업의 두뇌입니다. 7명의 AI 에이전트가 여기서 일합니다.

## 폴더 구조
- `_shared/` — 모든 에이전트가 매번 읽는 공동 메모리
  - `identity.md` — 회사 정체성 (이름, 톤, 가치)
  - `goals.md` — 목표
  - `decisions.md` — 의사결정 로그 (자가학습이 자동 누적)
  - `_system.md` — 이 파일
- `_agents/<id>/` — 각 에이전트 개인 공간
  - `memory.md` — 자가학습 (자동, append-only)
  - `prompt.md` — 페르소나 디테일 (사용자가 편집)
  - `config.md` — API 키·시크릿 (`.gitignore`로 보호)
- `sessions/<ts>/` — 세션별 산출물 (자동)
- `_cache/` — API 응답 캐시 (sync 제외)

## 메모리 위계 (충돌 시 우선순위)
1. `decisions.md` — 가장 강한 신뢰
2. `identity.md`
3. `goals.md`
4. 개인 메모리
5. 지식 베이스 (`10_Wiki/`)

## 다른 PC로 옮길 때
1. 새 PC에 My Webtoon AI 설치
2. 👔 모드 ON → "📥 다른 PC에서 가져오기" 선택
3. GitHub URL 입력 → 자동 clone
4. 끝.

## 동기화 정책
- `_shared/`, `_agents/*/memory.md`, `_agents/*/prompt.md`, `sessions/` → git sync ✅
- `_agents/*/config.md`, `_cache/` → git sync ❌ (시크릿·캐시)

## 7명의 에이전트
- 🧭 **스튜디오 매니저** (Studio Executive Agent): 웹툰 제작 프로세스 오케스트레이션, 작업 분해, 마감 관리, 최종 검수
- ✍️ **스토리 작가** (Lead Story Writer): 시놉시스, 캐릭터 설정, 회차별 시나리오, 대사 최적화, 세계관 구축
- 📋 **콘티 작가** (Storyboard Artist): 시나리오 기반 연출, 컷 분할, 구도 설계, 말풍선 배치, 가이드 데생
- 🎨 **배경/소품 디자이너** (Asset & BG Designer): 스케치업 배경 모델링, 소품 디자인, 컬러 팔레트 설계, 텍스처링
- 💻 **기술 지원 (코다리)** (Technical Support & Automation): 제작 자동화 스크립트, 이미지 처리 도구, 데이터 관리, AI 툴 통합
- 📱 **총무 영숙** (Production Coordinator): 일정 관리, 마감 알림, 자료 정리, 팀원 간 소통 조율
- 🔍 **자료 조사관** (Trend & Reference Researcher): 고증 자료 수집, 트렌드 분석, 레퍼런스 이미지 검색, 소재 리서치
