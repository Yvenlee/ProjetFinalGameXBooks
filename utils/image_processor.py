from PIL import Image
import requests
from io import BytesIO

def download_and_resize_image(url, output_path):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.resize((300, 300))
    img.save(output_path)
