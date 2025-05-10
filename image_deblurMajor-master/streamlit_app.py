import streamlit as st
import requests
import base64
from PIL import Image
import io
import numpy as np
from skimage import img_as_ubyte

st.set_page_config(page_title="Image Deblurring", page_icon="🖼️")

st.title("Image Deblurring App")
st.write("Upload an image to remove blur and enhance its quality")

def resize_image(image, target_size=(256, 256)):
    """Resize image to target size while maintaining aspect ratio"""
    img = Image.open(image)
    img.thumbnail(target_size, Image.Resampling.LANCZOS)
    return img

def process_image(image_file):
    # Resize image to 256x256
    img = resize_image(image_file)
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Send to Flask API
    files = {'image': ('image.png', img_byte_arr, 'image/png')}
    response = requests.post('http://localhost:5000/deblur', files=files)
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            # Convert base64 to image
            image_data = base64.b64decode(result['image'])
            return Image.open(io.BytesIO(image_data))
    return None

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display original image
    st.subheader("Original Image")
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    
    if st.button("Deblur Image"):
        # Prepare the image
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Send to Flask API
        try:
            response = requests.post(
                'http://localhost:5000/deblur',
                files={'image': img_byte_arr}
            )
            
            if response.status_code == 200:
                # Get the processed image
                result = response.json()
                if result['status'] == 'success':
                    # Convert base64 to image
                    img_data = base64.b64decode(result['image'])
                    deblurred_img = Image.open(io.BytesIO(img_data))
                    
                    # Display deblurred image
                    st.subheader("Deblurred Image")
                    st.image(deblurred_img, use_column_width=True)
                else:
                    st.error("Error processing image")
            else:
                st.error(f"Error: {response.status_code}")
                
        except Exception as e:
            st.error(f"Error: {str(e)}") 