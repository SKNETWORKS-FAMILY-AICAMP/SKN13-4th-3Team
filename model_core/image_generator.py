import os
import re
import time
from graph_state import GraphState
from google.cloud import translate_v2 as translate
from diffusers import StableDiffusionPipeline
import torch
from dotenv import load_dotenv

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


# 데이터 폴더 생성
DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/generated_images")
os.makedirs(DATA_DIR, exist_ok=True)

# Stable Diffusion 파이프라인 초기화
sd_model_id = "sd-legacy/stable-diffusion-v1-5"

pipe = StableDiffusionPipeline.from_pretrained(
    sd_model_id, torch_dtype=torch.float32  # CPU는 float32 권장
)
pipe = pipe.to("cpu")

def prompt_to_filename(prompt_en: str) -> str:
    # 영어 프롬프트에서 알파벳/숫자/공백만 남기고, 공백은 _로
    base = re.sub(r'[^a-zA-Z0-9 ]', '', prompt_en).strip().replace(' ', '_')
    base = base[:40]  # 너무 길면 자름
    timestamp = int(time.time())
    return f"{base}_{timestamp}.png"

def translate_ko_to_en(text):
    try:
        client = translate.Client()
        result = client.translate(text, source_language='ko', target_language='en')
        return result['translatedText']
    except Exception as e:
        print(f"[translate_ko_to_en] Error: {e}")
        return "a photo"

def image_gen_node(state: GraphState) -> GraphState:
    try:
        # 1. 입력 번역
        prompt_en = translate_ko_to_en(state.user_input)
        # 2. 이미지 생성
        image = pipe(prompt_en).images[0]
        # 3. 파일명 생성 및 저장
        filename = prompt_to_filename(prompt_en)
        image_path = os.path.join(DATA_DIR, filename)
        image.save(image_path)
        state.image_gen_result = image_path
    except Exception as e:
        print(f"[image_gen_node] Error: {e}")
        state.image_gen_result = "[이미지 생성 오류]"
    return state 