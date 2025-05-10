from flask import Flask, request, jsonify, render_template_string
import torch
import torch.nn.functional as F
import torchvision.transforms.functional as TF
from PIL import Image
import io
import base64
from CMFNet.model.CMFNet import CMFNet
import numpy as np
import cv2
from collections import OrderedDict
from skimage import img_as_ubyte

app = Flask(__name__)

# Initialize model
model = CMFNet()
device = torch.device('cpu')
model = model.to(device)

# Load pretrained weights
def load_checkpoint(model, weights):
    checkpoint = torch.load(weights, map_location='cpu')
    try:
        model.load_state_dict(checkpoint["state_dict"])
    except:
        state_dict = checkpoint["state_dict"]
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:]  # remove `module.`
            new_state_dict[name] = v
        model.load_state_dict(new_state_dict)

# Load the model weights
load_checkpoint(model, './CMFNet/pretrained_model/deblur_model.pth')
model.eval()

def process_image(image_bytes):
    # Convert bytes to PIL Image
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    
    # Convert to tensor
    input_ = TF.to_tensor(img).unsqueeze(0).to(device)
    
    # Pad the input if not multiple of 8
    h, w = input_.shape[2], input_.shape[3]
    H, W = ((h + 8) // 8) * 8, ((w + 8) // 8) * 8
    padh = H - h if h % 8 != 0 else 0
    padw = W - w if w % 8 != 0 else 0
    input_ = F.pad(input_, (0, padw, 0, padh), 'reflect')
    
    # Process image
    with torch.no_grad():
        restored = model(input_)
    restored = restored[0]
    restored = torch.clamp(restored, 0, 1)
    
    # Un-pad the output
    restored = restored[:, :, :h, :w]
    
    # Convert to numpy array using img_as_ubyte
    restored = restored.permute(0, 2, 3, 1).cpu().detach().numpy()
    restored = img_as_ubyte(restored[0])
    
    # Convert to bytes
    success, buffer = cv2.imencode('.png', cv2.cvtColor(restored, cv2.COLOR_RGB2BGR))
    return buffer.tobytes()

@app.route('/')
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Image Deblurring API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                .endpoint { background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; }
                code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>Image Deblurring API</h1>
            <div class="endpoint">
                <h2>Endpoint: /deblur</h2>
                <p>Method: POST</p>
                <p>Input: Form data with key 'image' containing the image file</p>
                <p>Output: JSON with base64 encoded deblurred image</p>
            </div>
            <p>Use the Streamlit interface for a user-friendly experience.</p>
        </body>
        </html>
    ''')

@app.route('/deblur', methods=['POST'])
def deblur():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        image_file = request.files['image']
        image_bytes = image_file.read()
        
        # Process the image
        processed_image = process_image(image_bytes)
        
        # Convert to base64 for response
        base64_image = base64.b64encode(processed_image).decode('utf-8')
        
        return jsonify({
            'status': 'success',
            'image': base64_image
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 