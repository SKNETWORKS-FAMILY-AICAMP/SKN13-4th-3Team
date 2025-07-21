from django.shortcuts import render

def chat_bot(request):
    return render(request, "chat_bot/chat_bot.html")

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatSession, ChatMessage

# --- RAG 로직을 처리할 함수 (별도 파일로 분리하는 것을 권장) ---
# 이 함수는 실제 Qdrant 검색 및 LLM 호출 로직을 구현해야 합니다.
def get_rag_response(query):
    # 1. Qdrant에서 query와 관련된 context 검색
    # context = search_qdrant(query)
    # 2. LLM 프롬프트 생성
    # prompt = create_prompt(query, context)
    # 3. LLM API 호출
    # response = call_llm(prompt)
    # 4. 답변 및 이미지 URL 파싱
    # answer_text = parse_text(response)
    # image_url = parse_image_url(response)

    # 아래는 임시 하드코딩된 답변입니다.
    # 실제 로직으로 교체해야 합니다.
    answer_text = f"'{query}' 모델은 뛰어난 성능과 디자인을 자랑하는 최신 전기차입니다."
    image_url = "https://placehold.co/600x400/0D1117/FFFFFF?text=Car+Image" # 임시 이미지
    
    return f"{answer_text}\n\n![추천 이미지]({image_url})"
# ----------------------------------------------------------------

@login_required
def chat_bot_view(request):
    # 사용자의 가장 최근 대화 세션을 가져오거나 새로 생성합니다.
    session, created = ChatSession.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_message_content = request.POST.get('message', '').strip()
        if user_message_content:
            # 1. 사용자 메시지 저장
            ChatMessage.objects.create(session=session, is_from_user=True, content=user_message_content)

            # 2. RAG 기반 AI 응답 생성
            ai_response_content = get_rag_response(user_message_content)

            # 3. AI 응답 저장
            ChatMessage.objects.create(session=session, is_from_user=False, content=ai_response_content)
        
        return redirect('chat_bot:chat_bot')

    # 기존 대화 기록을 가져옵니다.
    chat_history = session.messages.all().order_by('created_at')

    return render(request, 'chat_bot/chat_bot.html', {'chat_history': chat_history})
