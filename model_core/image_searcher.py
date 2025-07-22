from model_core.graph_state import GraphState
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()
HOST = os.getenv("HOST_PUBLIC_IP")

# 모델 및 Qdrant 클라이언트 초기화 (최적화 위해 전역에서 1회만)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
QDRANT_PATH = Path("qdrant_storage")  # 원하는 경로로 변경 가능 
COLLECTION_NAME = "description_vector_store"

client = QdrantClient(host="3.35.81.92", port=6333)
qdrant = Qdrant(
    client=client,
    collection_name="description_vector_store",
    embeddings=embedding_model
)

def image_search_node(state: GraphState) -> GraphState:
    try:
        # 1. 입력 문장 임베딩
        embedding = embedding_model.embed_query(state.user_input)
        # 2. Qdrant에서 top_k 유사 이미지 검색
        search_result = qdrant.similarity_search_with_score_by_vector(
            embedding=embedding,
            k=1,
        )
        if search_result:
            hit = search_result[0]
            state.image_search_result = hit[0].metadata.get("url", "[url 없음]")
            state.image_search_similarity = hit[1]
        else:
            state.image_search_result = None
            state.image_search_similarity = 0.0
    except Exception as e:
        print(f"[image_search_node] Error: {e}")
        state.image_search_result = "[이미지 검색 오류]"
        state.image_search_similarity = 0.0
    return state 