from flow import chatbot_pipeline

if __name__ == "__main__":
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