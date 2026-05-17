import os
import sys
import json

def main():
    print("=== [DESIGNER] 프리미엄 브랜드 컬러 팔레트 생성 ===")
    config_path = os.path.join(os.path.dirname(__file__), "color_palette_generator.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {"BASE_COLOR": "#22d3ee", "STYLE": "sleek-dark", "CSS_PREFIX": "brand"}

    base = cfg.get("BASE_COLOR", "#22d3ee")
    style = cfg.get("STYLE", "sleek-dark")
    prefix = cfg.get("CSS_PREFIX", "brand")

    print(f"\n[기준 색상] {base}")
    print(f"[디자인 스타일] {style}")
    print(f"[CSS 접두사] --{prefix}-\n")

    print("## 🎨 CSS Variables Output")
    print(":root {")
    if style == 'sleek-dark':
        print(f"  --{prefix}-primary: {base};")
        print(f"  --{prefix}-bg: #0F172A; /* Slate 900 */")
        print(f"  --{prefix}-card: #1E293B; /* Slate 800 */")
        print(f"  --{prefix}-text: #F8FAFC; /* Slate 50 */")
        print(f"  --{prefix}-muted: #64748B; /* Slate 500 */")
        print(f"  --{prefix}-accent: #EC4899; /* Pink 500 */")
    elif style == 'glassmorphism':
        print(f"  --{prefix}-primary: {base};")
        print(f"  --{prefix}-bg: radial-gradient(circle, #1e1b4b, #090514);")
        print(f"  --{prefix}-glass: rgba(255, 255, 255, 0.05);")
        print(f"  --{prefix}-border: rgba(255, 255, 255, 0.1);")
        print(f"  --{prefix}-text: #FFFFFF;")
    else:
        print(f"  --{prefix}-primary: {base};")
        print(f"  --{prefix}-bg: #FAFAF9; /* Stone 50 */")
        print(f"  --{prefix}-text: #1C1917; /* Stone 900 */")
    print("}")
    
    print("\n[출력 완료] 브랜드 컬러 팔레트가 CSS 변수 규격으로 깔끔하게 제정되었습니다.\n")

if __name__ == '__main__':
    main()
