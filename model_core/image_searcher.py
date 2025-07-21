from .graph_state import GraphState
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from pathlib import Path

# 모델 및 Qdrant 클라이언트 초기화 (최적화 위해 전역에서 1회만)
model = SentenceTransformer('jhgan/ko-sroberta-multitask')
QDRANT_PATH = Path("qdrant")  # 원하는 경로로 변경 가능
COLLECTION_NAME = "hyundaicar_embeddings"

qdrant = QdrantClient(
    path=QDRANT_PATH,
    prefer_grpc=False  # 로컬 파일 DB 모드 필수
)

def image_search_node(state: GraphState) -> GraphState:
    try:
        # 1. 입력 문장 임베딩
        embedding = model.encode(state.user_input).tolist()
        # 2. Qdrant에서 top_k 유사 이미지 검색
        search_result = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=embedding,
            limit=1,  # top 1
            with_payload=True
        )
        if search_result:
            hit = search_result[0]
            state.image_search_result = hit.payload.get("url", "[url 없음]")
            state.image_search_similarity = hit.score
        else:
            state.image_search_result = None
            state.image_search_similarity = 0.0
    except Exception as e:
        print(f"[image_search_node] Error: {e}")
        state.image_search_result = "[이미지 검색 오류]"
        state.image_search_similarity = 0.0
    return state 