import os
import sys
import json
import time
import re
import random
import urllib.request
import urllib.parse

def split_text_into_chunks(text, max_length=1600):
    text = text.strip()
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    remaining = text
    while len(remaining) > 0:
        if len(remaining) <= max_length:
            chunks.append(remaining)
            break
        
        split_idx = -1
        search_area = remaining[:max_length + 300]
        
        # 1. Scene dividers
        dividers = [r'\n\s*\*\s*\*\s*\*\s*\n', r'\n\s*---\s*\n', r'\n\s*===\s*\n']
        for div in dividers:
            match = re.search(div, search_area)
            if match and match.start() > 400 and match.start() < max_length + 150:
                split_idx = match.end()
                break
        
        # 2. Paragraph (\n\n)
        if split_idx == -1:
            p_idx = search_area.rfind('\n\n', 0, max_length)
            if p_idx > 400:
                split_idx = p_idx + 2
        
        # 3. Newline (\n)
        if split_idx == -1:
            n_idx = search_area.rfind('\n', 0, max_length)
            if n_idx > 400:
                split_idx = n_idx + 1
        
        # 4. Sentence boundary (. )
        if split_idx == -1:
            dot_idx = search_area.rfind('. ', 0, max_length)
            if dot_idx > 400:
                split_idx = dot_idx + 2
        
        # 5. Fallback space
        if split_idx == -1:
            s_idx = search_area.rfind(' ', 0, max_length)
            if s_idx > 150:
                split_idx = s_idx + 1
            else:
                split_idx = max_length
                
        chunk = remaining[:split_idx].strip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[split_idx:].strip()
        
    return chunks

def clean_and_parse_json(raw_text):
    cleaned = raw_text.strip()
    
    # 1. Strip markdown code fences
    markdown_match = re.search(r'```json\s*([\s\S]*?)\s*```', cleaned, re.IGNORECASE)
    if markdown_match:
        cleaned = markdown_match.group(1).strip()
    else:
        cleaned = cleaned.replace('```', '').strip()
        
    # 2. Isolate JSON
    start_idx = cleaned.find('{')
    end_idx = cleaned.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned = cleaned[start_idx:end_idx + 1]
        
    # 3. Trailing comma cleanup
    cleaned = re.sub(r',\s*([\]}])', r'\1', cleaned)
    
    try:
        return json.loads(cleaned)
    except Exception as e:
        print(f"[Robust Parser] Standard parse failed: {e}. Running Self-Healing...")
        
        # 4. Count brackets
        open_braces = cleaned.count('{')
        close_braces = cleaned.count('}')
        open_brackets = cleaned.count('[')
        close_brackets = cleaned.count(']')
        
        healed = cleaned
        
        if open_brackets > close_brackets:
            if open_braces > close_braces:
                healed += ' }'
                close_braces += 1
            healed += ' ]'
            close_brackets += 1
            
        if open_braces > close_braces:
            while open_braces > close_braces:
                healed += ' }'
                close_braces += 1
                
        try:
            return json.loads(healed)
        except Exception as e2:
            print(f"[Robust Parser] Self-healing failed. Healed string preview: {healed[-150:]}")
            raise Exception(f"JSON 자동 복구 실패: {e2}")

def main():
    print("📖 Webtoon Storyboard Extractor & ComfyUI Generator")
    print("====================================================")

    # 1. Load config
    config_path = "webtoon_storyboard_extractor.json"
    if not os.path.exists(config_path):
        config_path = os.path.join(os.path.dirname(__file__), "webtoon_storyboard_extractor.json")

    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"⚠️ 설정 로드 실패: {e}")

    # Fallback to direct raw text or file path
    novel_raw_text = config.get("NOVEL_RAW_TEXT", "")
    novel_path = config.get("NOVEL_TEXT_PATH", "")
    ollama_url = config.get("OLLAMA_SERVER_URL", "http://127.0.0.1:11434").rstrip("/")
    ollama_model = config.get("OLLAMA_MODEL", "qwen3.5:9b")
    server_url = config.get("COMFYUI_SERVER_URL", "http://127.0.0.1:8188").rstrip("/")
    generate_images = config.get("GENERATE_IMAGES", True)

    # If raw text is empty but path is provided, read it
    if not novel_raw_text.strip() and novel_path:
        try:
            with open(novel_path, "r", encoding="utf-8") as f:
                novel_raw_text = f.read()
            print(f"📖 파일 로드 성공: {novel_path} ({len(novel_raw_text)}자)")
        except Exception as e:
            print(f"❌ 소설 파일을 읽을 수 없습니다: {e}")
            sys.exit(1)

    if not novel_raw_text.strip():
        # Let's search for any .txt file in parent/sibling directory as fallback
        print("💡 입력된 소설 원고가 비어있습니다. c:/ai2 내의 텍스트 파일을 찾아봅니다...")
        default_paths = ["c:/ai2/novel.txt", "C:/ai2/novel.txt", "./novel.txt"]
        for p in default_paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        novel_raw_text = f.read()
                    print(f"📖 기본 소설 파일 자동 탐색 및 로드 성공: {p} ({len(novel_raw_text)}자)")
                    break
                except:
                    pass

    if not novel_raw_text.strip():
        # Generic sample text for illustration
        novel_raw_text = "이른 아침, 한 여학생이 벚꽃이 흩날리는 언덕길을 걸어가고 있었다. 그녀는 실버 헤어에 맑은 보라색 눈동자를 가지고 있었고, 검은 드레스를 입고 있었다. 그 순간 그녀의 손가락이 바람을 스쳤다."
        print(f"💡 소설 텍스트를 찾지 못하여 기본 샘플 원고로 시연을 시작합니다.")

    # Find Z-Anime-Workflow.json
    workflow_paths = [
        "c:/ai2/Z-Anime-Workflow.json",
        "C:/ai2/Z-Anime-Workflow.json",
        os.path.abspath("Z-Anime-Workflow.json"),
        os.path.abspath("../Z-Anime-Workflow.json"),
        os.path.abspath("../../Z-Anime-Workflow.json"),
    ]
    workflow_path = None
    for p in workflow_paths:
        if os.path.exists(p):
            workflow_path = p
            break

    if not workflow_path and generate_images:
        print("⚠️ 경고: Z-Anime-Workflow.json 워크플로우 템플릿을 찾을 수 없어 이미지 생성을 비활성화합니다.")
        generate_images = False

    # 2. Chunking
    chunks = split_text_into_chunks(novel_raw_text, 1500)
    print(f"📖 소설 원고가 총 {len(chunks)}개의 의미적 장면 청크로 자동 분할되었습니다.")

    accumulated_panels = []
    overall_title = ""
    characters = set()

    # 3. Loop over chunks and query Ollama
    for idx, chunk in enumerate(chunks):
        chunk_num = idx + 1
        print(f"\n⚡ [청크 {chunk_num}/{len(chunks)}] AI 분석 및 콘티 패널 추출 시작...")
        
        system_instructions = (
            "당신은 전문 웹툰 스토리보드 작가입니다. 주어진 소설 텍스트를 분석하여 웹툰 제작을 위한 상세 스토리보드(콘티)를 JSON 포맷으로 치밀하게 추출해야 합니다.\n\n"
            "[constraints]\n"
            "- Z-Anime performs best with Natural Language Descriptions (coherent sentences) for image prompts.\n"
            "- Do not include negative prompts in the imagePrompt field.\n"
            "- Ensure sceneDescription, narration, and dialogue are in KOREAN.\n"
            "- Ensure imagePrompt is in ENGLISH.\n\n"
            f"- This is Chunk {chunk_num} of {len(chunks)}.\n"
            f"- Already generated {len(accumulated_panels)} panels. You MUST start numbering panels in this chunk from {len(accumulated_panels) + 1}."
        )

        user_prompt = (
            "다음 형식의 JSON으로만 출력하세요:\n"
            "{\n"
            '  "title": "에피소드 제목 (Korean)",\n'
            '  "characters": ["캐릭터 이름 1", "캐릭터 이름 2"],\n'
            '  "panels": [\n'
            "    {\n"
            f'      "panelNumber": {len(accumulated_panels) + 1},\n'
            '      "sceneDescription": "한국어 장면 상세 묘사",\n'
            '      "imagePrompt": "Extremely detailed English prompt describing the characters (with their appearance, clothing), background location, lighting, camera angle, and modern anime style in cohesive sentences.",\n'
            '      "narration": "한국어 나레이션 (없으면 빈 문자열)",\n'
            '      "dialogue": "한국어 인물 대사 (없으면 빈 문자열)"\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "[분석할 소설 원문]\n"
            f"{chunk}"
        )

        payload = {
            "model": ollama_model,
            "prompt": user_prompt,
            "system": system_instructions,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.3,
                "num_ctx": 16384,
                "num_predict": 8192
            }
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{ollama_url}/api/generate",
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                text_response = res_data.get("response", "")
                
                chunk_result = clean_and_parse_json(text_response)
                
                if chunk_result:
                    if chunk_result.get("title") and not overall_title:
                        overall_title = chunk_result.get("title")
                    for c in chunk_result.get("characters", []):
                        characters.add(c)
                    
                    for p_idx, p in enumerate(chunk_result.get("panels", [])):
                        p["id"] = str(random.randint(1000000, 9999999))
                        p["panelNumber"] = len(accumulated_panels) + 1
                        accumulated_panels.append(p)
                        print(f"  └─ 패널 {p['panelNumber']} 추출 성공: {p['sceneDescription'][:40]}...")
        except Exception as e:
            print(f"❌ [청크 {chunk_num} 실패] Ollama 연결 또는 파싱 오류: {e}")
            continue

    if not accumulated_panels:
        print("❌ 스토리보드 패널을 하나도 추출하지 못했습니다. 프로그램을 종료합니다.")
        sys.exit(1)

    print(f"\n🎉 콘티 추출 완수! 총 {len(accumulated_panels)}개의 패널 스토리보드가 생성되었습니다.")
    print(f"🏷️ 에피소드 제목: {overall_title or '웹툰 스토리보드'}")
    print(f"👥 등장 캐릭터: {', '.join(list(characters))}")

    # 4. Save Folder Creation (Same timestamped folder pattern!)
    timestamp = time.strftime("%Y-%m-%dT%H-%M-%S")
    export_dir = f"c:/ai2/comfy_outputs/exports/콘티추출_{timestamp}"
    os.makedirs(export_dir, exist_ok=True)
    os.makedirs(f"c:/ai2/comfy_outputs/images", exist_ok=True)

    # 5. Image Generation loop
    storyboard_report = []
    storyboard_report.append(f"# 📖 웹툰 콘티 및 시네마틱 작화 리포트 ({overall_title or '무제'})\n")
    storyboard_report.append(f"- **생성 일시:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
    storyboard_report.append(f"- **추출된 총 패널 수:** {len(accumulated_panels)}개")
    storyboard_report.append(f"- **분석된 등장 캐릭터:** {', '.join(list(characters))}\n")
    storyboard_report.append("| 패널 번호 | 연출 및 장면 설명 (Korean) | 나레이션/대사 | 이미지 (Z-Anime) |")
    storyboard_report.append("|---|---|---|---|")

    # Read Workflow template once if generating images
    workflow_template = None
    if generate_images and workflow_path:
        try:
            with open(workflow_path, "r", encoding="utf-8") as f:
                workflow_template = json.load(f)
        except Exception as e:
            print(f"⚠️ 워크플로우 템플릿 로드 실패: {e}")
            generate_images = False

    for p in accumulated_panels:
        p_num = p["panelNumber"]
        scene_desc = p.get("sceneDescription", "")
        img_prompt = p.get("imagePrompt", "")
        narration = p.get("narration", "")
        dialogue = p.get("dialogue", "")
        
        local_img_filename = f"panel_{str(p_num).padStart(2, '0')}.png"
        local_img_path = os.path.join(export_dir, local_img_filename)
        
        image_rendered = False
        
        if generate_images and workflow_template:
            print(f"\n🎨 [패널 {p_num}/{len(accumulated_panels)}] Z-Anime 작화 엔진 구동 중...")
            print(f"  └─ 프롬프트: {img_prompt[:70]}...")
            
            p_workflow = json.loads(json.dumps(workflow_template)) # Deepcopy
            
            # Update inputs
            if "20" in p_workflow and "inputs" in p_workflow["20"]:
                p_workflow["20"]["inputs"]["text"] = img_prompt
            if "100" in p_workflow and "inputs" in p_workflow["100"]:
                p_workflow["100"]["inputs"]["text"] = "blurry, low quality, deformed, text, bad hands, extra digits"
            if "54" in p_workflow and "inputs" in p_workflow["54"]:
                p_workflow["54"]["inputs"]["seed"] = random.randint(1000000000, 9999999999)
                
            prompt_data = {"prompt": p_workflow}
            data_bytes = json.dumps(prompt_data).encode("utf-8")
            
            req = urllib.request.Request(
                f"{server_url}/prompt", 
                data=data_bytes, 
                headers={"Content-Type": "application/json"}
            )
            
            try:
                # Post to ComfyUI
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    prompt_id = res_data.get("prompt_id")
                    
                if prompt_id:
                    completed = False
                    attempts = 0
                    comfy_filename = None
                    
                    while not completed and attempts < 60: # Max 90 seconds
                        time.sleep(1.5)
                        attempts += 1
                        
                        hist_url = f"{server_url}/history/{prompt_id}"
                        try:
                            with urllib.request.urlopen(hist_url, timeout=5) as h_response:
                                hist_data = json.loads(h_response.read().decode("utf-8"))
                        except:
                            continue
                            
                        if prompt_id in hist_data:
                            task_info = hist_data[prompt_id]
                            if task_info.get("status", {}).get("completed", False):
                                completed = True
                                outputs = task_info.get("outputs", {})
                                image_info = outputs.get("95", {}).get("images", [None])[0] or outputs.get("93", {}).get("images", [None])[0]
                                if not image_info:
                                    for node_id, node_out in outputs.items():
                                        if "images" in node_out and node_out["images"]:
                                            image_info = node_out["images"][0]
                                            break
                                if image_info:
                                    comfy_filename = image_info.get("filename")
                                break
                    
                    if comfy_filename:
                        # Download view
                        view_url = f"{server_url}/view?filename={urllib.parse.quote(comfy_filename)}&type=output&subfolder="
                        # Keep history in images
                        hist_local_path = f"c:/ai2/comfy_outputs/images/panel_{str(p_num).padStart(2, '0')}_{str(random.randint(100, 999))}.png"
                        try:
                            urllib.request.urlretrieve(view_url, local_img_path)
                            urllib.request.urlretrieve(view_url, hist_local_path)
                            print(f"  └─ 작화 생성 및 저장 성공: {local_img_path}")
                            image_rendered = True
                        except Exception as save_err:
                            print(f"  └─ 이미지 다운로드 실패: {save_err}")
            except Exception as comfy_err:
                print(f"  └─ ComfyUI 생성 실패 (서버 꺼짐 또는 에러): {comfy_err}")
                
        # 6. Save text file (.txt) for the panel
        txt_content = (
            f"[Panel Number] {p_num}\n"
            f"[Scene Description]\n{scene_desc}\n\n"
            f"[Image Generation Prompt (English)]\n{img_prompt}\n\n"
            f"[Narration]\n{narration}\n\n"
            f"[Dialogue]\n{dialogue}\n"
        )
        try:
            txt_path = os.path.join(export_dir, f"panel_{str(p_num).padStart(2, '0')}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(txt_content)
        except Exception as txt_err:
            print(f"  └─ 텍스트 정보 파일 저장 오류: {txt_err}")
            
        # Add to markdown report
        speak_text = ""
        if narration:
            speak_text += f"**[나레이션]**<br>{narration}<br><br>"
        if dialogue:
            speak_text += f"**[대사]**<br>{dialogue}"
        if not speak_text:
            speak_text = "_(없음)_"
            
        img_column = "🎨 생성 안됨 (ComfyUI 오프라인)"
        if image_rendered:
            # We can use file protocol or markdown image representation.
            img_column = f"![Panel {p_num}](file:///{local_img_path})"
            
        storyboard_report.append(f"| **패널 {p_num}** | {scene_desc} | {speak_text} | {img_column} |")

    # Save final JSON storyboard
    try:
        json_path = os.path.join(export_dir, "storyboard.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "title": overall_title,
                "characters": list(characters),
                "panels": accumulated_panels
            }, f, indent=2, ensure_ascii=False)
            
        # Save master report as MD
        md_path = os.path.join(export_dir, "storyboard_report.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(storyboard_report))
    except Exception as save_err:
        print(f"⚠️ 마스터 파일 저장 실패: {save_err}")

    print("\n====================================================")
    print("SUCCESS: Webtoon storyboard extracted and generated!")
    print(f"EXPORT_DIRECTORY: {export_dir}")
    print(f"TOTAL_PANELS: {len(accumulated_panels)}")
    print("====================================================")
    print("\n## 📋 생성된 마크다운 스토리보드\n")
    print("\n".join(storyboard_report))

if __name__ == "__main__":
    main()
