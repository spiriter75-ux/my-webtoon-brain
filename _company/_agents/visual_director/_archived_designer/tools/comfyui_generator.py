import os
import sys
import json
import random
import time
import urllib.request
import urllib.parse

def main():
    print("🎨 ComfyUI Studio Agentic Image Generator")
    print("=========================================")

    # 1. Load config
    config_path = "comfyui_generator.json"
    if not os.path.exists(config_path):
        config_path = os.path.join(os.path.dirname(__file__), "comfyui_generator.json")

    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"⚠️ 설정 파일을 로드하지 못했습니다: {e}")

    server_url = config.get("COMFYUI_SERVER_URL", "http://127.0.0.1:8188").rstrip("/")
    positive_prompt = config.get("POSITIVE_PROMPT", "A young anime girl with long flowing silver hair, purple eyes, wearing a sleek black dress, highly detailed, masterpieces, 8k resolution")
    negative_prompt = config.get("NEGATIVE_PROMPT", "blurry, low quality, deformed, bad anatomy, bad hands, extra limbs")
    seed = config.get("SEED", -1)

    if seed == -1:
        seed = random.randint(1000000000, 9999999999)

    print(f"🔌 서버 주소: {server_url}")
    print(f"📝 긍정 프롬프트: {positive_prompt}")
    print(f"🚫 부정 프롬프트: {negative_prompt}")
    print(f"🎲 시드: {seed}")

    # 2. Find Z-Anime-Workflow.json
    workflow_paths = [
        os.path.abspath("Z-Anime-Workflow.json"),
        os.path.abspath("../Z-Anime-Workflow.json"),
        os.path.abspath("../../Z-Anime-Workflow.json"),
        os.path.abspath("../../../Z-Anime-Workflow.json"),
        "c:/ai2/Z-Anime-Workflow.json",
        "C:/ai2/Z-Anime-Workflow.json",
    ]
    
    workflow_path = None
    for p in workflow_paths:
        if os.path.exists(p):
            workflow_path = p
            break

    if not workflow_path:
        print("❌ 에러: Z-Anime-Workflow.json 파일을 찾을 수 없습니다.")
        sys.exit(1)

    print(f"📄 워크플로우 발견: {workflow_path}")

    # 3. Read & update workflow
    try:
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow = json.load(f)
    except Exception as e:
        print(f"❌ 워크플로우 JSON 파싱 실패: {e}")
        sys.exit(1)

    if "20" in workflow and "inputs" in workflow["20"]:
        workflow["20"]["inputs"]["text"] = positive_prompt
    if "100" in workflow and "inputs" in workflow["100"]:
        workflow["100"]["inputs"]["text"] = negative_prompt
    if "54" in workflow and "inputs" in workflow["54"]:
        workflow["54"]["inputs"]["seed"] = seed

    # 4. Post prompt to ComfyUI
    print("⏳ ComfyUI 큐에 등록 중...")
    prompt_data = {"prompt": workflow}
    data_bytes = json.dumps(prompt_data).encode("utf-8")
    
    req = urllib.request.Request(
        f"{server_url}/prompt", 
        data=data_bytes, 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            prompt_id = res_data.get("prompt_id")
    except Exception as e:
        print(f"❌ ComfyUI 연결 실패: ComfyUI 서버가 켜져 있는지 확인하세요. ({e})")
        sys.exit(1)

    if not prompt_id:
        print("❌ 에러: ComfyUI로부터 prompt_id를 받지 못했습니다.")
        sys.exit(1)

    print(f"✅ 큐 등록 성공 (Prompt ID: {prompt_id})")

    # 5. Poll history
    completed = False
    attempts = 0
    max_attempts = 120
    filename = None

    print("⏳ KSampler 이미지 생성 대기 중 (최대 2분)...")
    while not completed and attempts < max_attempts:
        time.sleep(1.5)
        attempts += 1
        
        hist_url = f"{server_url}/history/{prompt_id}"
        try:
            with urllib.request.urlopen(hist_url, timeout=5) as response:
                hist_data = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            # Server might be busy, ignore temporarily
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
                    filename = image_info.get("filename")
                break
        
        if attempts % 10 == 0:
            print(f"  ... {attempts * 1.5:.1f}초 경과")

    if not completed or not filename:
        print("❌ 이미지 생성 실패 또는 시간 초과.")
        sys.exit(1)

    print(f"🎉 이미지 생성 완료! 파일명: {filename}")

    # 6. Download image
    view_url = f"{server_url}/view?filename={urllib.parse.quote(filename)}&type=output&subfolder="
    print(f"📥 이미지 다운로드 중: {view_url}")
    
    # Save directory
    out_dir = "c:/ai2/comfy_outputs"
    if not os.path.exists(out_dir):
        out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "comfy_outputs"))
        os.makedirs(out_dir, exist_ok=True)
    else:
        os.makedirs(out_dir, exist_ok=True)
        
    local_path = os.path.join(out_dir, filename)
    
    try:
        urllib.request.urlretrieve(view_url, local_path)
        print(f"💾 로컬 파일 저장 성공: {local_path}")
    except Exception as e:
        print(f"❌ 이미지 저장 실패: {e}")
        sys.exit(1)

    print("=========================================")
    print("SUCCESS: Image generated and saved successfully!")
    print(f"RESULT_PATH: {local_path}")
    print(f"SEED_USED: {seed}")

if __name__ == "__main__":
    main()
