# Image_to_text: InternVL3-8B-hf model로 car_image description 추출

##  활용 모델: InternVL3-8B-hf
: Huggingface Transformers 호환버전 ([OpenGVLab/InternVL3-8B-hf · Hugging Face](https://huggingface.co/OpenGVLab/InternVL3-8B-hf?utm_source=chatgpt.com#usage-example))

- Vision Encoder (e.g. EVA-CLIP, ViT, Swin)
- Projector (image features → text embedding space)
- LLM backbone (Qwen, LLaMA, Baichuan 등)
<img width="500" alt="image" src="https://github.com/user-attachments/assets/25397f71-3470-4ce3-b168-3fa393675e81" />

💡InternVL3의 Backbone 구조를 한국어 모델로 바꿔야 하나...?<br>
backbone LLM을 교체하려면:<br>
1️⃣ LLM input embedding dim과 Vision Projector output dim이 일치해야 함<br>
2️⃣ positional embedding, attention mask 같은 구조가 호환돼야 함<br>
3️⃣ tokenizer, special tokens 처리도 맞춰야 함<br>

→ Qwen을 한국어 모델로 바꿔보려고 했는데, 그거보다 차라리 한국어로 추가적인 finetuning을 하거나, output값을 영어로 나오게 prompt를 주고자 함.

### 1. InternVL3 fine-tuning 데이터 준비 <br>
: JSON 파일(web_crawling으로 이름,종류) + 이미지 파일 별도 directory로 저장

| 데이터 유형 | 예시 포맷 |
| --- | --- |
| 경로 기반 데이터 | images/elantra.png + 텍스트 JSON/JSONL로 연결 |
| 바이너리 직접 | webdataset (tar로 이미지+주석 압축) |
| huggingface datasets | Dataset.from_json / from_dict |

⏩ JSON/JSONL 형식, but, 이미지의 경우 

- binary로 직접 넣는 게 아니라,
- 경로로 넣고, 학습 코드에서 `PIL.Image.open(path)` 식으로 로드

### **2. GPU 환경 설정(with RunPod)**


💡multimodal model은 colab 무료 버전에서는 안 돌아감

→ Runpod 사용해야됨! (그중에서도  OOM(out of memory)이 안되는 애들로 골라서 잘 써야함)

```bash
OutOfMemoryError: CUDA out of memory. 
Tried to allocate 2.03 GiB. GPU 0 has a total capacity of 31.37 GiB of which 32.69 MiB is free. 
Including non-PyTorch memory, this process has 31.33 GiB memory in use. Of the allocated memory 30.57 GiB i
s allocated by PyTorch, and 185.26 MiB is reserved by PyTorch but unallocated. 
If reserved but unallocated memory is large try setting PYTORCH_CUDA_ALLOC_CONF=expandable_segments:
id fragmentation.  See documentation for Memory Management  (https://pytorch.org/docs/stable/notes/cuda.html#environment-variables)
```

| GPU | VRAM | 지원 타입 | 적합한 용도 |
| --- | --- | --- | --- |
| **A6000** | 48GB | float16 | ✅ 안정적 + 가성비 좋음 – 일반 개발용 추천 |
| **A100 80GB** | 80GB | float16, bfloat16 | ✅ 속도와 메모리 최강 – 프로덕션/배치처리 시 추천 |
| **H100 80GB** | 80GB+ | float16, bfloat16 | ✅ 최고성능 – 논문, 거대 실험용 → 비용 고려 필수 |

<img width="1826" height="326" alt="image" src="https://github.com/user-attachments/assets/ac2a03c3-0a06-4637-be37-fd5c372da95f" />


→ 현재 데이터셋으로는 A6000으로도 충분함 !!

### 3. hugging face `model card`에서 usage example 꼭 확인!!

InternVL3 모델이 사용하는 message 형식 같은게 있을 수 있으니깐, hugging face 홈페이지에 들어가서 꼭 model card에서 usage example를 확인하는 것이 좋다!! (마음대로 넣으면 에러 발생함….)

<img width="700" alt="image" src="https://github.com/user-attachments/assets/0a19036f-92cc-48d8-a650-ef2be213d579" />

### 4. 학습시킬 때 prompt의 중요성

이미지에 대한 설명으로 중요한건 자동차 디자이너에게 필요한 정보를 제공할 수 있는 이미지들을 만들어내야함.

초기 프롬프트(영문- backbone이 Qwen모델이라서 영문 작성)

```python
"As an automotive designer, describe this car's design in detail, "
"incl. body type, proportions, surface treatments, lighting design, "
"grill pattern, wheel design, color palette, and any unique or futuristic elements."
```

→ 자세해서 좋긴 한데 나중에 text_to_image 모델에 넣을때 token 제한 수 걸림

**💥 Stable Diffusion에서의 텍스트 token 처리 방식**

✅ Stable Diffusion (특히 v1.x, v2.x, SDXL 등)은

CLIP (OpenAI, Hugging Face 등에서 제공) tokenizer로 텍스트를 encoding합니다.

- 보통 **BPE (Byte Pair Encoding) tokenizer** 기반
- max length 제한 있음

최종 프롬프트

```python
prompt = (
    "Describe this car's design briefly and precisely: body type, proportions, surface, lighting, grill, wheels, color, unique or futuristic elements."
)

```

### 5. 메모리 최적화를 위해 사용한 전략

1️⃣ float16 사용 (quantization 양자화)

: 모델과 데이터의 숫자 표현을 32비트(float32) → 16비트(float16)로 줄여 연산

- GPU 메모리 사용량 약 **절반**으로 줄어듦.
- 연산 속도 **향상** (특히 A100, H100 같은 최신 GPU에서 효과적).
- large language model (LLM) & multimodal model에서 거의 필수 최적화.

```python
model = AutoModelForImageTextToText.from_pretrained(
    'model_name',
    device_map='cuda',
    torch_dtype=torch.float16  # ✅ float16로 메모리 절약
).to('cuda')

inputs = processor(...).to('cuda', dtype=torch.float16)  # inputs도 맞춰줌
```

2️⃣ 추론할때 no_grad 사용 (gradient 계산 비활성화)

: 추론(inference)에서 gradient 계산을 꺼서 backward 패스 메모리/연산 제거.

```python
with torch.no_grad():
    output = model.generate(**inputs, max_new_tokens=300)  # ✅ gradient 계산 안 함
```

3️⃣ loop마다 메모리 청소 (캐시 정리)

: 각 이미지/배치 처리 후 불필요한 변수 제거, GPU 캐시 비우기, Python garbage collection 실행.

- GPU 메모리 **누적 방지** → Out Of Memory (OOM) 에러 방어.
- 특히 **대규모 이미지/멀티모달 처리 loop**에서 메모리 릭 방지.
