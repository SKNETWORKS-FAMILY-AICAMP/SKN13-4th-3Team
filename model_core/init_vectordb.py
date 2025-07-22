import os
import json
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST_PUBLIC_IP", "localhost")
PORT = 6333


def init_description_vectordb():
    DATA_DIR = Path(__file__).parent.parent / "data"
    DESC_JSON = DATA_DIR / "hyundaicar_descript_merge_all.json"
    EMBEDDING_DIM = 3072
    COLLECTION_NAME = "description_vector_store"
    client = QdrantClient(host=HOST, port=PORT)
    # 컬렉션이 이미 있으면 삭제
    if client.collection_exists(collection_name=COLLECTION_NAME):
        client.delete_collection(collection_name=COLLECTION_NAME)
        print(f"⚠️ Qdrant 컬렉션 '{COLLECTION_NAME}' 삭제 후 재생성.")
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
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    split_docs = text_splitter.split_documents(description_documents)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
    )
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = Qdrant(
        client=client,
        collection_name=COLLECTION_NAME,
        embeddings=embedding_model
    )
    vector_store.add_documents(split_docs)
    print(f"✅ Qdrant에 description_vector_store 벡터 저장 완료 (항상 새로 생성)")

def init_feedback_vectordb():
    DATA_DIR = Path(__file__).parent.parent / "data"
    REVIEW_JSON = DATA_DIR / "hyundai_car_reviews.json"
    EMBEDDING_DIM = 3072
    COLLECTION_NAME = "feedback_vector_store"
    client = QdrantClient(host=HOST, port=PORT)
    # 컬렉션이 이미 있으면 삭제
    if client.collection_exists(collection_name=COLLECTION_NAME):
        client.delete_collection(collection_name=COLLECTION_NAME)
        print(f"⚠️ Qdrant 컬렉션 '{COLLECTION_NAME}' 삭제 후 재생성.")
    REVIEW_KEYWORDS = ["연비", "주행감", "실내공간", "디자인", "하이브리드", "정숙성", "가속", "승차감", "가격", "안전성"]
    def extract_korean_keywords(text, keyword_list):
        return [kw for kw in keyword_list if kw in text]
    def flatten_tags(tags_dict):
        return {f"tags_{k}": v for k, v in tags_dict.items()}
    with open(REVIEW_JSON, "r", encoding="utf-8") as f:
        hyundai_car_reviews = json.load(f)
    def assign_metadata(docs):
        result = []
        for item in docs:
            car_name_kr = item.get('car_name', '').strip()
            car_name_en = car_name_kr.replace(' ', '').replace('하이브리드', 'Hybrid')
            review_text = item.get('review', '')
            review_keywords = extract_korean_keywords(review_text, REVIEW_KEYWORDS)
            review_length = len(review_text)
            item.update({
                'car_name_kr': car_name_kr,
                'car_name_en': car_name_en,
                'review_keywords': review_keywords,
                'review_length': review_length
            })
            result.append(item)
        return result
    result_docs = assign_metadata(hyundai_car_reviews)
    review_documents = [
        Document(
            page_content=f"data_id: {item.get('data_id')} | car_name: {item.get('car_name_kr')}, {item.get('car_name_en')}| review: {item.get('review')}",
            metadata={
                "review_length": item.get('review_length'),
                "review_keywords": item.get('review_keywords', []),
                **flatten_tags(item.get('tags', {}))
            }
        )
        for item in result_docs
    ]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    split_docs = text_splitter.split_documents(review_documents)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
    )
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = Qdrant(
        client=client,
        collection_name=COLLECTION_NAME,
        embeddings=embedding_model
    )
    vector_store.add_documents(split_docs)
    print(f"✅ Qdrant에 feedback_vector_store 벡터 저장 완료 (항상 새로 생성)") 