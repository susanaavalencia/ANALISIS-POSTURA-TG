# test_video.py
import os
import pandas as pd
from video_processor import process_video_and_extract_csv

def test_procesamiento():
    # 1. Configurar rutas de prueba
    video_entrada = "test_video.mp4"
    csv_salida = "test_landmarks.csv"

    print("🚀 Iniciando prueba de procesamiento biomecánico...")

    if not os.path.exists(video_entrada):
        print(f"\n❌ Error: No se encontró el archivo '{video_entrada}'.")
        print("💡 Solución: Copia un video a esta carpeta y renómbralo como 'test_video.mp4'.")
        return

    print(f"✅ Video encontrado: {video_entrada}")
    print("⚙️ Procesando con MediaPipe y FFmpeg (esto puede tardar unos segundos)...")

    try:
        # 2. Ejecutar la función principal (ahora retorna 3 variables)
        df, ruta_black, ruta_overlay = process_video_and_extract_csv(
            video_path=video_entrada,
            output_csv_path=csv_salida,
            generate_skeleton_video=True,
            generate_overlay_video=True
        )

        print("\n📊 --- RESULTADOS DE LA PRUEBA ---")

        # 3. Validar los datos del CSV
        if df.empty:
            print("⚠️ Advertencia: El DataFrame está vacío. No se detectó ninguna persona.")
        else:
            print(f"✅ CSV generado con éxito. Dimensión de los datos: {df.shape}")
            print(f"✅ Guardado en: {csv_salida}")
            print("\nMuestra de las primeras 3 coordenadas capturadas:")
            print(df[['frame', 'landmark_id', 'x', 'y', 'z']].head(3))

        # 4. Validar el video con fondo negro
        if ruta_black and os.path.exists(ruta_black):
            tamano_mb = os.path.getsize(ruta_black) / (1024 * 1024)
            print(f"\n✅ Video esqueleto (fondo negro) generado: {ruta_black}")
            print(f"   Tamaño: {tamano_mb:.2f} MB")

        # 5. Validar el video con fondo original
        if ruta_overlay and os.path.exists(ruta_overlay):
            tamano_mb = os.path.getsize(ruta_overlay) / (1024 * 1024)
            print(f"✅ Video esqueleto (sobrepuesto) generado: {ruta_overlay}")
            print(f"   Tamaño: {tamano_mb:.2f} MB")

    except Exception as e:
        print(f"\n❌ Ocurrió un error inesperado durante la prueba:\n{e}")

if __name__ == "__main__":
    test_procesamiento()