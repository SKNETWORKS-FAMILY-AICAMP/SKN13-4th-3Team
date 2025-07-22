from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse
from .models import ChatSession, ChatMessage
from model_core.flow import chatbot_pipeline
import json

def chat_bot(request):
    return render(request, "chat_bot/chat_bot.html")

@login_required
def chat_list_view(request):
    conversations = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'chat_bot/chat_bot.html', {'conversations': conversations})

@login_required
def new_chat_session(request):
    session = ChatSession.objects.create(user=request.user)
    return redirect('chat_bot:chat_conversation_with_id', session_id=session.id)

@login_required
def chat_conversation(request, session_id=None):
    if session_id:
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    else:
        # If no session_id is provided, get the most recent session or create a new one
        session, created = ChatSession.objects.get_or_create(user=request.user, defaults={})
        if created:
            return redirect('chat_bot:chat_conversation', session_id=session.id)

    if request.method == 'POST':
        user_message_content = request.POST.get('message', '').strip()
        if user_message_content:
            # 1. 사용자 메시지 저장
            ChatMessage.objects.create(session=session, is_from_user=True, content=user_message_content)

            # 2. LangGraph 챗봇 파이프라인 호출 및 스트리밍
            def generate_response():
                ai_response_content = ""
                try:
                    # Fetch chat history for context
                    chat_history_for_llm = []
                    for msg in session.messages.all().order_by('created_at'):
                        chat_history_for_llm.append({"role": "user" if msg.is_from_user else "assistant", "content": msg.content})

                    # Pass chat history to the pipeline
                    for chunk_data in chatbot_pipeline(user_input=user_message_content):
                        if isinstance(chunk_data, dict):
                            if chunk_data.get("type") == "image":
                                yield json.dumps({"type": "image", "content": chunk_data["content"]}) + "\n"
                                ai_response_content += f"chatbot/{chunk_data['content']}" # Store a placeholder for history
                            elif chunk_data.get("type") == "text":
                                content = chunk_data["content"]
                                ai_response_content += content
                                yield json.dumps({"type": "text", "content": content}) + "\n"
                            elif chunk_data.get("type") == "gen":
                                yield json.dumps({"type": "gen", "content": chunk_data["content"]}) + "\n"
                                ai_response_content += f"chatbot/{chunk_data['content']}" # Store a placeholder for history
                            elif 'generation' in chunk_data: # Fallback for older generation chunks if any
                                content = chunk_data['generation']
                                ai_response_content += content
                                yield json.dumps({"type": "text", "content": content}) + "\n"
                            else:
                                print(f"Unexpected dict chunk: {chunk_data}")
                        elif isinstance(chunk_data, str):
                            ai_response_content += chunk_data
                            yield json.dumps({"type": "text", "content": chunk_data}) + "\n"
                        else:
                            print(f"Unexpected chunk type: {type(chunk_data)}, content: {chunk_data}")

                except Exception as e:
                    error_message = f"챗봇 처리 중 오류가 발생했습니다: {e}"
                    print(f"Error during chatbot_pipeline: {e}")
                    yield error_message
                    ai_response_content = error_message # Store error in final response

                # 3. AI 응답 저장 (스트리밍 완료 후)
                ChatMessage.objects.create(session=session, is_from_user=False, content=ai_response_content)

            return StreamingHttpResponse(generate_response(), content_type='application/x-ndjson')
        
        return JsonResponse({'status': 'error', 'message': 'No message provided'}, status=400)

    # 모든 대화 목록을 가져와 템플릿으로 전달
    conversations = ChatSession.objects.filter(user=request.user).order_by('-created_at')

    # 기존 대화 기록을 가져옵니다.
    chat_history = session.messages.all().order_by('created_at')

    return render(request, 'chat_bot/chat_converation.html', {'chat_history': chat_history, 'session_id': session.id, 'conversations': conversations})

@login_required
def clear_chat(request):
    """대화 내용 초기화"""
    if request.method == 'POST':
        ChatSession.objects.filter(user=request.user).delete()
    return redirect('chat_bot:chat_list') # 대화 목록 페이지로 리다이렉트
