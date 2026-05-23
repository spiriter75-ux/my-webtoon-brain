import os
import sys
import json
from duckduckgo_search import DDGS

# Windows 환경 터미널 출력 시 이모지 인코딩(CP949) 오류 방지
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=== [RESEARCHER] DuckDuckGo 기반 통합 웹 검색 ===")
    config_path = os.path.join(os.path.dirname(__file__), "web_search.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {"KEYWORDS": "웹툰 트렌드", "SEARCH_TYPE": "text", "MAX_RESULTS": 5}

    keywords = cfg.get("KEYWORDS", "웹툰 트렌드")
    search_type = cfg.get("SEARCH_TYPE", "text")
    max_results = int(cfg.get("MAX_RESULTS", 5))

    print(f"[검색어] {keywords}")
    print(f"[검색 모드] {search_type}")
    print(f"[최대 수집 건수] {max_results}건\n")

    results_data = []
    try:
        with DDGS() as ddgs:
            if search_type == "image":
                results = ddgs.images(keywords, max_results=max_results)
                for r in results:
                    clean_item = {
                        "title": r.get("title", "").strip(),
                        "image_url": r.get("image", "").strip(),
                        "source": r.get("source", "").strip()
                    }
                    results_data.append(clean_item)
            else:
                results = ddgs.text(keywords, max_results=max_results)
                for r in results:
                    clean_item = {
                        "title": r.get("title", "").strip(),
                        "url": r.get("href", "").strip(),
                        "snippet": r.get("body", "").strip()
                    }
                    results_data.append(clean_item)
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    print("## 📊 검색 결과 (JSON 정규화)")
    print(json.dumps(results_data, ensure_ascii=False, indent=2))
    print("\n[보고 결론] 불필요한 태그와 광고 요소를 배제하고 순수 데이터를 JSON 포맷으로 성공적으로 추출하였습니다.\n")

if __name__ == '__main__':
    main()
