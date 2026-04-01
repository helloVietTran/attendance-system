import numpy as np
from insightface.app import FaceAnalysis
import cv2
import json
from sqlalchemy.orm import Session
from app.models.face_template import FaceTemplate

class FaceRecognitionService:
    def __init__(self):
        self.app = FaceAnalysis(name='buffalo_s', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        self._cache_templates = None

    def process_multiple_images(self, image_list: list[bytes]):
        """Xử lý 20 ảnh mẫu và trả về vector trung bình chuẩn hóa"""
        all_embeddings = []
        
        for img_bytes in image_list:
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None: continue
            
            faces = self.app.get(img)
            if faces:
                # Lấy khuôn mặt chính diện nhất
                face = max(faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]))
                
                if abs(face.pose[1]) < 45: 
                    all_embeddings.append(face.embedding)

        if not all_embeddings:
            return None

        centroid_embedding = np.mean(all_embeddings, axis=0)
        
        centroid_embedding = centroid_embedding / np.linalg.norm(centroid_embedding)
        return centroid_embedding.tolist()

    def get_known_templates(self, db: Session):
        if self._cache_templates is None:
            self._cache_templates = db.query(FaceTemplate).all()
        return self._cache_templates

    def clear_cache(self):
        """Xóa cache khi có nhân viên mới đăng ký"""
        self._cache_templates = None

    def verify_face(self, current_encoding, known_templates):
        """So khớp khuôn mặt sử dụng Vectorization để đạt tốc độ cao"""
        if not current_encoding or not known_templates:
            return None

        cur_vec = np.array(current_encoding)
        
        # Chuyển đổi list templates thành matrix
        known_vecs = np.array([
            (json.loads(t.face_encoding) if isinstance(t.face_encoding, str) else t.face_encoding)
            for t in known_templates
        ])
        emp_ids = [t.employee_id for t in known_templates]

        # Tính toán độ tương đồng hàng loạt (Matrix Multiplication)
        similarities = np.dot(known_vecs, cur_vec)
        
        max_idx = np.argmax(similarities)
        if similarities[max_idx] > 0.45: # Threshold
            return emp_ids[max_idx]
        
        return None

# Singleton Instance
face_service = FaceRecognitionService()