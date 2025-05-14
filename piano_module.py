"""
Módulo principal del piano que conecta la detección de manos con la reproducción de sonido.
"""

import cv2
import numpy as np
import time

class PianoModule:
    def __init__(self, hand_detector, sound_player):
        """
        Inicializa el módulo del piano
        
        Parámetros:
        - hand_detector: Instancia de HandDetector para detectar manos y dedos
        - sound_player: Instancia de SoundPlayer para reproducir sonidos
        """
        self.detector = hand_detector
        self.sound_player = sound_player
        
        # Mapeo de dedos a notas (mano derecha)
        self.right_hand_notes = ['la4', 'si4', 'do5', 're5', 'mi5']
        
        # Mapeo de dedos a notas (mano izquierda)
        self.left_hand_notes = ['do4', 're4', 'mi4', 'fa4', 'sol4']
        
        # Estado de los dedos en el frame anterior
        self.previous_fingers_right = [0, 0, 0, 0, 0]
        self.previous_fingers_left = [0, 0, 0, 0, 0]
        
        # Tiempo del último acorde
        self.last_chord_time = 0
        self.chord_cooldown = 1.0  # segundos de enfriamiento entre acordes
        
        # Estado del último puño detectado
        self.last_fist_right = False
        self.last_fist_left = False
        
        # Visualización de teclas virtuales
        self.piano_keys = {
            'right': self._create_piano_visualization(is_right=True),
            'left': self._create_piano_visualization(is_right=False)
            
        }
    
    def _create_piano_visualization(self, is_right=True):
        """
        Crea una visualización de teclas de piano
        
        Parámetros:
        - is_right: Si es para la mano derecha (True) o izquierda (False)
        
        Retorna:
        - Un diccionario con información de las teclas virtuales
        """
        key_width = 40
        key_height = 120

        # Cambia las posiciones iniciales: izquierda inicia más a la izquierda
        start_x = 50 if not is_right else 350
        start_y = 50

        keys = []

        # Orden natural: de izquierda a derecha
        notes = self.right_hand_notes if is_right else self.left_hand_notes

        for i, note in enumerate(notes):
            key = {
                'x': start_x + i * key_width,
                'y': start_y,
                'width': key_width,
                'height': key_height,
                'color': (255, 255, 255),
                'active_color': (173, 216, 230),
                'note': note,
                'active': False,
                'label': note.upper()
            }
            keys.append(key)

        return keys


    
    def _draw_piano_keys(self, img):
        """
        Dibuja las teclas virtuales del piano en la imagen
        
        Parámetros:
        - img: Imagen donde se dibujarán las teclas
        
        Retorna:
        - Imagen con las teclas dibujadas
        """
        for hand_type in ['right', 'left']:
            keys = self.piano_keys[hand_type]
            
            for key in keys:
                color = key['active_color'] if key['active'] else key['color']
                cv2.rectangle(img, (key['x'], key['y']), 
                              (key['x'] + key['width'], key['y'] + key['height']), 
                              color, cv2.FILLED)
                cv2.rectangle(img, (key['x'], key['y']), 
                              (key['x'] + key['width'], key['y'] + key['height']), 
                              (0, 0, 0), 2)
                cv2.putText(img, key['label'], 
                            (key['x'] + 5, key['y'] + key['height'] - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return img
    
    def process(self, img):
        """
        Procesa la imagen, detecta manos y dedos, y reproduce las notas correspondientes
        
        Parámetros:
        - img: Imagen de la cámara
        
        Retorna:
        - img: Imagen procesada con visualizaciones
        """
        # Detectar manos
        img = self.detector.find_hands(img)
        
        # Procesar cada mano
        for hand_idx in range(2):  # Intenta detectar hasta 2 manos
            landmark_list, bbox, hand_type = self.detector.find_positions(img, hand_idx)
            
            if landmark_list and hand_type:
                # Detectar dedos levantados
                fingers = self.detector.fingers_up(landmark_list, hand_type)
                
                # Verificar si la mano está cerrada en puño
                is_fist = self.detector.is_fist(fingers)
                
                # Dibujar bounding box alrededor de la mano
                if bbox:
                    x, y, w, h = bbox
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(img, hand_type, (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Procesar según el tipo de mano
                if hand_type == "Right":
                    # Reproducir notas individuales al levantar dedos
                    for idx, finger_up in enumerate(fingers):
                        # Si el dedo se acaba de levantar
                        if finger_up == 1 and self.previous_fingers_right[idx] == 0:
                            note = self.right_hand_notes[idx]
                            self.sound_player.play_note(note)
                            
                            # Activar visualización de la tecla
                            for key in self.piano_keys['right']:
                                if key['note'] == note:
                                    key['active'] = True
                        
                        # Si el dedo se ha bajado, desactivar la tecla
                        elif finger_up == 0 and self.previous_fingers_right[idx] == 1:
                            note = self.right_hand_notes[idx]
                            for key in self.piano_keys['right']:
                                if key['note'] == note:
                                    key['active'] = False
                    
                    # Reproducir acorde al cerrar el puño
                    current_time = time.time()
                    if is_fist and not self.last_fist_right and current_time - self.last_chord_time > self.chord_cooldown:
                        self.sound_player.play_chord(self.right_hand_notes)
                        self.last_chord_time = current_time
                        
                        # Activar todas las teclas
                        for key in self.piano_keys['right']:
                            key['active'] = True
                    
                    # Si el puño se abre, desactivar todas las teclas
                    if not is_fist and self.last_fist_right:
                        for key in self.piano_keys['right']:
                            key['active'] = False
                    
                    # Actualizar estados
                    self.previous_fingers_right = fingers.copy()
                    self.last_fist_right = is_fist
                
                elif hand_type == "Left":
                    # Reproducir notas individuales al levantar dedos
                    for idx, finger_up in enumerate(fingers):
                        # Si el dedo se acaba de levantar
                        if finger_up == 1 and self.previous_fingers_left[idx] == 0:
                            note = list(self.left_hand_notes)[::-1][idx]
                            self.sound_player.play_note(note)
                            
                            # Activar visualización de la tecla
                            for key in self.piano_keys['left']:
                                if key['note'] == note:
                                    key['active'] = True
                        
                        # Si el dedo se ha bajado, desactivar la tecla
                        elif finger_up == 0 and self.previous_fingers_left[idx] == 1:
                            note = list(self.left_hand_notes)[::-1][idx]
                            for key in self.piano_keys['left']:
                                if key['note'] == note:
                                    key['active'] = False
                    
                    # Reproducir acorde al cerrar el puño
                    current_time = time.time()
                    if is_fist and not self.last_fist_left and current_time - self.last_chord_time > self.chord_cooldown:
                        self.sound_player.play_chord(self.left_hand_notes)
                        self.last_chord_time = current_time
                        
                        # Activar todas las teclas
                        for key in self.piano_keys['left']:
                            key['active'] = True
                    
                    # Si el puño se abre, desactivar todas las teclas
                    if not is_fist and self.last_fist_left:
                        for key in self.piano_keys['left']:
                            key['active'] = False
                    
                    # Actualizar estados
                    self.previous_fingers_left = fingers.copy()
                    self.last_fist_left = is_fist
        
        # Dibujar las teclas del piano
        img = self._draw_piano_keys(img)
        
        # Mostrar instrucciones en pantalla
        cv2.putText(img, "Mano Izquierda: DO4-SOL4", (10, 450), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(img, "Mano Derecha: LA4-MI5", (10, 480), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(img, "Puño cerrado = Acorde", (10, 510), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, "Presiona 'q' para salir", (10, 540), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return img