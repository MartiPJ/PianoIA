"""
Módulo para la detección de manos utilizando MediaPipe.
Este componente maneja toda la lógica relacionada con la detección de manos y dedos.
"""

import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, mode=False, max_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Inicializa el detector de manos con MediaPipe
        
        Parámetros:
        - mode: Establece si se detectará la mano en cada frame (True) o si se utilizará tracking (False)
        - max_hands: Número máximo de manos a detectar
        - min_detection_confidence: Confianza mínima para considerar una detección exitosa
        - min_tracking_confidence: Confianza mínima para considerar un tracking exitoso
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = min_detection_confidence
        self.tracking_con = min_tracking_confidence
        
        # Inicializar MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.tracking_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Landmarks para cada dedo (pulgar, índice, medio, anular, meñique)
        self.finger_tips = [4, 8, 12, 16, 20]  # ID de los puntos de las puntas de los dedos
        self.finger_bases = [2, 5, 9, 13, 17]  # ID de los puntos base de cada dedo
        
    def find_hands(self, img, draw=True, flip_type=True):
        """
        Detecta manos en la imagen proporcionada
        
        Parámetros:
        - img: Imagen en la que se buscarán manos
        - draw: Si se deben dibujar los landmarks y conexiones
        - flip_type: Si se debe voltear la imagen horizontalmente
        
        Retorna:
        - img: Imagen con o sin dibujos de landmarks según el parámetro draw
        - results: Resultados de la detección de manos
        """
        # Convertir la imagen de BGR a RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Procesar la imagen con MediaPipe
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        img, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
        
        return img
    
    def find_positions(self, img, hand_no=0):
        """
        Encuentra las posiciones de los landmarks de una mano específica
        
        Parámetros:
        - img: Imagen en la que se buscarán los landmarks
        - hand_no: Índice de la mano (0 para la primera mano detectada)
        
        Retorna:
        - landmark_list: Lista de coordenadas (x,y) de cada landmark
        - bbox: Bounding box (x,y,w,h) alrededor de la mano
        - hand_type: Tipo de mano ('Left' o 'Right')
        """
        h, w, c = img.shape
        landmark_list = []
        bbox = []
        hand_type = None
        
        if self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) > hand_no:
                # Obtener el tipo de mano (izquierda o derecha)
                if self.results.multi_handedness:
                    hand_type = self.results.multi_handedness[hand_no].classification[0].label
                
                my_hand = self.results.multi_hand_landmarks[hand_no]
                
                # Extraer coordenadas x,y normalizadas y convertirlas a píxeles
                x_min, y_min = w, h
                x_max, y_max = 0, 0
                
                for id, lm in enumerate(my_hand.landmark):
                    px, py = int(lm.x * w), int(lm.y * h)
                    landmark_list.append([id, px, py])
                    
                    # Actualizar los valores para el bounding box
                    x_min = min(x_min, px)
                    y_min = min(y_min, py)
                    x_max = max(x_max, px)
                    y_max = max(y_max, py)
                
                # Añadir margen al bounding box
                margin = 20
                x_min = max(0, x_min - margin)
                y_min = max(0, y_min - margin)
                x_max = min(w, x_max + margin)
                y_max = min(h, y_max + margin)
                
                bbox = [x_min, y_min, x_max - x_min, y_max - y_min]
        
        return landmark_list, bbox, hand_type
    
    def fingers_up(self, landmark_list, hand_type):
        """
        Determina qué dedos están levantados
        
        Parámetros:
        - landmark_list: Lista de coordenadas de landmarks
        - hand_type: Tipo de mano ('Left' o 'Right')
        
        Retorna:
        - fingers: Lista de 5 elementos indicando si cada dedo está levantado (1) o no (0)
        """
        fingers = []
        
        if not landmark_list:
            return [0, 0, 0, 0, 0]
        
        # Adaptamos la lógica para el pulgar según sea mano izquierda o derecha
        # El pulgar está levantado si su punta está a la izquierda/derecha de su base
        if hand_type == "Right":
            if landmark_list[self.finger_tips[0]][1] < landmark_list[self.finger_bases[0]][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:  # Left hand
            if landmark_list[self.finger_tips[0]][1] > landmark_list[self.finger_bases[0]][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        
        # Para los demás dedos, están levantados si su punta está por encima de la segunda articulación
        for id in range(1, 5):
            if landmark_list[self.finger_tips[id]][2] < landmark_list[self.finger_tips[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers
    
    def is_fist(self, fingers):
        """
        Determina si la mano está en forma de puño cerrado
        
        Parámetros:
        - fingers: Lista de 5 elementos indicando si cada dedo está levantado
        
        Retorna:
        - True si todos los dedos están bajados (puño cerrado), False en caso contrario
        """
        return sum(fingers) == 0