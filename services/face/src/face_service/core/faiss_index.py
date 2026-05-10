import os
from dataclasses import dataclass
from typing import List, Optional

import cv2
import faiss
import insightface
import numpy as np
from sklearn.cluster import KMeans

INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "/data/faiss.index")
EMBEDDING_DIM = 512


@dataclass
class DetectedFaceData:
    face_id: str = ""
    bbox: tuple = (0, 0, 0, 0)
    confidence: float = 0.0
    embedding: np.ndarray = None


class FaissIndex:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.index = None
        self.face_data = {}
        self.embedding_dim = EMBEDDING_DIM

        self._model = insightface.app.FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        self._model.prepare(ctx_id=0)

        self._load_index()

    def _load_index(self):
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
        else:
            self.index = faiss.IndexFlatIP(self.embedding_dim)

    def persist(self):
        os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
        faiss.write_index(self.index, INDEX_PATH)

    def detect_faces(self, image: np.ndarray) -> List[DetectedFaceData]:
        if len(image.shape) == 1:
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        faces = self._model.get(image)
        results = []
        for face in faces:
            results.append(
                DetectedFaceData(
                    bbox=tuple(face.bbox.astype(int)),
                    confidence=float(face.det_score),
                    embedding=face.embedding.astype(np.float32),
                )
            )
        return results

    def extract_embedding(self, image: np.ndarray) -> np.ndarray:
        faces = self.detect_faces(image)
        if not faces:
            raise ValueError("No face detected in image")
        return faces[0].embedding

    def add_face(self, face_id: str, embedding: np.ndarray, face_data: DetectedFaceData = None):
        normalized = embedding / np.linalg.norm(embedding)
        self.index.add(normalized.reshape(1, -1))
        self.face_data[str(self.index.ntotal - 1)] = {
            "face_id": face_id,
            "embedding": embedding.tolist(),
            "bbox": face_data.bbox if face_data else (0, 0, 0, 0),
            "confidence": face_data.confidence if face_data else 0.0,
        }

    def search(self, query_embedding: np.ndarray, k: int = 10) -> List[dict]:
        if self.index.ntotal == 0:
            return []

        normalized = query_embedding / np.linalg.norm(query_embedding)
        scores, indices = self.index.search(normalized.reshape(1, -1), min(k, self.index.ntotal))

        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx == -1:
                continue
            data = self.face_data.get(str(idx), {})
            results.append(
                {
                    "face_id": data.get("face_id", ""),
                    "score": float(score),
                    "bbox": data.get("bbox", (0, 0, 0, 0)),
                    "confidence": data.get("confidence", 0.0),
                }
            )
        return results

    def cluster(self, k: int = 5) -> List[List[str]]:
        if self.index.ntotal == 0:
            return []

        embeddings = np.array([d.get("embedding", []) for d in self.face_data.values()])
        if len(embeddings) < k:
            k = max(1, len(embeddings))

        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)

        clusters = [[] for _ in range(k)]
        for i, label in enumerate(labels):
            face_id = list(self.face_data.values())[i].get("face_id", "")
            if face_id:
                clusters[label].append(face_id)

        return clusters