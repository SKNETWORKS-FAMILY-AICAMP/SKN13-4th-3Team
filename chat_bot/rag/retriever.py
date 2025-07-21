# import json

# def search_qdrant(query: str) -> dict:
#     """
#     Qdrant 벡터 DB에서 사용자의 질문(query)과 가장 유사한 자동차 정보를 검색합니다.
    
#     Args:
#         query (str): 사용자의 질문 (예: "그랜저에 대해 알려줘")

#     Returns:
#         dict: 검색된 자동차 정보. {'image': '...', 'description': '...'} 형식.
#     """
#     # =================================================================
#     # TODO: 이 부분에 실제 Qdrant 클라이언트 검색 로직을 구현해야 합니다.
#     # 예시:
#     # from qdrant_client import QdrantClient
#     # client = QdrantClient(host="localhost", port=6333)
#     # hits = client.search(collection_name="cars", query_text=query, limit=1)
#     # context = hits[0].payload if hits else {}
#     # =================================================================

#     # --- 아래는 실제 Qdrant 연동 전 테스트를 위한 임시 데이터입니다. ---
#     print(f"임시 리트리버 실행: '{query}'에 대한 정보를 검색합니다.")
#     # 실제로는 Qdrant 검색 결과가 이 자리에 와야 합니다.
#     # 제공해주신 JSON 파일과 동일한 구조의 샘플 데이터를 반환합니다.
#     sample_context = {
#         "image": "1_그랜저.png",
#         "description": "This car features a sleek estate body type with a balanced, elongated proportion. The smooth, aerodynamic surface enhances its modern look. Subtle lighting accents are integrated into the design, with a minimalist LED strip at the rear. The grill is narrow and horizontal, contributing to a streamlined front fascia. Large, multi-spoke alloy wheels add to its dynamic appearance. The matte gray color gives it a sophisticated finish. Unique elements include the flush door handles and a distinctive, futuristic taillight design."
#     }
#     # 검색된 결과가 없을 경우를 대비해 빈 딕셔너리를 반환할 수도 있습니다.
#     # return context if context else {}
#     return sample_context

# retriever는 아직 수정중. 모델 생성 후 연동하고 사용해볼것.