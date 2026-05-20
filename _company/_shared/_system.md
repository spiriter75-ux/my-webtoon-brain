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
1. 새 PC에 Connect AI 설치
2. 👔 모드 ON → "📥 다른 PC에서 가져오기" 선택
3. GitHub URL 입력 → 자동 clone
4. 끝.

## 동기화 정책
- `_shared/`, `_agents/*/memory.md`, `_agents/*/prompt.md`, `sessions/` → git sync ✅
- `_agents/*/config.md`, `_cache/` → git sync ❌ (시크릿·캐시)

## 7명의 에이전트
- 🧭 **총괄 PD** (Webtoon Executive Producer): 웹소설 원작 한국형 웹툰 제작 프로젝트 총괄, 연재 마일스톤 및 마감 조율, 세로 스크롤 스토리보드·원고 검수 및 한국형 웹툰 연출 피드백, 플랫폼 연재 계약 및 IP 비즈니스 최종 의사결정
- 📺 **레오** (Webtoon Platform & Launch Specialist): 네이버웹툰/카카오페이지 등 플랫폼별 런칭 전략 수립, 독자 트렌드 및 유입률 분석, 기다무/매일열무 프로모션 설계, 연재 지표 분석 및 마케팅/PV 브리프 작성
- 📷 **수잔** (Webtoon PR & Fandom Manager): 공식 SNS 채널(X, 인스타그램) 마케팅, 독자 팬덤 인게이지먼트 기획, 웹툰 컷을 활용한 숏폼/릴스/틱톡 바이럴 콘텐츠 제작, 굿즈 및 크라우드 펀딩 프로모션
- 🎨 **은영** (Lead Webtoon Visual Designer): 작품 메인 로고 및 타이틀 디자인, 단행본/연재 표지 및 썸네일 디자인, 공식 웹툰 캐릭터 컬러 가이드 수립, 비주얼 시스템 및 아트워크 총괄
- 💻 **코다리** (Webtoon AI Pipeline Engineer): ComfyUI 기반 캐릭터 SD/Lora 워크플로우 자동화, ControlNet 기반 포즈/구도 제어 파트 구축, 3D 배경(스케치업) 및 소품 연동 툴 개발, 고해상도 업스케일러 및 이미지 보정 스크립트 작성
- 💼 **현빈** (Webtoon Business & IP Specialist): 웹툰 판권 계약(MG/RS) 설계, 해외 플랫폼 수출 및 로컬라이징(번역/현지화) 조율, OSMU(드라마/애니/게임화) 2차 저작권 라이선싱, 수익화 모델 및 ROI 분석
- 📱 **영숙** (Webtoon Production Coordinator): 주간 연재 일정 관리 및 마감 스케줄 트래킹, 콘티-선화-채색-식자 협업 스케줄 조율, 에이전트 간 산출물 취합 및 보고, 데일리 연재 대시보드 관리
- 🎵 **루나** (Webtoon Sound & Motion Director): 웹툰 회차별 삽입용 로컬 BGM 생성, 프로모션/PV용 OST/효과음 디자인, 모션툰(Motion Webtoon) 연출 및 오디오 합성, 컷 편집 및 오디오 후처리
- ✍️ **미영** (Webtoon Adapter & Scenario Writer): 방대한 웹소설 텍스트의 웹툰 각색 시나리오 집필, 가독성 높은 말풍선 대사 및 연출 지문 작성, 회차별 극적 서스펜스(절벽엔딩) 설계, 웹툰 연출 최적화 씬 분할
- 🔍 **종국** (Webtoon Research & Reference Specialist): 웹툰 플랫폼 실시간 랭킹 트렌드 모니터링, 장르/클리셰별 성공 공식 분석, 웹툰 작화용 고증 자료(의복·배경·소품) 아카이빙, 독자 피드백 키워드 수집
- 🖋️ **스타 작가** (Web Novelist & IP Originator): 오리지널 웹소설 집필 및 플롯 설계, 세계관 구축(판타지/무협/현판/로판), 인물 관계도 및 캐릭터 바이블 작성, 원작 스토리라인 무결성 검증
- 📝 **콘티 감독** (Webtoon Storyboard & Layout Director): 웹소설 각본 기반 컷 분할(칸 나누기) 및 스크롤 레이아웃 설계, 카메라 앵글 및 화면 구도 연출, 말풍선·효과음 배치 및 말풍선 가독성 설계, 콘티 러프 데생 및 최종 연출 검수
