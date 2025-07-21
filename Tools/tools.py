from langchain.tools import tool
from langchain_tavily import Tavilysearch
import json

@tool
def search_web(query: str, max_results: int = 3, time_range: str = "month") -> str: # 반환 타입을 dict에서 str로 변경
    """최신 정보가 필요할 때 인터넷 검색을 하는 Tool입니다. """ # description 명확화
    tavily_search = Tavilysearch(max_results=max_results, time_range=time_range)
    search_result = tavily_search.invoke(query)["results"]
    if search_result:
        # 딕셔너리 리스트를 JSON 문자열로 직렬화하여 반환
        return json.dumps({"results": search_result}, ensure_ascii=False) # 한글 깨짐 방지
    else:
        return json.dumps({"results": []}) # 검색 결과가 없을 때 빈 리스트 반환
