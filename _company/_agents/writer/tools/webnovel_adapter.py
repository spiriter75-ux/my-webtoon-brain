import os
import sys
import json

# Windows 환경에서 한글 및 이모지 출력 시 UnicodeEncodeError(CP949) 방지
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass # 파이썬 구버전 대응

def main():
    print("=== [WRITER] 한국형 웹툰 각색 시나리오 제너레이터 실행 ===")
    
    config_path = os.path.join(os.path.dirname(__file__), "webnovel_adapter.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {"TARGET_PLATFORM": "Naver Webtoon", "GENRE": "Fantasy Romance", "EPISODE_NUMBER": 1}

    platform = cfg.get("TARGET_PLATFORM", "Naver Webtoon")
    genre = cfg.get("GENRE", "Fantasy Romance")
    episode = cfg.get("EPISODE_NUMBER", 1)

    print(f"\n[타겟 플랫폼] {platform}")
    print(f"[아트워크 장르] {genre}")
    print(f"[각색 진행 회차] {episode}화\n")

    print("✨ 한국형 웹툰 모바일 스크롤 최적화 각색 작업 중...")
    print("--------------------------------------------------")
    
    if genre == "Fantasy Romance":
        print(f"## 👸 로맨스 판타지 K-웹툰 각색 시나리오 (제 {episode}화)")
        print("\n[씬 1] 황궁 연회장 내부 (세로 스크롤 최적 연출)")
        print("  - [시각 연출 지문]: 샹들리에의 화려한 불빛이 쏟아져 내리는 연회장.")
        print("  - [스크롤 흐름]: 서서히 앵글이 내려오며, 연회장의 사람들을 한눈에 담는다.")
        print("  - [인물 대사] 👑 아리엘: (잔을 가볍게 쥐며, 조소 띤 미소로)")
        print("    > \"결국... 이 날이 오고야 말았군.\"")
    elif genre == "Modern Fantasy":
        print(f"## ⚔️ 현대 판타지 K-웹툰 각색 시나리오 (제 {episode}화)")
        print("\n[씬 1] 게이트 내부 몬스터 던전 (스피디한 세로 연출)")
        print("  - [시각 연출 지문]: 어두운 동굴 벽을 타고 흘러내리는 끈적한 점액질.")
        print("  - [스크롤 흐름]: 주인공의 발걸음을 따라 카메라가 빠르게 아래로 하강.")
        print("  - [상태창 이펙트]: 🔷 [알림: 던전 보스 '네크로맨서'가 각성합니다.]")
        print("  - [인물 대사] 🗡️ 진우: (검을 굳게 쥐며 코웃음 친다)")
        print("    > \"여기서 끝낼 순 없어. 덤벼라!\"")
    else:
        print(f"## 👊 소년/액션 K-웹툰 각색 시나리오 (제 {episode}화)")
        print("\n[씬 1] 골목길 전투 씬 (컷 가독성 극대화)")
        print("  - [시각 연출 지문]: 비에 젖은 어두운 아스팔트 골목길.")
        print("  - [스크롤 흐름]: 빗방울이 떨어지는 짧은 컷들의 배치 후, 타격 씬에서의 롱 스크롤 전환.")
        print("  - [인물 대사] 🥊 강혁: (주먹을 풀며)")
        print("    > \"더 이상 물러설 곳은 없다.\"")

    print("--------------------------------------------------")
    print(f"✅ [각색 완료] {platform} 최적화 {genre} 웹툰 콘티 각색 시나리오 변환을 마쳤습니다.\n")

if __name__ == '__main__':
    main()
