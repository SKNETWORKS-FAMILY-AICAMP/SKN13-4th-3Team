from pydantic import BaseModel
from typing import Optional

class GraphState(BaseModel):
    user_input: str
    intent: Optional[str] = None
    image_search_result: Optional[str] = None
    image_search_similarity: Optional[float] = None
    image_gen_result: Optional[str] = None
    faq_rag_result: Optional[str] = None
    faq_rag_similarity: Optional[str] = None
    general_result: Optional[str] = None
    final_response: Optional[str] = None
    stream_response: Optional[str] = None 