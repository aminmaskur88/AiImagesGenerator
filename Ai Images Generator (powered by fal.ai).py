import requests
from urllib.parse import urlparse
from datetime import datetime
from tqdm import tqdm
from langdetect import detect, LangDetectException
from googletrans import Translator

# Menentukan fungsi untuk mendownload gambar dengan progres bar
def download_with_progress(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte

    with open(filename, 'wb') as file, tqdm(
            desc=f"Downloading {filename}",
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
            leave=False  # Menyembunyikan progres bar setelah selesai
    ) as bar:
        for data in response.iter_content(block_size):
            bar.update(len(data))
            file.write(data)

# Mengisi Authorization
your_authorization_key = input("Masukkan kunci otentikasi Anda: ")

while True:
    # Mengisi prompt
    your_prompt = input("Masukkan teks prompt Anda: ")

    try:
        # Deteksi bahasa prompt
        prompt_language = detect(your_prompt)

        # Terjemahkan ke bahasa Inggris jika tidak dalam bahasa Inggris
        if prompt_language != 'en':
            translator = Translator()
            your_prompt = translator.translate(your_prompt, src=prompt_language, dest='en').text

        # URL target
        url = "https://110602490-lora.gateway.alpha.fal.ai/"

        # Payload data
        payload = {
            "model_name": "stabilityai/stable-diffusion-xl-base-1.0",
            "prompt": your_prompt
        }

        # Header dengan kunci otentikasi
        headers = {
            "Authorization": f"Key {your_authorization_key}",
            "Content-Type": "application/json"
        }

        # Mengirim permintaan POST
        response = requests.post(url, json=payload, headers=headers)

        # Mendapatkan URL gambar dari respons
        image_url = response.json().get('images', [{}])[0].get('url', '')

        if image_url:
            # Mendownload file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{your_prompt.replace(' ', '_')}_{timestamp}.png"

            download_with_progress(image_url, filename)

            print(f"\nFile berhasil diunduh dengan nama: {filename}")

            # Menanyakan apakah ingin melanjutkan (hanya menekan Enter)
            user_input = input("Tekan Enter untuk melanjutkan atau ketik 'exit' lalu tekan Enter untuk keluar: ").lower()
            if user_input == 'exit':
                break
            else:
                # Membersihkan konsol setelah melanjutkan
                print('\033c', end='')
        else:
            print("Tidak ada URL gambar dalam respons.")
            break

    except LangDetectException as e:
        print("Gagal mendeteksi bahasa. Pastikan teks prompt memiliki struktur bahasa yang jelas.")
