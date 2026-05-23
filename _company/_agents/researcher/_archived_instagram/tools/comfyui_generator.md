# 🎨 ComfyUI Studio 이미지 생성기 (Z-Anime-Workflow)

ComfyUI API를 활용하여 로컬 또는 원격 ComfyUI 서버에서 `Z-Anime-Workflow.json` 워크플로우에 기반한 초고화질 애니메이션 캐릭터 일러스트를 생성합니다.
에이전트가 웹툰 콘티 연출, 디자인 콘셉트 시각화, 소셜 미디어 피드 구성(인스타그램) 등의 작업을 진행할 때, 텍스트 묘사를 바탕으로 즉시 고품질 이미지를 생성하고 그 결과 경로를 확보할 수 있습니다.

## ⚙️ 매개변수 설정 (comfyui_generator.json)
- **COMFYUI_SERVER_URL**: ComfyUI API URL (기본값: `http://127.0.0.1:8188`)
- **POSITIVE_PROMPT**: 생성할 이미지에 들어갈 캐릭터, 머리색, 구도, 장신구 등을 영어 프롬프트로 묘사합니다.
- **NEGATIVE_PROMPT**: 제외하고 싶은 퀄리티 저하 요소, 기형적 표현 등 (기본값: `blurry, low quality, deformed, bad anatomy, bad hands, extra limbs`).
- **SEED**: 무작위 이미지 생성을 위해 `-1`을 입력하거나, 특정 시드 번호로 고정합니다.

## 💾 결과물 저장 경로
생성 완료 후 이미지 파일은 `c:\ai2\comfy_outputs\` 폴더에 `Z-Anime-Upscale_XXXXX_.png` 포맷으로 자동 다운로드되어 저장됩니다.
도구 실행 성공 시 출력문 끝부분의 `RESULT_PATH: <경로>`와 `SEED_USED: <시드>` 값을 캡처하여 확인 및 활용하세요.
