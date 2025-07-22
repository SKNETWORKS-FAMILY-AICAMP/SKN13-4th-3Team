# 사용 모델 : [stable-diffusion-v1-5](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5)


## ✅ [diffusers란?] (https://github.com/huggingface/diffusers.git)
"Diffusion 모델을 불러오고, 실행하고, fine-tuning하고, inference하는 걸 간단하게 만들어주는 라이브러리"

diffuser를 이용해서 현대 자동차 이미지 - 이미지에 대한 텍스트 설명 데이터 쌍을 stable-diffusion-v1-5 모델을 파인튜닝 진행 중.
diffuser에 text-to-image 모델의 파인튜닝 예제 코드를 활용해서 진행중.

✅ 파인튜닝 목적 요약
베이스 모델: stable-diffusion-v1-5

데이터: 이미지-텍스트 쌍 (현대차 이미지 + 디자인 설명)

목표: 기존 Stable Diffusion 모델이 현대차 디자인을 더 잘 생성하거나 특정 스타일을 반영하도록 만드는 것

## Stable Diffusion 파인 튜닝
대표 기법 2가지.

**A. DreamBooth**
- Google 연구팀이 개발한 기법
- 몇 장의 이미지로 모델을 특정 인물·스타일에 맞게 세밀하게 조정
- 고품질, 일관된 생성 가능 


**B. LoRA (Low‑Rank Adaptation)**
- 저랭크 행렬을 활용해 일부 가중치만 업데이트
- 효율적이며 메모리 사용량과 학습 시간 감소
- 적은 데이터로도 효과적인 학습 가능

🔧 파인튜닝 방법 선택
LoRA (Low-Rank Adaptation) 방식 추천
✅ 적은 메모리 사용

✅ 빠른 훈련

✅ 원본 모델 손상 없이 학습 결과 분리 가능 (.safetensors or .bin으로 저장)

✅ 특정 submodule만 선택적으로 훈련 가능 (예: UNet의 attention block)

🧠 훈련
Stable Diffusion은 대략 다음 세 부분으로 나뉨:

Text Encoder (CLIP): 텍스트 임베딩

**UNet**: 노이즈 예측 (이미지 생성의 핵심)

VAE: latent space에서 이미지 압축/복원

👉 권장 훈련 대상:
**UNet**의 Cross-Attention 레이어에만 LoRA를 적용해서 훈련
→ 텍스트와 이미지의 연결 학습에 집중

이 방식은 기존 스타일이나 일반적인 생성 능력은 유지하면서, “현대차 디자인”에 대한 반응을 학습시키는 데 적합.



runpod 환경에 diffuser를 clone한 다음 pip install . 으로 모듈 설치, 실행하려는 예제 코드 디렉에 들어가서 requirement.txt의 모듈 설치하고 train_text_to_image_lora.py 실행.

## 학습 실행 명령어

```bash
accelerate launch train_text_to_image_lora.py \
  --pretrained_model_name_or_path="sd-legacy/stable-diffusion-v1-5" \
  --train_data_dir="./car_images_all" \
  --output_dir="./lora_hyundai_output" \
  --caption_column="text" \
  --resolution=512 \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --learning_rate=1e-4 \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --max_train_steps=1000 \
  --checkpointing_steps=100 \
  --mixed_precision="fp16" \
  --seed=42
```


| 옵션                        | 설명                                                      |
|-----------------------------|-----------------------------------------------------------|
| `accelerate launch`         | Hugging Face Accelerate를 이용해 분산 학습 실행          |
| `train_text_to_image_lora.py` | 텍스트-투-이미지 LoRA 학습 스크립트                      |
| `--pretrained_model_name_or_path` | 사용할 사전 학습 모델 경로 (예: `sd-legacy/stable-diffusion-v1-5`) |
| `--train_data_dir`          | 이미지-텍스트 학습 데이터가 위치한 디렉토리              |
| `--output_dir`              | 학습 결과물 및 체크포인트 저장 경로                     |
| `--caption_column`          | 텍스트 설명이 들어 있는 데이터 열 이름 (`text`)         |
| `--resolution`              | 학습 이미지의 입력 해상도 (예: 512x512)                  |
| `--train_batch_size`        | 배치 크기 (메모리 제한 시 1로 설정 가능)                |
| `--gradient_accumulation_steps` | 그래디언트 누적 횟수 (실질 배치 크기 = 배치 × 누적 스텝) |
| `--learning_rate`           | 학습률 설정 (보통 `1e-4` ~ `5e-5` 사용)                  |
| `--lr_scheduler`            | 학습률 스케줄러 (여기선 고정 학습률 사용)               |
| `--lr_warmup_steps`         | 학습률 워밍업 스텝 수 (0이면 워밍업 없음)               |
| `--max_train_steps`         | 전체 학습 스텝 수                                        |
| `--checkpointing_steps`     | 체크포인트 저장 주기 (여기선 100 스텝마다)              |
| `--mixed_precision`         | 혼합 정밀도 학습 모드 (`fp16`으로 메모리 절약)          |
| `--seed`                    | 랜덤 시드를 고정해 재현성 확보                          |




