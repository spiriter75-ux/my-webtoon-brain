import os
import sys
import json

def main():
    print("=== [INSTAGRAM] 인스타 릴스 바이럴 기획서 생성 ===")
    config_path = os.path.join(os.path.dirname(__file__), "reels_planner.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {"TOPIC": "릴스 주제", "TARGET_LENGTH_SEC": 30, "TONE": "confident"}

    topic = cfg.get("TOPIC", "미지정")
    length = cfg.get("TARGET_LENGTH_SEC", 30)
    tone = cfg.get("TONE", "confident")

    print(f"\n[기획 주제] {topic}")
    print(f"[영상 길이] {length}초")
    print(f"[스타일 톤] {tone}\n")

    print("## 🎬 릴스 스토리보드 (Storyboard)")
    print("1. [0-3초] 🚨 강력한 시각적 훅 (Visual Hook)")
    print(f"   - 화면: 카메라를 정면으로 응시하며 빠른 자막 등장")
    print(f"   - 자막: '아직도 회사 다닌다고요? {topic} 비밀 알려드림'")
    print("2. [3-15초] 📊 핵심 본론 (Core Value)")
    print("   - 화면: 8px 그리드의 대시보드 화면 줌인, 또는 실제 작업 모습")
    print("   - 보이스오버: 데이터를 기반으로 한 명확한 근거 제시")
    print("3. [15-30초] 🎯 행동 촉구 (CTA)")
    print("   - 화면: 프로필 링크 클릭 유도 모션 그래픽")
    print("   - 자막: '댓글로 \'비밀\'을 적어주시면 DM으로 풀버전 링크를 쏩니다!'")
    print("\n[기획 완료] 릴스 촬영을 위한 콘셉트 기획서가 완성되었습니다.\n")

if __name__ == '__main__':
    main()
