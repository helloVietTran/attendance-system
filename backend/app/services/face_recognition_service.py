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
        
        self._cache = None 

    def process_multiple_images(self, image_list: list[bytes]):
        all_embeddings = []
        for img_bytes in image_list:
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None: continue
            
            faces = self.app.get(img)
            if faces:
                # Lấy mặt to nhất
                face = max(faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]))
                
                norm_emb = face.embedding / np.linalg.norm(face.embedding)
                all_embeddings.append(norm_emb)

        if not all_embeddings:
            return None

        # Tính vector trung bình của 20 ảnh mẫu
        centroid = np.mean(all_embeddings, axis=0)
        centroid = centroid / np.linalg.norm(centroid)
        return centroid.tolist()

    def get_known_templates(self, db: Session):
        """Tối ưu hóa: Load toàn bộ template vào RAM dưới dạng Matrix"""
        if self._cache is None:
            templates = db.query(FaceTemplate).all()
            if not templates:
                return None
            
            vecs = []
            ids = []
            for t in templates:
                # Parse JSON & nạp Cache
                emb = json.loads(t.face_encoding) if isinstance(t.face_encoding, str) else t.face_encoding
                vecs.append(emb)
                ids.append(t.employee_id)
            
            self._cache = {
                'matrix': np.array(vecs, dtype='float32'),
                'ids': ids
            }
        return self._cache

    def clear_cache(self):
        self._cache = None

    def verify_face(self, current_encoding, cache_data):
        if current_encoding is None or cache_data is None:
            return None

        cur_vec = np.array(current_encoding, dtype='float32')
        known_vecs = cache_data['matrix']
        emp_ids = cache_data['ids']

        similarities = np.dot(known_vecs, cur_vec)
        
        max_idx = np.argmax(similarities)
        if similarities[max_idx] > 0.55:  # Ngưỡng chấp nhận
            return emp_ids[max_idx]
        
        return None

    def check_face_similarity(self, new_encoding, db: Session, exclude_employee_id=None):
        """Kiểm tra xem khuôn mặt mới có giống với template nào đã có không"""
        if new_encoding is None:
            return None

        cache_data = self.get_known_templates(db)
        if cache_data is None:
            return None

        cur_vec = np.array(new_encoding, dtype='float32')
        known_vecs = cache_data['matrix']
        emp_ids = cache_data['ids']

        similarities = np.dot(known_vecs, cur_vec)
        
        for i, sim in enumerate(similarities):
            if exclude_employee_id and emp_ids[i] == exclude_employee_id:
                continue  # Bỏ qua template của chính nhân viên này nếu đang update
            if sim > 0.45:  # Ngưỡng trùng lặp
                return emp_ids[i]  # Trả về ID của nhân viên có khuôn mặt giống
        
        return None

face_service = FaceRecognitionService()