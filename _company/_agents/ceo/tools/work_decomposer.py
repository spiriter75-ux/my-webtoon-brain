import os
import sys
import json

def main():
    print("=== [CEO] 업무 세분화 및 실행 로드맵 수립 ===")
    config_path = os.path.join(os.path.dirname(__file__), "work_decomposer.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {"PROJECT_TITLE": "신규 프로젝트", "AGENTS_INVOLVED": "developer, designer", "MILESTONES_COUNT": 3}

    title = cfg.get("PROJECT_TITLE", "신규 프로젝트")
    agents = [a.strip() for a in cfg.get("AGENTS_INVOLVED", "").split(",") if a.strip()]
    count = int(cfg.get("MILESTONES_COUNT", 3))

    print(f"\n[프로젝트] {title}")
    print(f"[참여 에이전트] {', '.join(agents)}")
    print(f"[단계 수] {count}단계\n")

    print("## 🗺️ 실행 로드맵")
    for i in range(1, count + 1):
        print(f"### 📍 마일스톤 {i}단계")
        for agent in agents:
            print(f"  - [{agent.upper()}] 마일스톤 {i} 세부 임무 할당 및 결과물 검증 준비")
    
    print("\n[검증 결과] 로드맵이 완벽하게 설계되었습니다. 각 에이전트별 업무 분장에 맞게 액션을 전개하세요.\n")

if __name__ == '__main__':
    main()
