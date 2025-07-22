

if __name__ == "__main__":
    from .init_vectordb import init_description_vectordb
    from .flow import chatbot_pipeline

    # Qdrant description_vector_store가 없으면 최초 1회만 초기화
    init_description_vectordb()
    test_inputs = [
        "고양이 이미지를 그려줘",
        "비슷한 이미지를 찾아줘",
        "FAQ를 보여줘",
        "오늘 날씨 어때?"
    ]
    for inp in test_inputs:
        result = chatbot_pipeline(inp)
        print(f"입력: {inp}")
        print(f"최종 답변: {result.final_response}")
        print("-"*40)
