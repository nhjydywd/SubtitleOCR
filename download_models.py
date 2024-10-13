

model_urls = [
    "https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_det_infer.tar",
    "https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_rec_infer.tar",
    "https://paddleocr.bj.bcebos.com/PP-OCRv4/english/en_PP-OCRv4_rec_infer.tar",
    "https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/korean_PP-OCRv3_rec_infer.tar",
    "https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/japan_PP-OCRv3_rec_infer.tar"
]

def get_name_from_url(url):
    return url.split("/")[-1]

dir_models = "models"

from tqdm import tqdm
import os
import requests

def download_file(url, output_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte

    with open(output_path, 'wb') as file, tqdm(
        desc=output_path,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(block_size):
            file.write(data)
            bar.update(len(data))

def download_models():

    for url in model_urls:
        name = get_name_from_url(url)
        basename = os.path.basename(name)
        path = os.path.join(dir_models, basename)
        if os.path.exists(path):
            os.remove(path)
            print(f"Model {name} already exists, skipping download")
            continue
        print(f"Downloading {name}.......")
        download_file(url, path)
        print(f"Unzip {name}")
        os.system(f"tar -xf {path} -C {dir_models}")
        os.remove(path)

if __name__ == "__main__":
    download_models()