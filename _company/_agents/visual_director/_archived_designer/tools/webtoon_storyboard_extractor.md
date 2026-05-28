# webtoon_storyboard_extractor (웹툰 콘티 추출 및 작화 일괄 생성기)

이 도구는 대용량 소설이나 기획 시나리오를 분석하여 **웹툰 콘티 패널(스토리보드)을 구조적으로 분할 추출**하고, **ComfyUI를 연동하여 패널별 애니메이션 시각 작화까지 일괄로 생성**해주는 고도의 자율 실행기입니다.

---

## 🛠️ 주요 기능

1. **지능형 문맥 슬라이서**: 소설이 아무리 길어도 씬 전환 구분선이나 문맥 흐름을 유지하며 1,600자씩 자동으로 청킹하여 LLM의 오류를 원천 차단합니다.
2. **연속적 패널 넘버링**: 단락 간의 스토리 연속성을 유지하며 패널 시퀀스를 1, 2, 3... 순차 매핑합니다.
3. **ComfyUI 이미지 자동 생성**: 로컬 ComfyUI 서버와 연동하여 각 콘티 패널별 영어 프롬프트를 템플릿에 주입하고 고품질 Z-Anime 작화 이미지를 연속 렌더링합니다.
4. **결과 패키징**: `c:/ai2/comfy_outputs/exports/콘티추출_YYYY-MM-DDTHH-MM-SS/` 폴더에 패널별 `.txt`, `.png` 이미지, 그리고 최종 마스터 `storyboard.json` 및 `storyboard_report.md`를 일괄 생성하여 보관합니다.

---

## ⚙️ 실행 파라미터 (`webtoon_storyboard_extractor.json`)

```json
{
  "NOVEL_TEXT_PATH": "c:\\ai2\\novel.txt",
  "NOVEL_RAW_TEXT": "여기에 소설 텍스트 본문을 직접 붙여넣어도 작동합니다.",
  "OLLAMA_SERVER_URL": "http://127.0.0.1:11434",
  "OLLAMA_MODEL": "qwen3.5:9b",
  "COMFYUI_SERVER_URL": "http://127.0.0.1:8188",
  "GENERATE_IMAGES": true
}
```

* **NOVEL_TEXT_PATH**: 소설 텍스트 파일 경로. 지정되어 있으면 해당 파일의 원본을 우선 로드합니다.
* **NOVEL_RAW_TEXT**: 텍스트 파일이 없을 경우 직접 전달하는 소설 원문 텍스트입니다.
* **OLLAMA_SERVER_URL**: 로컬 Ollama AI 서버 주소. (기본값: `http://127.0.0.1:11434`)
* **OLLAMA_MODEL**: 추출 작업에 사용할 로컬 모델명. (기본값: `qwen3.5:9b` 또는 `qwen2.5:7b`)
* **COMFYUI_SERVER_URL**: 로컬 ComfyUI 서버 주소. (기본값: `http://127.0.0.1:8188`)
* **GENERATE_IMAGES**: 패널별 이미지 작화까지 연동하여 한 번에 생성할지 여부입니다. (기본값: `true`)

---

## 💡 사용 권장 상황

- **소설 삽화 기획 및 시각 콘티 제작**: 소설 원문을 만화나 웹툰 형태의 콘티로 변환하면서 이미지 프롬프트를 얻고 싶을 때.
- **인스타 카드뉴스 및 영상 썸네일 대량 기획**: 시나리오 대본으로부터 다중 비주얼 컷을 일괄로 뽑아낼 때.
- **Gemini API 비용 절감**: 제미나이의 높은 호출 비용을 피하고 로컬 Ollama 모델을 활용해 콘티 기획 연산을 고속으로 로컬 처리하고 싶을 때.
