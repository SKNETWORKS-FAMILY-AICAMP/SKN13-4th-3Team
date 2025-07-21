from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatSession, ChatMessage
from model_core.flow import chatbot_pipeline

def chat_bot(request):
    return render(request, "chat_bot/chat_bot.html")

@login_required
def chat_bot_view(request):
    # 사용자의 가장 최근 대화 세션을 가져오거나 새로 생성합니다.
    session, created = ChatSession.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_message_content = request.POST.get('message', '').strip()
        if user_message_content:
            # 1. 사용자 메시지 저장
            ChatMessage.objects.create(session=session, is_from_user=True, content=user_message_content)

            # 2. LangGraph 챗봇 파이프라인 호출
            try:
                graph_state = chatbot_pipeline(user_input=user_message_content)
                ai_response_content = graph_state.final_response if graph_state.final_response else "죄송합니다. 응답을 생성하지 못했습니다."
            except Exception as e:
                ai_response_content = f"챗봇 처리 중 오류가 발생했습니다: {e}"
                print(f"Error during chatbot_pipeline: {e}")

            # 3. AI 응답 저장
            ChatMessage.objects.create(session=session, is_from_user=False, content=ai_response_content)
        
        return redirect('chat_bot:chat_conversation') # 대화 페이지로 리다이렉트

    # 기존 대화 기록을 가져옵니다.
    chat_history = session.messages.all().order_by('created_at')

    return render(request, 'chat_bot/chat_converation.html', {'chat_history': chat_history})


@login_required
def clear_chat(request):
    """대화 내용 초기화"""
    if request.method == 'POST':
        ChatSession.objects.filter(user=request.user).delete()
    return redirect('chat_bot:chat_conversation') # 대화 페이지로 리다이렉트
