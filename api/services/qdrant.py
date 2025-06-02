from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct,VectorParams, Distance, \
PointIdsList, FieldCondition, FilterSelector, Filter, MatchValue,\
RecommendInput, RecommendQuery, SearchParams
import os

qdrant_client = QdrantClient(os.getenv("QDRANT_URL"))

def transform_groups_to_list(input_data):
    output_list = []
    for group in input_data.groups:
        output_list.append(group.hits[0])
    return {'points':output_list}


def create_collection(name: str):
    qdrant_client.create_collection(
        name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

def delete_collection(name: str):
    qdrant_client.delete_collection(name)

def list_collections():
    return qdrant_client.get_collections()



def upsert_points(collection: str, points: list):
    vectors_count = qdrant_client.get_collection(collection_name=collection).points_count
    
    qdrant_client.upsert(
        collection_name=collection,
        points=[
            PointStruct(
                id = (0 if vectors_count is None else vectors_count) + idx, 
                vector=point['vector'], 
                payload=point['payload']
            )
            for idx, point in enumerate(points)
        ],
    )

def get_point(collection: str, point_id: int):
    points = qdrant_client.retrieve(collection, ids=[point_id])
    return points[0] if points else None

def delete_points(collection: str, point_ids: list[int]):
    qdrant_client.delete(
        collection_name=collection,
        points_selector=PointIdsList(points=point_ids),
    )

def delete_points_by_name(
    collection_name: str,
    document_name: str,
    payload_key: str = "name"
    ):


    

    return qdrant_client.delete(
        collection_name=collection_name,
        points_selector=FilterSelector(

        filter=Filter(

            must=[

                FieldCondition(

                    key=payload_key,

                    match=MatchValue(value=document_name),

                ),

            ],

        )

    ),
    )

        


def search_points(collection: str, 
                  vector: list, 
                  distinct:bool,
                  limit: int):
    if distinct:
        return transform_groups_to_list(qdrant_client.query_points_groups(
        collection_name=collection,
        query=vector,
        
        group_by="name",
        group_size=1,
        limit=limit
    ))
        
    else:
        return qdrant_client.query_points(
            collection_name=collection,
            query=vector,
            limit=limit
        )
        


def recommend_points(collection: str, 
                     positive_vector: list, 
                     negative_vector: list, 
                     distinct: bool,
                     limit: int):
    if distinct:
        return transform_groups_to_list(
            qdrant_client.query_points_groups(
                collection_name=collection,
                query=RecommendQuery(recommend=RecommendInput(
                    positive=positive_vector,
                    negative=negative_vector)),
                group_by="name",
                group_size=1,
                limit=limit,
                
            ))
    else:
        return qdrant_client.query_points(
                collection,
                query=RecommendQuery(recommend=RecommendInput(
                    positive=positive_vector,
                    negative=negative_vector)),
                limit=limit

            )



        
