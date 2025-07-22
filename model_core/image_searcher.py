from model_core.graph_state import GraphState
from sentence_transformers import SentenceTransformer
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

qdrant = QdrantClient(host=HOST, port="6333")

def image_search_node(state: GraphState) -> GraphState:
    try:
        # 1. 입력 문장 임베딩
        embedding = embedding_model.embed_query(state.user_input)
        # 2. Qdrant에서 top_k 유사 이미지 검색
        search_result = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=embedding,
            limit=1,  # top 1
            with_payload=True
        )
        if search_result:
            hit = search_result[0]
            state.image_search_result = hit.metadata.get("url", "[url 없음]")
            state.image_search_similarity = hit.score
        else:
            state.image_search_result = None
            state.image_search_similarity = 0.0
    except Exception as e:
        print(f"[image_search_node] Error: {e}")
        state.image_search_result = "[이미지 검색 오류]"
        state.image_search_similarity = 0.0
    return state 