import os
import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from model_core.graph_state import GraphState

from typing import Iterator

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "너는 친절하고 똑똑한 챗봇이야. 사용자 질문과 참고 정보를 바탕으로 자연스럽고 유용한 답변을 생성해줘."),
    ("user", """
질문: {user_input}
참고 정보: {info}
답변:
""")
])

def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        print(f"[get_image_base64] Error: {e}")
        return None

def response_node(state: GraphState) -> Iterator[str]:
    state.final_response = "" # Initialize final_response for accumulation

    if state.intent == "image_search":
        if state.image_search_similarity is not None and state.image_search_similarity < 0.5:
            # 생성 이미지 파일명만 반환 (Django에서 /media/파일명으로 접근)
            response_content = os.path.basename(state.image_gen_result)
        else:
            # 유사 이미지가 URL이면 URL, 경로면 파일명만 반환
            if state.image_search_result and str(state.image_search_result).startswith("http"):
                response_content = state.image_search_result
            else:
                response_content = os.path.basename(state.image_search_result)
        state.final_response = response_content
        yield response_content # Yield the entire response at once for image search
    elif state.intent == "faq_rag":
        info = f"FAQ 답변: {state.faq_rag_result}"
        prompt = prompt_template.format_messages(user_input=state.user_input, info=info)
        for chunk in llm.stream(prompt):
            content = chunk.content or ""
            state.final_response += content
            yield content
    elif state.intent == "general":
        info = state.general_result
        prompt = prompt_template.format_messages(user_input=state.user_input, info=info)
        for chunk in llm.stream(prompt):
            content = chunk.content or ""
            state.final_response += content
            yield content
    else:
        response_content = "적절한 답변을 찾지 못했습니다."
        state.final_response = response_content
        yield response_content 
