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

    # Fallback to env vars, then JSON config, then default values
    ollama_url = os.environ.get("OLLAMA_SERVER_URL", config.get("OLLAMA_SERVER_URL", "http://127.0.0.1:11434")).rstrip("/")
    ollama_model = os.environ.get("OLLAMA_MODEL", config.get("OLLAMA_MODEL", "qwen3.5:9b"))
    server_url = os.environ.get("COMFYUI_SERVER_URL", config.get("COMFYUI_SERVER_URL", "http://127.0.0.1:8188")).rstrip("/")
    
    # Priority for GENERATE_IMAGES: env var -> config -> default True
    gen_images_env = os.environ.get("GENERATE_IMAGES")
    if gen_images_env is not None:
        generate_images = gen_images_env.lower() in ("true", "1", "yes")
    else:
        generate_images = config.get("GENERATE_IMAGES", True)

    # Priority for novel path: env var -> config -> empty
    novel_path = os.environ.get("NOVEL_TEXT_PATH", config.get("NOVEL_TEXT_PATH", ""))
    
    # Priority for raw text: env var -> config -> empty
    novel_raw_text = os.environ.get("NOVEL_RAW_TEXT", config.get("NOVEL_RAW_TEXT", ""))

    # If raw text is a placeholder or empty, and novel_path exists, load from path
    is_placeholder = "소설 텍스트 내용을 입력하거나" in novel_raw_text or not novel_raw_text.strip()
    if is_placeholder and novel_path:
        try:
            with open(novel_path, "r", encoding="utf-8") as f:
                novel_raw_text = f.read()
            print(f"📖 파일 로드 성공: {novel_path} ({len(novel_raw_text)}자)")
        except Exception as e:
            print(f"❌ 소설 파일을 읽을 수 없습니다: {e}")
            sys.exit(1)

    # Fetch available models from Ollama
    available_models = []
    try:
        req_tags = urllib.request.Request(f"{ollama_url}/api/tags")
        with urllib.request.urlopen(req_tags, timeout=5) as resp:
            tags_data = json.loads(resp.read().decode("utf-8"))
            available_models = [m["name"] for m in tags_data.get("models", [])]
    except Exception as tags_err:
        print(f"⚠️ Ollama 모델 목록 조회 실패: {tags_err}")

    # Resolve ollama_model robustly
    resolved_model = None
    if available_models:
        # 1. Exact match
        if ollama_model in available_models:
            resolved_model = ollama_model
        # 2. Match without tag (e.g. qwen3.5:9b vs qwen3.5:9b:latest)
        if not resolved_model:
            for m in available_models:
                if m.split(':')[0] == ollama_model.split(':')[0]:
                    resolved_model = m
                    break
        # 3. Partial match (case-insensitive)
        if not resolved_model:
            for m in available_models:
                if "qwen3.5" in m.lower() or ("qwen" in m.lower() and "9b" in m.lower()):
                    resolved_model = m
                    break
        # 4. Fallback to Qwen3.6 or any Qwen model
        if not resolved_model:
            for m in available_models:
                if "qwen" in m.lower():
                    resolved_model = m
                    break
        # 5. Fallback to any gemma or other model
        if not resolved_model:
            for m in available_models:
                if "gemma" in m.lower():
                    resolved_model = m
                    break
        # 6. Fallback to first available model
        if not resolved_model and available_models:
            resolved_model = available_models[0]
            
    if resolved_model:
        if resolved_model != ollama_model:
            print(f"🔄 설정된 모델 '{ollama_model}'을 찾을 수 없어 로컬 모델 '{resolved_model}'로 자동 변경합니다.")
        ollama_model = resolved_model
    else:
        print(f"⚠️ Ollama에 로드된 모델을 찾을 수 없습니다. 기본값 '{ollama_model}'을 시도합니다.")


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

    # 2. Chunking (Finer granularity to force 9-15 highly detailed action shots)
    chunks = split_text_into_chunks(novel_raw_text, 600)
    print(f"📖 소설 원고가 총 {len(chunks)}개의 의미적 장면 청크로 자동 분할되었습니다.")

    # 2b. Load designer long-term memory to extract expert rules
    memory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "memory.md"))
    if not os.path.exists(memory_path):
        memory_path = "c:/ai2/_company/_company/_agents/designer/memory.md"
        
    expert_rules = []
    if os.path.exists(memory_path):
        try:
            with open(memory_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            in_rules_section = False
            for line in lines:
                if "## 🏆 누적된 전문가 디자인 규칙" in line or "## 누적된 전문가 디자인 규칙" in line:
                    in_rules_section = True
                    continue
                if in_rules_section:
                    if line.strip().startswith("##"):
                        break
                    if line.strip().startswith("-") or line.strip().startswith("*") or len(line.strip()) > 3:
                        expert_rules.append(line.strip())
            if expert_rules:
                print(f"🧠 [자가 학습 엔진] 메모리({memory_path})로부터 {len(expert_rules)}개의 누적 전문가 디자인 규칙 로드 완료!")
        except Exception as mem_err:
            print(f"⚠️ 에이전트 메모리 로드 중 오류: {mem_err}")

    rules_str = ""
    if expert_rules:
        rules_str = "\n[ACCUMULATED EXPERT DESIGN RULES (메모리 자가 학습 누적 규칙)]\n" + "\n".join(expert_rules) + "\n\n"

    accumulated_panels = []
    overall_title = ""
    characters = set()

    # 3. Loop over chunks and query Ollama
    for idx, chunk in enumerate(chunks):
        chunk_num = idx + 1
        print(f"\n⚡ [청크 {chunk_num}/{len(chunks)}] AI 분석 및 콘티 패널 추출 시작...")
        
        system_instructions = (
            "당신은 전문 웹툰 연출가이자 최정예 스토리보드(콘티) 감독입니다. 원고의 서사적 성격과 감정선, 액션의 속도감에 따라 장면 분할을 고도로 유연하고 가변적이게 조절해야 합니다 (Adaptive Narrative Pacing).\n\n"
            f"{rules_str}"
            "[장면 및 호흡 연출 자율 가이드]\n"
            "1. 상황 맞춤형 장면 분할 (Adaptive Pacing - 1장부터 100장까지 가변성 극대화):\n"
            "   - 모든 에피소드나 씬의 컷 수를 획일적으로 강제하지 마십시오! 장면의 특성에 따라 다음과 같이 자율적이고 스마트하게 조절해야 합니다.\n"
            "     * 서정적 / 심리 묘사 / 인물의 침묵 및 정적 씬: 컷을 최소화하여 단 1~2장의 큼직하고 압도적인 고밀도 시네마틱 프레임으로 연출해 여운과 여백의 미를 극대화하십시오.\n"
            "     * 긴박한 전투 / 어뢰 추격 / 급박한 대치 / 난전 씬: 시간의 흐름을 쪼개어 아주 조밀하고 긴박하게 컷을 수십 장으로 조각내어(Rapid Sequencing) 찰나의 순간과 다각도의 충격을 입체적으로 묘사하십시오.\n"
            "2. 다채로운 카메라 앵글 & 샷 연출 (Cinematography Diversity):\n"
            "   - '인물 얼굴 클로즈업' 1장으로 끝내지 마십시오! 각 컷은 반드시 상호 유기적으로 다양한 카메라 구도를 가져야 합니다.\n"
            "     * Extreme Close-up (눈동자의 미세한 떨림, 땀방울, 손가락 끝)\n"
            "     * Extreme Wide Shot (수심 400미터 밑바닥의 거대한 어둠과 작아 보이는 잠수함)\n"
            "     * High-angle / Low-angle (함장의 위압감, 위성 통신 중단 시의 좌절감)\n"
            "     * Over-the-shoulder (대치하는 부함장과 함장의 시점 샷)\n"
            "     * Action / Effect Impact Cut (어뢰의 접근 궤적, 기만체가 폭발하여 갈라지는 해수)\n"
            "3. 철저한 텍스트 분리 및 매핑 (No Dialogue Loss):\n"
            "   - 원고 속 인물의 실제 대사(Dialogue)와 서술적 묘사(Narration)를 하나도 빠짐없이 100% 매핑하여 별도의 필드에 분리 추출해야 합니다. 컷 묘사만 하고 대사를 유실시키는 것은 절대 불허합니다.\n\n"
            "[technical_constraints]\n"
            "- Z-Anime performs best with Natural Language Descriptions (coherent sentences) for image prompts.\n"
            "- Do not include negative prompts in the imagePrompt field.\n"
            "- Ensure sceneDescription, narration, and dialogue are in KOREAN.\n"
            "- Ensure imagePrompt is in ENGLISH.\n\n"
            f"- This is Chunk {chunk_num} of {len(chunks)}.\n"
            f"- Already generated {len(accumulated_panels)} panels. You MUST start numbering panels in this chunk from {len(accumulated_panels) + 1}."
        )

        user_prompt = (
            "다음 형식의 JSON으로만 출력하세요. 절대 양식을 훼손하지 마십시오:\n"
            "{\n"
            '  "title": "에피소드 제목 (Korean)",\n'
            '  "characters": ["캐릭터 이름 1", "캐릭터 이름 2"],\n'
            '  "panels": [\n'
            "    {\n"
            f'      "panelNumber": {len(accumulated_panels) + 1},\n'
            '      "cameraAngle": "Extreme Close-up 또는 Extreme Wide Shot 등 구체적 지칭",\n'
            '      "sceneDescription": "한국어 장면 상세 묘사 (인물의 행동, 표정, 배경 등 만화 칸 구성 요소)",\n'
            '      "imagePrompt": "Extremely detailed English prompt describing the characters (with their appearance, clothing), background location, lighting, camera angle, and modern anime style in cohesive sentences.",\n'
            '      "narration": "소설 속 실제 서술문이나 나레이션 (한국어, 없으면 빈 문자열)",\n'
            '      "dialogue": "소설 속 실제 큰따옴표 안의 인물 대사 (한국어, 없으면 빈 문자열)"\n'
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

        # =========================================================================
        # 🎬 [REAL WEBTOON STYLING] Generate High-End Vertical Scrolling HTML Viewer
        # =========================================================================
        html_panels = []
        for p in accumulated_panels:
            p_num = p["panelNumber"]
            scene_desc = p.get("sceneDescription", "")
            camera = p.get("cameraAngle", "Eye Level")
            narration = p.get("narration", "")
            dialogue = p.get("dialogue", "")
            
            # Simple heuristic to extract sound effects from narration or dialogue
            sfx = ""
            for word in ["쾅—", "쾅!", "콰아아", "쉬이이", "콰광", "콰앙", "피잉", "쿠쿵"]:
                if word in narration or word in dialogue or word in scene_desc:
                    sfx = word
                    break

            img_src = f"panel_{str(p_num).padStart(2, '0')}.png"
            
            # Dialogue Speech Bubble structure
            dialogue_html = ""
            if dialogue:
                # Alternate bubbles left/right for cinematic variety
                bubble_class = "bubble-right" if p_num % 2 == 0 else "bubble-left"
                speaker_label = "인물"
                if "함장" in scene_desc or "함장" in dialogue:
                    speaker_label = "김태형 함장"
                elif "이헌성" in scene_desc or "이헌성" in dialogue or "부함장" in scene_desc:
                    speaker_label = "이헌성 부함장"
                elif "소나장" in scene_desc or "소나장" in dialogue:
                    speaker_label = "소나장 박 중사"
                elif "통신관" in scene_desc:
                    speaker_label = "통신관"

                dialogue_html = f"""
                <div class="speech-bubble-wrapper {bubble_class}">
                    <div class="speech-bubble">
                        <span class="bubble-speaker">{speaker_label}</span>
                        <p class="bubble-text">"{dialogue}"</p>
                    </div>
                </div>
                """

            # Narration overlay
            narration_html = ""
            if narration:
                narration_html = f'<div class="narration-card">📝 {narration}</div>'

            # Slanted dynamic SFX overlay (의성어/의태어 웹툰 폰트 연출)
            sfx_html = ""
            if sfx:
                sfx_html = f'<div class="webtoon-sfx">{sfx}</div>'

            html_panels.append(f"""
            <div class="webtoon-panel-frame">
                <div class="panel-badge">CUT #{p_num} — {camera}</div>
                <div class="panel-image-wrapper">
                    <img class="webtoon-image" src="{img_src}" alt="Panel {p_num}">
                    {sfx_html}
                </div>
                <div class="panel-text-container">
                    {narration_html}
                    {dialogue_html}
                </div>
            </div>
            """)

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{overall_title or '웹툰 감상실'}</title>
    <link href="https://fonts.googleapis.com/css2?family=Bazzar&family=Noto+Sans+KR:wght@300;400;700;900&family=Nanum+Brush+Script&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #000000;
            --panel-bg: #07090e;
            --gold: #fbbf24;
            --bubble-bg: #ffffff;
            --text-dark: #1f2937;
            --text-light: #f3f4f6;
            --text-dim: #9ca3af;
        }}
        body {{
            background-color: var(--bg-dark);
            color: var(--text-light);
            font-family: 'Noto Sans KR', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            overflow-x: hidden;
        }}
        /* 웹툰 최상단 헤더 */
        .webtoon-header {{
            width: 100%;
            max-width: 600px;
            padding: 30px 20px;
            box-sizing: border-box;
            background: linear-gradient(to bottom, #0d1117, rgba(0,0,0,0));
            text-align: center;
            border-bottom: 1px solid rgba(251, 191, 36, 0.15);
            margin-bottom: 40px;
        }}
        .webtoon-header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 900;
            color: var(--gold);
            text-shadow: 0 0 10px rgba(251,191,36,0.3);
            letter-spacing: -1px;
        }}
        .webtoon-header p {{
            margin: 8px 0 0 0;
            font-size: 13px;
            color: var(--text-dim);
            letter-spacing: 0.5px;
        }}
        /* 웹툰 메인 종스크롤 컨테이너 */
        .webtoon-container {{
            width: 100%;
            max-width: 600px;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-bottom: 200px;
        }}
        /* 개별 웹툰 프레임 및 호흡용 마진(Gutter) 적용 */
        .webtoon-panel-frame {{
            width: 100%;
            display: flex;
            flex-direction: column;
            position: relative;
            margin-bottom: 160px; /* 웹툰 특유의 연출 호흡을 위한 넓은 세로 여백 */
            box-sizing: border-box;
            background-color: var(--panel-bg);
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.03);
            box-shadow: 0 20px 40px rgba(0,0,0,0.8);
            overflow: hidden;
        }}
        .panel-badge {{
            background: rgba(251, 191, 36, 0.15);
            color: var(--gold);
            border-bottom: 1px solid rgba(251, 191, 36, 0.1);
            font-size: 11px;
            font-weight: 700;
            padding: 8px 16px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .panel-image-wrapper {{
            width: 100%;
            position: relative;
            background: #000;
            line-height: 0;
        }}
        .webtoon-image {{
            width: 100%;
            display: block;
            object-fit: cover;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        /* 웹툰 텍스트 & 대사 말풍선 레이아웃 */
        .panel-text-container {{
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            background: linear-gradient(to bottom, var(--panel-bg), #000000);
        }}
        /* 나레이션 카드 */
        .narration-card {{
            background: rgba(17, 24, 39, 0.85);
            border-left: 4px solid var(--gold);
            border-radius: 6px;
            padding: 14px 18px;
            font-size: 14px;
            line-height: 1.6;
            color: #e5e7eb;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            backdrop-filter: blur(8px);
            font-weight: 300;
        }}
        /* 말풍선 래퍼 및 정렬 */
        .speech-bubble-wrapper {{
            display: flex;
            width: 100%;
            margin-top: 8px;
        }}
        .speech-bubble-wrapper.bubble-left {{
            justify-content: flex-start;
        }}
        .speech-bubble-wrapper.bubble-right {{
            justify-content: flex-end;
        }}
        /* 실제 만화 말풍선 디자인 */
        .speech-bubble {{
            background-color: var(--bubble-bg);
            color: var(--text-dark);
            padding: 14px 20px;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            max-width: 85%;
            position: relative;
            box-sizing: border-box;
            border: 1px solid rgba(0,0,0,0.15);
        }}
        .speech-bubble-wrapper.bubble-left .speech-bubble {{
            border-bottom-left-radius: 2px;
        }}
        .speech-bubble-wrapper.bubble-right .speech-bubble {{
            border-bottom-right-radius: 2px;
            background-color: #fef08a; /* 우측 발화자(주로 대치)는 미색 말풍선 처리 */
        }}
        .bubble-speaker {{
            font-size: 11px;
            font-weight: 900;
            color: #b45309;
            display: block;
            margin-bottom: 4px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        .bubble-text {{
            margin: 0;
            font-size: 14px;
            font-weight: 700;
            line-height: 1.5;
            letter-spacing: -0.2px;
        }}
        /* 웹툰 특유의 다이내믹 의성어/의태어 연출 (SFX) */
        .webtoon-sfx {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            font-family: 'Nanum Brush Script', cursive, sans-serif;
            font-size: 54px;
            font-weight: 900;
            color: #ef4444;
            text-shadow: 
                -3px -3px 0 #fff,  
                 3px -3px 0 #fff,
                -3px  3px 0 #fff,
                 3px  3px 0 #fff,
                 0px  10px 20px rgba(239,68,68,0.6);
            transform: rotate(-12deg) scale(1.1);
            z-index: 50;
            pointer-events: none;
            letter-spacing: -2px;
            animation: sfxPulse 1.5s infinite ease-in-out alternate;
        }}
        @keyframes sfxPulse {{
            0% {{ transform: rotate(-12deg) scale(1); }}
            100% {{ transform: rotate(-8deg) scale(1.15); }}
        }}
        /* 하단 푸터 */
        .webtoon-footer {{
            width: 100%;
            max-width: 600px;
            padding: 60px 20px;
            box-sizing: border-box;
            text-align: center;
            background-color: #08090d;
            border-top: 1px solid rgba(251, 191, 36, 0.15);
            font-size: 12px;
            color: var(--text-dim);
            line-height: 1.7;
        }}
        .webtoon-footer strong {{
            color: var(--gold);
        }}
    </style>
</head>
<body>
    <div class="webtoon-header">
        <h1>{overall_title or '웹툰 감상실'}</h1>
        <p>전체 {len(accumulated_panels)}개 패널 • AI 에이전트 자율 연동 작화 리포트</p>
    </div>
    
    <div class="webtoon-container">
        {"".join(html_panels)}
    </div>
    
    <div class="webtoon-footer">
        <p>본 웹툰은 독립형 웹툰 저작 에이전트들이 <strong>100% 자율 협업</strong>하여 제작했습니다.</p>
        <p><strong>[1화 원고 분석 ➔ 콘티 씬 정밀 분할 ➔ 캐릭터/사물 앵글 다양화 ➔ ComfyUI 이미지 렌더링 ➔ 동적 대사 말풍선 오버레이]</strong></p>
        <p>© Connect AI Studio. All rights reserved.</p>
    </div>
</body>
</html>"""

        html_path = os.path.join(export_dir, "webtoon_viewer.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"  └─ ✨ [웹툰 모바일 뷰어] Naver Webtoon 스타일 뷰어 생성 성공: {html_path}")
    except Exception as save_err:
        print(f"⚠️ 마스터 파일 및 뷰어 저장 실패: {save_err}")

    print("\n====================================================")
    print("SUCCESS: Webtoon storyboard extracted and generated!")
    print(f"EXPORT_DIRECTORY: {export_dir}")
    print(f"TOTAL_PANELS: {len(accumulated_panels)}")
    print("====================================================")
    print("\n## 📋 생성된 마크다운 스토리보드\n")
    print("\n".join(storyboard_report))

# webtoon_storyboard_extractor_v4
if __name__ == "__main__":
    main()
