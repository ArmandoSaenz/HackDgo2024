import React, { useRef, useState } from 'react'; 
import { View, StyleSheet, Button, Image } from 'react-native';
import { RNCamera } from 'react-native-camera';
import RNFS from 'react-native-fs'; // Necesario para convertir la imagen a base64
import axios from 'axios'; // Usamos axios para enviar la imagen
import { Dimensions } from 'react-native';
import ImagePicker from 'react-native-image-crop-picker';

const CameraScreen = () => {
  const cameraRef = useRef(null);
  const [imageUri, setImageUri] = useState(null);

  const takePicture = async () => {
    if (cameraRef.current) {
      const options = { quality: 0.8, base64: true };
      const data = await cameraRef.current.takePictureAsync(options);
      const croppedImage = await cropImage(data.uri);
      setImageUri(croppedImage);
      uploadImage(croppedImage);
    }
  };

  const cropImage = async (uri) => {
    try {
      // Abrimos el cropper con la imagen seleccionada
      const croppedImage = await ImagePicker.openCropper({
        path: uri,        // URI de la imagen que queremos recortar
        width: 550,       // Ancho de la imagen recortada
        height: 340,      // Altura de la imagen recortada
        cropping: true,   // Habilitar el recorte
        cropperCircleOverlay: false, // Para que no sea un recorte circular
        freeStyleCropEnabled: true,  // Permite mover y ajustar libremente el área de recorte
      });
  
      return croppedImage.path; // Retorna la nueva URI de la imagen recortada
    } catch (error) {
      console.error('Error al recortar la imagen:', error);
      return null; // Manejo del error, en caso de que ocurra algún problema
    }
  };

  const uploadImage = async (uri) => {
    try {
      const formData = new FormData();
      formData.append('image', {
        uri: uri,
        type: "image/jpeg", // Asegúrate de que el tipo de la imagen sea correcto
        name: "name.jpeg" // Puedes cambiar el nombre si lo necesitas
      });
  
      // Hacemos la solicitud POST con axios
      const response = await axios.post('http://93.127.200.111/ine', formData, {
        headers: {
          'Content-Type': 'multipart/form-data' // Corrección aquí
        }
      });
  
      if (response.status === 200) {
        console.log('Imagen enviada correctamente');
      } else {
        console.error('Error al enviar la imagen');
      }
    } catch (error) {
      console.error('Error al enviar la imagen:', error);
      // Más detalles sobre el error
      console.error('Detalles del error:', error.response ? error.response.data : error.message);
    }
  };
  

  return (
    <View style={styles.container}>
      <RNCamera
        ref={cameraRef}
        style={styles.camera}
        type={RNCamera.Constants.Type.back}
        captureAudio={false}
        androidCameraPermissionOptions={{
          title: 'Permiso para usar la cámara',
          message: 'Necesitamos tu permiso para usar la cámara del teléfono',
          buttonPositive: 'Aceptar',
          buttonNegative: 'Cancelar',
        }}
      >
        <View style={styles.overlay} />
        <View style={styles.frameContainer}>
          <View style={styles.frame} />
        </View>
        <View style={styles.overlay} />
      </RNCamera>
      <Button title="Tomar foto" onPress={takePicture} />
      {imageUri && <Image source={{ uri: imageUri }} style={styles.imagePreview} />}
    </View>
  );
};

const windowWidth = Dimensions.get('window').width;
const windowHeight = Dimensions.get('window').height;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  camera: {
    flex: 1,
    width: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  frameContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
  },
  frame: {
    width: 550,
    height: 340,
    borderColor: 'red',
    borderWidth: 2,
  },
  overlay: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  imagePreview: {
    width: 100,
    height: 100,
    marginTop: 10,
  },
});

export default CameraScreen;