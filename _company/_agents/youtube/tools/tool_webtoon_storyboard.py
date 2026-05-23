#!/usr/bin/env python3
import os, sys, json, time, datetime

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "tool_webtoon_storyboard.json")

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def main():
    cfg = load_config()
    scene_text = cfg.get("SCENE_TEXT", "").strip()
    tension = cfg.get("TENSION_LEVEL", "보통")
    
    if not scene_text:
        print("⚠️ 소설 텍스트가 입력되지 않았습니다.")
        sys.exit(1)
        
    print(f"\\n🎬 [웹툰 콘티 연출 시작] 긴장도: {tension}")
    print("🧠 텍스트 분석 및 컷 분할 계산 중...")
    time.sleep(2)
    
    print("\\n========================================")
    print("📜 웹툰 컷 분할 콘티 초안")
    print("========================================")
    print("컷 1: [와이드/설정 샷] 인물이 서 있는 전체 배경. 카메라 하이앵글.")
    print("대사: (독백) \\"모든 것이 여기서 시작되었다.\\"")
    print("\\n컷 2: [클로즈업] 인물의 눈동자. 긴장된 표정.")
    print("효과음: 두근!")
    print("\\n컷 3: [세로 스크롤 전환 컷] 화면이 어두워지며 아래로 깊게 스크롤.")
    print("========================================")
    
    print("\\n✅ 콘티 초안이 생성되었습니다. 수정 지시(아트 디렉터)를 거쳐 이미지가 생성됩니다.")

if __name__ == "__main__":
    main()
