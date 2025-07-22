from model_core.graph_state import GraphState
from model_core.intent_router import route_intent
from model_core.image_searcher import image_search_node
from model_core.image_generator import image_gen_node
from model_core.faq_retriever import faq_rag_node
from model_core.general_llm import general_node
from model_core.response_llm import response_node
from typing import Iterator

def chatbot_pipeline(user_input: str) -> Iterator[str]:
    state = GraphState(user_input=user_input)
    # 1. intent 분석
    state = route_intent(state)
    # 2. intent에 따라 분기
    if state.intent == "image_search":
        state = image_search_node(state)
        if state.image_search_similarity is not None and state.image_search_similarity < 0.5:
            state = image_gen_node(state)
    elif state.intent == "faq_rag":
        state = faq_rag_node(state)
    elif state.intent == "general":
        state = general_node(state)
    else:
        state = general_node(state)
    # 3. 항상 마지막에 response_node 호출
    # response_node에서 yield되는 각 청크를 다시 yield
    for chunk in response_node(state):
        yield chunk 
