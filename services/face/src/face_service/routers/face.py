import io
import json
import uuid
from typing import List, Optional

import numpy as np
import redis.asyncio as redis
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from ..core.faiss_index import FaissIndex
from ..core.models import Face
from ..core.storage import get_redis_client, get_session

router = APIRouter()


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class DetectedFace(BaseModel):
    face_id: str
    bounding_box: BoundingBox
    confidence: float
    embedding: List[float]


class DetectResponse(BaseModel):
    faces: List[DetectedFace]


class SearchResult(BaseModel):
    face_id: str
    similarity_score: float
    bounding_box: BoundingBox
    confidence: float


class SearchResponse(BaseModel):
    results: List[SearchResult]


class ClusterResponse(BaseModel):
    clusters: List[List[str]]


@router.post("/detect", response_model=DetectResponse)
async def detect_faces(
    file: UploadFile = File(...),
    source_scan_id: Optional[str] = Form(None),
    face_index: FaissIndex = Depends(),
    session=Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis_client),
):
    try:
        contents = await file.read()
        image = np.array(np.frombuffer(contents, np.uint8))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")

    faces = face_index.detect_faces(image)

    for face in faces:
        face_id = str(uuid.uuid4())
        face.face_id = face_id
        await face_index.add_face(face_id, face.embedding, face)
        face_index.persist()

        session.add(
            Face(
                id=face_id,
                embedding=face.embedding.tobytes(),
                source_scan_id=source_scan_id,
                face_metadata=json.dumps({}),
            )
        )
        await session.commit()

        await redis_client.setex(
            f"face:{face_id}", 86400, json.dumps({"embedding": face.embedding.tolist()})
        )

    return DetectResponse(
        faces=[
            DetectedFace(
                face_id=f.face_id,
                bounding_box=BoundingBox(
                    x=int(f.bbox[0]), y=int(f.bbox[1]), width=int(f.bbox[2]), height=int(f.bbox[3])
                ),
                confidence=f.confidence,
                embedding=f.embedding.tolist(),
            )
            for f in faces
        ]
    )


@router.post("/search", response_model=SearchResponse)
async def search_faces(
    file: Optional[UploadFile] = File(None),
    embedding: Optional[str] = Form(None),
    k: int = Form(10),
    face_index: FaissIndex = Depends(),
):
    if file is None and embedding is None:
        raise HTTPException(status_code=400, detail="Either file or embedding must be provided")

    query_embedding = None
    if file is not None:
        contents = await file.read()
        image = np.array(np.frombuffer(contents, np.uint8))
        query_embedding = face_index.extract_embedding(image)
    else:
        try:
            query_embedding = np.array(json.loads(embedding), dtype=np.float32)
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid embedding: {str(e)}")

    results = face_index.search(query_embedding, k)

    return SearchResponse(
        results=[
            SearchResult(
                face_id=r["face_id"],
                similarity_score=r["score"],
                bounding_box=BoundingBox(
                    x=int(r["bbox"][0]), y=int(r["bbox"][1]), width=int(r["bbox"][2]), height=int(r["bbox"][3])
                ),
                confidence=r["confidence"],
            )
            for r in results
        ]
    )


@router.get("/cluster", response_model=ClusterResponse)
async def cluster_faces(
    k: int = 5,
    face_index: FaissIndex = Depends(),
):
    clusters = face_index.cluster(k)
    return ClusterResponse(clusters=clusters)