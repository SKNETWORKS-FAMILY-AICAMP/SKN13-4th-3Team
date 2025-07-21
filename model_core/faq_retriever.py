from graph_state import GraphState
from qdrant_client import QdrantClient
from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

QDRANT_PATH = Path("qdrant")  # 원하는 경로로 변경 가능
COLLECTION_NAME = "hyundaicar_embeddings"

qdrant = QdrantClient(
    path=QDRANT_PATH,
    prefer_grpc=False  # 로컬 파일 DB 모드 필수
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "너는 FAQ와 디자인 지식에 능통한 챗봇이야. 아래 참고 문서(context)와 사용자의 질문을 바탕으로 정확하고 친절하게 답변해줘."),
    ("user", """
질문: {user_input}
참고 문서:
{context}
답변:
""")
])

def faq_rag_node(state: GraphState) -> GraphState:
    try:
        search_result = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=state.user_input,  # 이미 임베딩된 벡터라면 벡터로 전달해야 함
            limit=3,
            with_payload=True
        )
        if search_result:
            context = "\n".join(
                f"Q: {hit.payload.get('question', '[질문 없음]')}\nA: {hit.payload.get('answer', '[답변 없음]')}"
                for hit in search_result
            )
            prompt = prompt_template.format_messages(user_input=state.user_input, context=context)
            response = llm.invoke(prompt)
            state.faq_rag_result = response.content.strip()
            state.faq_rag_similarity = max(hit.score for hit in search_result)
        else:
            state.faq_rag_result = "FAQ DB에서 적절한 정보를 찾지 못했습니다."
            state.faq_rag_similarity = 0.0
    except Exception as e:
        print(f"[faq_rag_node] Error: {e}")
        state.faq_rag_result = "FAQ 검색 또는 답변 생성 중 오류가 발생했습니다."
        state.faq_rag_similarity = 0.0
    return state 