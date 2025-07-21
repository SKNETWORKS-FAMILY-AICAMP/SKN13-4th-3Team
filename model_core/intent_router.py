from graph_state import GraphState
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4-1106-preview",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "너는 사용자의 질문을 intent로 분류하는 분류기야. 반드시 intent만 영문으로 출력해. 선택지는 image_search, faq_rag, general 세 가지야."),
    ("user", """
다음 사용자 질문을 intent로 분류하세요.
- 이미지나 사진을 만들어 달라는 요청: image_search
- 후기, 리뷰, 디자인 지식, 디자인 원리, 디자인 팁 등: faq_rag
- 그 외: general

질문: {user_input}
intent:
""")
])

def route_intent(state: GraphState) -> GraphState:
    try:
        prompt = prompt_template.format_messages(user_input=state.user_input)
        response = llm.invoke(prompt)
        state.intent = response.content.strip()
    except Exception as e:
        print(f"[intent_router] Error: {e}")
        state.intent = "general"
        state.general_result = "질문 분석 중 오류가 발생하여 일반 답변으로 처리합니다."
    return state 