# Servidor de pruebas para la red neuronal
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras import models, layers
import mysql.connector
from mysql.connector import Error
import easyocr

app = FastAPI()

# Disable CORS (Allow all origins, methods, headers, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
# Cargar la red neuronal
model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(500, 500, 1)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(512, activation='relu'),
    layers.Dense(1, activation='sigmoid')
])

# Cargar los pesos del modelo
model.load_weights(f'./WheelTraining.keras')

@app.post("/ine")
async def receive_image(image: UploadFile = File(...)):
    print(image)
    print("Se recibio una peticion")
    # Verificar el tipo de archivo
    if image.content_type not in ["image/png", "image/jpeg"]:
        print("No es de la extensión que se necesita")
        return JSONResponse(content={"status": "unsupported format"}, status_code=400)
    print("Es de la extension que se necesita")
    # Leer y procesar la imagen
    frame = await image.read()
    image_array = np.asarray(bytearray(frame), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    print(image)
    print("***********************************")
    print(image.shape)
    print("***********************************")
    #frame = np.asarray(bytearray(tmp), dtype=np.uint8)
    # ROIs predefinidas (puedes ajustar estos valores según tus necesidades)
    predefined_rois = [
        (185, 100, 110, 65),  # (x, y, width, height) para el primer "río"
        (185, 180, 220, 65),  # (x, y, width, height) para el segundo "río"
        (185, 265, 190, 33)   # (x, y, width, height) para el tercer "río"
    ]
    print(predefined_rois)
    # Inicializar EasyOCR
    reader = easyocr.Reader(["es"], gpu=False)

    # Lista para almacenar los textos extraídos
    texts = []
    # Procesar cada ROI predefinida
    for i, roi in enumerate(predefined_rois):
        x, y, w, h = roi
        print(x)
        print(y)
        print(w)
        print(h)
        roi_image = image[y:y+h, x:x+w]
        
        # Usar EasyOCR para leer el texto de la imagen recortada (ROI)
        result = reader.readtext(roi_image, paragraph=False)
        
        # Agregar todos los textos extraídos a partir del segundo a la lista
        roi_texts = [res[1] for res in result[1:]]
        texts.append(" ".join(roi_texts))

    # Configuración de la base de datos
    db_config = {
        'host': '195.179.239.102',
        'database': 'u105647449_torneo',
        'user': 'u105647449_siru',
        'password': 'T3rasoluciones',
        'port': 3306,
        'connect_timeout': 10
    }
    # Procesar cada ROI predefinida
    for i, roi in enumerate(predefined_rois):
        x, y, w, h = roi
        roi_image = image[y:y+h, x:x+w]
        
        # Usar EasyOCR para leer el texto de la imagen recortada (ROI)
        result = reader.readtext(roi_image, paragraph=False)
        
        # Agregar todos los textos extraídos a partir del segundo a la lista
        roi_texts = [res[1] for res in result[1:]]
        texts.append(" ".join(roi_texts))
        for res in result[1:]:  # Comenzar desde el segundo resultado
            text = res[1]
    print(texts)  
    # Conectar a la base de datos e insertar los datos
    connection = None
    try:
        print("Intentando conectar a la base de datos...")
        connection = mysql.connector.connect(**db_config)
    
        if connection.is_connected():
            print("Conexión exitosa a la base de datos.")
            cursor = connection.cursor()


            # Insertar los textos de cada ROI en la base de datos
            sql = f"INSERT INTO INE (nombre, domicilio, curp) VALUES ('{texts[0]}','{texts[1]}','{texts[2]}')"
            cursor.execute(sql)
            connection.commit()
            print(cursor.rowcount, "registro insertado.")
        else:
            print("No se pudo establecer la conexión a la base de datos.")
    except Error as e:
        print(f"Error mientras se conectaba a MySQL: {e}")
        print(f"Error número: {e.errno}")
        print(f"SQL Estado: {e.sqlstate}")
        print(f"Mensaje: {e.msg}")

    except Exception as e:
        print(f"Error inesperado: {e}")

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a MySQL cerrada")
        else:
            print("No se pudo establecer una conexión. No hay nada que cerrar.")

@app.get("/test")
async def test():
    return JSONResponse(content={"Online": 1})

# Para ejecutar la app de FastAPI
# Ejecuta esto en la terminal: uvicorn nombre_del_archivo:app --reload
