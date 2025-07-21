# 사용 모델 : [stable-diffusion-v1-5](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5)


✅ diffusers란?
"Diffusion 모델을 불러오고, 실행하고, fine-tuning하고, inference하는 걸 간단하게 만들어주는 라이브러리"

diffuser를 이용해서 현대 자동차 이미지 - 이미지에 대한 텍스트 설명 데이터 쌍을 stable-diffusion-v1-5 모델을 파인튜닝 진행 중.
diffuser에 text-to-image 모델의 파인튜닝 예제 코드를 활용해서 진행중.
모듈 버전 충돌 이슈

✅ 파인튜닝 목적 요약
베이스 모델: stable-diffusion-v1-5

데이터: 이미지-텍스트 쌍 (현대차 이미지 + 디자인 설명)

목표: 기존 Stable Diffusion 모델이 현대차 디자인을 더 잘 생성하거나 특정 스타일을 반영하도록 만드는 것

🔧 파인튜닝 방법 선택
1. LoRA (Low-Rank Adaptation) 방식 추천
✅ 적은 메모리 사용

✅ 빠른 훈련

✅ 원본 모델 손상 없이 학습 결과 분리 가능 (.safetensors or .bin으로 저장)

✅ 특정 submodule만 선택적으로 훈련 가능 (예: UNet의 attention block)

🧠 어떤 부분을 훈련시킬까?
Stable Diffusion은 대략 다음 세 부분으로 나뉘어:

Text Encoder (CLIP): 텍스트 임베딩

UNet: 노이즈 예측 (이미지 생성의 핵심)

VAE: latent space에서 이미지 압축/복원

👉 권장 훈련 대상:
UNet의 Cross-Attention 레이어에만 LoRA를 적용해서 훈련
→ 텍스트와 이미지의 연결 학습에 집중

이 방식은 기존 스타일이나 일반적인 생성 능력은 유지하면서, “현대차 디자인”에 대한 반응을 학습시키는 데 적합해.