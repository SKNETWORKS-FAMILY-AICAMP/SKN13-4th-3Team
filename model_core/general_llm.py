from model_core.graph_state import GraphState
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "너는 친절하고 똑똑한 챗봇이야. 사용자 질문에 대해 자연스럽고 유용한 답변을 생성해줘."),
    ("user", """
질문: {user_input}
답변:
""")
])

def general_node(state: GraphState) -> GraphState:
    try:
        prompt = prompt_template.format_messages(user_input=state.user_input)
        response = llm.invoke(prompt)
        state.general_result = response.content.strip()
    except Exception as e:
        print(f"[general_node] Error: {e}")
        state.general_result = "일반 답변 생성 중 오류가 발생했습니다."
    return state 