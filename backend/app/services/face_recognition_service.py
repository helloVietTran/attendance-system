import numpy as np
import cv2
import json
from sqlalchemy.orm import Session
from app.models.face_template import FaceTemplate


class FaceRecognitionService:
    def __init__(self):
        # Dùng Haar Cascade thay vì AI model
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self._cache_templates = None

    def extract_embedding(self, img):
        """
        Giả lập embedding bằng cách resize + flatten ảnh khuôn mặt
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face = cv2.resize(gray, (50, 50))  # resize nhỏ lại
        
        embedding = face.flatten().astype("float32")
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding

    def process_multiple_images(self, image_list: list[bytes]):
        """
        Xử lý nhiều ảnh → trả về vector trung bình
        """
        all_embeddings = []

        for img_bytes in image_list:
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                face_img = img[y:y+h, x:x+w]
                embedding = self.extract_embedding(face_img)
                all_embeddings.append(embedding)
                break  # chỉ lấy 1 mặt

        if not all_embeddings:
            return None

        centroid = np.mean(all_embeddings, axis=0)
        centroid = centroid / np.linalg.norm(centroid)

        return centroid.tolist()

    def get_known_templates(self, db: Session):
        if self._cache_templates is None:
            self._cache_templates = db.query(FaceTemplate).all()
        return self._cache_templates

    def clear_cache(self):
        self._cache_templates = None

    def verify_face(self, current_encoding, known_templates):
        """
        So khớp khuôn mặt bằng cosine similarity
        """
        if not current_encoding or not known_templates:
            return None

        cur_vec = np.array(current_encoding)

        known_vecs = []
        emp_ids = []

        for t in known_templates:
            vec = t.face_encoding
            if isinstance(vec, str):
                vec = json.loads(vec)

            known_vecs.append(vec)
            emp_ids.append(t.employee_id)

        known_vecs = np.array(known_vecs)

        # cosine similarity
        similarities = np.dot(known_vecs, cur_vec)

        max_idx = np.argmax(similarities)

        if similarities[max_idx] > 0.8:  # threshold cao hơn vì fake embedding
            return emp_ids[max_idx]

        return None


# Singleton
face_service = FaceRecognitionService()