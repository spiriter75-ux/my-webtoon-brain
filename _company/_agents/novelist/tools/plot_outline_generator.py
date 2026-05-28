import os
import sys
import json

def main():
    print("=== [NOVELIST] 메가 히트 플롯 및 시나리오 기획 ===")
    base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    config_path = os.path.join(base_dir, "plot_outline_generator.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {"GENRE": "fantasy", "THEME": "천재", "PROTAGONIST_WOUND": "트라우마"}

    genre = cfg.get("GENRE", "fantasy")
    theme = cfg.get("THEME", "미정")
    wound = cfg.get("PROTAGONIST_WOUND", "미정")

    print(f"\n[스토리 장르] {genre}")
    print(f"[스토리 테마] {theme}")
    print(f"[주인공 상처] {wound}\n")

    print("## 📖 3막 구조 및 시나리오 뼈대")
    print("### 1막: 도입부 (Set-up)")
    print(f"  - 주인공의 비루한 현실과 내면적 상처('{wound}')의 단서 표출.")
    print(f"  - 일상을 깨부수는 소환/회귀/각성 사건 발생 -> 테마: {theme}")
    print("### 2막: 전개 및 위기 (Confrontation)")
    print("  - 조력자들과의 만남, 거듭된 사이다 전개로 독자 호감도 및 카타르시스 극대화.")
    print("  - 상처를 다시 건드리는 최대 위기 발생 및 갈등 심화.")
    print("### 3막: 클라이맥스 & 결말 (Resolution)")
    print("  - 내면의 성장을 통해 상처를 완전히 딛고 일어서 최후의 적 격퇴.")
    print("  - 완벽한 대리만족(사이다)과 함께 독자에게 감동을 주는 절벽 엔딩(Next season hook).")
    print("\n[플롯 설계 완료] 스토리 작성을 위한 대리만족 3막 구조 아키텍처가 구축되었습니다.\n")

if __name__ == '__main__':
    main()
