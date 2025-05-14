"""
Script para instalar todas las dependencias necesarias para el piano digital.
"""

import subprocess
import sys
import pkg_resources
import platform

def install_package(package):
    """
    Instala un paquete de Python usando pip
    
    Parámetros:
    - package: Nombre del paquete a instalar
    """
    try:
        # Intentar importar para ver si ya está instalado
        __import__(package.split('==')[0])
        print(f"{package} ya está instalado.")
    except ImportError:
        print(f"Instalando {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} instalado correctamente.")

def main():
    print("Verificando e instalando las dependencias necesarias...")
    
    # Lista de dependencias con versiones específicas
    requirements = [
        "opencv-python==4.8.0.74",
        "mediapipe==0.10.0",
        "numpy==1.24.3",
        "pygame==2.5.0",
        "scipy==1.10.1"
    ]
    
    # Instalar cada paquete
    for package in requirements:
        install_package(package)
    
    print("\nTodas las dependencias han sido instaladas correctamente.")
    print("\nConfiguración del sistema:")
    print(f"- Python: {sys.version}")
    print(f"- Sistema operativo: {platform.system()} {platform.version()}")
    
    # Mostrar instrucciones para ejecutar el programa
    print("\nPara ejecutar el piano digital, sigue estos pasos:")
    print("1. Asegúrate de tener conectada una cámara web.")
    print("2. Ejecuta el script 'main.py' con el comando: python main.py")
    print("\nDisfruta de tu piano digital con detección de gestos!")

if __name__ == "__main__":
    main()