import os
import json
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def init_description_vectordb():
    # 데이터 경로
    DATA_DIR = Path(__file__).parent.parent / "data"
    DESC_JSON = DATA_DIR / "hyundaicar_descript_merge_all.json"

    # Qdrant 설정
    EMBEDDING_DIM = 3072
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    COLLECTION_NAME = "description_vector_store"

    # Qdrant 클라이언트
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # 이미 컬렉션이 있으면 아무 작업도 하지 않음
    if client.collection_exists(collection_name=COLLECTION_NAME):
        print(f"✅ Qdrant 컬렉션 '{COLLECTION_NAME}' 이미 존재. 초기화/업로드 생략.")
        return

    # 1. 데이터 로드 및 Document 생성
    def extract_english_keywords(text, keyword_list):
        from sklearn.feature_extraction.text import CountVectorizer
        vectorizer = CountVectorizer(vocabulary=keyword_list, lowercase=True)
        X = vectorizer.fit_transform([text.lower()])
        return [kw for kw, count in zip(vectorizer.get_feature_names_out(), X.toarray()[0]) if count > 0]

    DESCRIPTION_KEYWORDS = ["sleek", "modern", "aerodynamic", "SUV", "sedan", "electric", "hybrid", "dynamic", "spacious", "luxury"]

    with open(DESC_JSON, "r", encoding="utf-8") as f:
        hyundaicar_descript = json.load(f)

    def assign_metadata(docs):
        result = []
        for item in docs:
            car_name_en = item.get('car_name', '').replace('_', ' ').strip()
            car_name_kr = car_name_en.replace('Hybrid', '하이브리드')
            description_text = item.get('description', '')
            description_keywords = extract_english_keywords(description_text, DESCRIPTION_KEYWORDS)
            item.update({
                'car_name_en': car_name_en,
                'car_name_kr': car_name_kr,
                'description_keywords': description_keywords
            })
            result.append(item)
        return result

    json_docs = assign_metadata(hyundaicar_descript)

    description_documents = [
        Document(
            page_content=f"car_name: {item.get('car_name_kr')}, {item.get('car_name_en')} | description: {item.get('description')}",
            metadata={
                "description_keywords": item.get('description_keywords', [])
            }
        )
        for item in json_docs
    ]

    # 2. 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    split_docs = text_splitter.split_documents(description_documents)

    # 3. Qdrant 컬렉션 생성
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
    )

    # 4. 임베딩 및 벡터 저장
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = Qdrant(
        client=client,
        collection_name=COLLECTION_NAME,
        embeddings=embedding_model
    )
    vector_store.add_documents(split_docs)

    print(f"✅ Qdrant에 description_vector_store 벡터 저장 완료 (최초 1회)") 