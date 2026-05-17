import os
import sys
import json

def main():
    print("=== [WRITER] 고전환 마케팅 카피라이팅 생성 ===")
    config_path = os.path.join(os.path.dirname(__file__), "copywriter_generator.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {"PRODUCT_NAME": "상품", "BENEFITS": "장점", "FRAMEWORK": "PAS"}

    name = cfg.get("PRODUCT_NAME", "상품")
    benefits = cfg.get("BENEFITS", "장점")
    framework = cfg.get("FRAMEWORK", "PAS")

    print(f"\n[상품명] {name}")
    print(f"[핵심 혜택] {benefits}")
    print(f"[프레임워크] {framework}\n")

    print(f"## 💎 {framework} 마케팅 카피셋")
    if framework == "PAS":
        print("1. [Problem - 문제 제기]")
        print("  > 매일 잠잘 시간도 없이 비즈니스 기획, 유튜브, 디자인에 시달리고 계신가요?")
        print("2. [Agitate - 감정 자극]")
        print("  > 혼자서 다 하려니 시간은 없고, 전문 외주를 맡기자니 비용이 수백만 원씩 깨져 스트레스가 폭발 직전일 겁니다.")
        print("3. [Solve - 해결책 제시]")
        print(f"  > 이제 걱정 끝! 단 하나의 솔루션, '{name}'으로 해결하세요. {benefits}!")
    else:
        print("1. [Attention - 주의 끄기]")
        print(f"  > 하루 딱 10분만 쓰고 매출 3배 올리는 치트키가 나타났습니다!")
        print("2. [Interest - 흥미 유발]")
        print(f"  > AI 비서들이 사장님의 의도를 찰떡같이 이해하고 일하는 모습을 상상해보세요.")
        print("3. [Desire - 욕구 자극]")
        print(f"  > 시간은 벌고, 퀄리티는 극대화됩니다. 외주 비용은 0원!")
        print(f"4. [Action - 행동 유도]")
        print(f"  > 지금 바로 '{name}'을 신청하시고 자율 주행 비즈니스의 첫 발을 떼세요!")
    
    print("\n[카피 완성] 구매율을 폭발적으로 증가시킬 카피라이팅이 준비되었습니다.\n")

if __name__ == '__main__':
    main()
