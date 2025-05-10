# Image Deblurring Application

This project implements an image deblurring application using the CMFNet model. It provides both a Flask API and a Streamlit interface for deblurring images.

## Features

- Flask API for image deblurring
- Streamlit web interface for easy interaction
- Supports various image formats (JPG, JPEG, PNG)
- Maintains aspect ratio while processing images
- Real-time image processing

## Installation

1. Clone the repository:

```bash
git clone https://github.com/waiz2601/image_deblurMajor.git
cd image_deblurMajor
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Download the pretrained model from [Google Drive](https://drive.google.com/file/d/1-0C7FdQ5P8_5FEK3qM1uWZAJmXYD2Dm_/view?usp=sharing) and place it in `CMFNet/pretrained_model/deblur_model.pth`

## Usage

1. Start the Flask API:

```bash
python app.py
```

2. Start the Streamlit interface:

```bash
streamlit run streamlit_app.py
```

3. Open your browser and navigate to:
   - Streamlit interface: http://localhost:8501
   - Flask API: http://localhost:5000

## API Endpoints

- `GET /`: API documentation
- `POST /deblur`: Process an image
  - Input: Form data with key 'image' containing the image file
  - Output: JSON with base64 encoded deblurred image

## Project Structure

```
.
├── app.py                 # Flask API implementation
├── streamlit_app.py       # Streamlit interface
├── requirements.txt       # Python dependencies
├── CMFNet/               # CMFNet model implementation
│   ├── model/
│   │   ├── CMFNet.py
│   │   └── block.py
│   └── pretrained_model/
│       └── deblur_model.pth
└── README.md
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
