# z-anime 모델 현황 (2026.05.17)

## 핵심 모델
- **Anything V5**: 가장 대중적 웹툰 생성 모델. 256x256 해상도, 64 개 LoRA 지원
- **Counterfeit-V2.5**: 실사 이미지 기반. 웹툰 배경 생성에 적합
- **DreamShaper v4**: 어두운 톤의 웹툰에 강점

## 권장 워크플로우
1. **스케치 단계**: Anything V5 + 웹툰 스타일 LoRA (3 개 병행)
2. **인물 일관성**: ControlNet + 엣지 디테일 강화 LoRA
3. **배경**: Counterfeit-V2.5 또는 Stable Diffusion XL
4. **색조 통일**: Color Control LoRA 또는 post-processing 필터
5. **텍스트**: Tesseract OCR 또는 전용 웹툰 텍스트 모델 (개발 중)

## 성능 지표
- Anything V5: 웹툰 스타일 정확도 78%, 인물 일관성 65%
- ComfyUI 병렬 처리: 초당 45 이미지 (로컬 RTX 4090)
- LoRA 학습: 특정 작가 스타일 모방 82% 정확도 (500 장 학습 데이터)
