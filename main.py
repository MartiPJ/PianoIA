"""
Piano Digital con Reconocimiento de Gestos usando OpenCV y MediaPipe
Este archivo es el punto de entrada principal para la aplicación.
"""

import cv2
import time
from piano_module import PianoModule
from hand_detector import HandDetector
from sound_player import SoundPlayer

def main():
    # Inicializar el detector de manos
    detector = HandDetector(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    
    # Inicializar el reproductor de sonido
    sound_player = SoundPlayer()
    
    # Inicializar el módulo del piano
    piano = PianoModule(detector, sound_player)
    
    # Inicializar la cámara
    cap = cv2.VideoCapture(0)
    
    # Variables para el control de FPS
    prev_time = 0
    curr_time = 0
    
    print("Piano Digital iniciado...")
    print("Instrucciones:")
    print("- Muestra tu mano derecha para tocar Do4, Re4, Mi4, Fa4, Sol4 (pulgar a meñique)")
    print("- Muestra tu mano izquierda para tocar Do3, Re3, Mi3, Fa3, Sol3 (meñique a pulgar)")
    print("- Cierra el puño completamente para tocar todas las notas de la mano correspondiente")
    print("- Presiona 'q' para salir")
    
    while True:
        # Capturar un frame de la cámara
        success, img = cap.read()
        if not success:
            print("Error al capturar imagen de la cámara")
            break
            
        # Voltear la imagen horizontalmente para una experiencia de espejo
        img = cv2.flip(img, 1)
        
        # Detectar manos y procesar el piano
        img = piano.process(img)
        
        # Calcular y mostrar FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time
        cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (255, 0, 0), 2)
        
        # Mostrar la imagen
        cv2.imshow("Piano Digital", img)
        
        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()