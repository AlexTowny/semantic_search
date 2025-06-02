import os
import json
import requests
import tempfile
import pytesseract
from pdf2image import convert_from_path


JSON_FOLDER = "arxiv_metadata"  # Директория файлов с мета данными
API_BASE_URL = "http://localhost:8000"
COLLECTION_NAME = "research_papers_new"  # Название коллекции точек
CREATE_COLLECTION = False

def process_json_files(json_folder):

    if CREATE_COLLECTION:
        response = requests.post(
          f"{API_BASE_URL}/collections/",
            params={"name": COLLECTION_NAME}
        )
        if not response.ok:
            print(f"Failed to create collection {COLLECTION_NAME}. Status: {response.status_code}")
            return


    for filename in os.listdir(json_folder):
        if not filename.endswith('.json'):
            continue

        file_path = os.path.join(json_folder, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {filename}: {e}")
                continue


        for index, entry in enumerate(data):
            pdf_url = entry.get("pdf_link")
            if not pdf_url:
                print(f"Skipping entry {index} in {filename}: No PDF link")
                continue

            # Download PDF
            try:
                pdf_response = requests.get(pdf_url, timeout=10)
                pdf_response.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to download PDF from {pdf_url}: {e}")
                continue

            # Save to temporary file
            try:
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(pdf_response.content)
                    tmp_path = tmp_file.name
            except IOError as e:
                print(f"Error saving PDF to temp file: {e}")
                continue

            # Convert PDF to images and extract text
            extracted_text = ""
            try:
                images = convert_from_path(tmp_path)
                page_count = 0
                for image in images:
                    if page_count > 3:
                        break
                    page_count += 1
                    extracted_text += pytesseract.image_to_string(image)
            except Exception as e:
                print(f"Error converting PDF to text: {e}")
                os.unlink(tmp_path)
                continue
            finally:
                os.unlink(tmp_path)

            # Prepare point data for the single collection
            point_data = {
                "collection": COLLECTION_NAME,
                "text": extracted_text,
                "link": pdf_url,
                "name": entry.get("title", ""),
                "description": ", ".join(entry.get("authors", []))
            }

            # Create point via API
            try:
                response = requests.post(
                    f"{API_BASE_URL}/points/",
                    json=point_data
                )
                response.raise_for_status()
                print(f"Created point for '{entry.get('title')}' in collection {COLLECTION_NAME}")
            except requests.RequestException as e:
                print(f"Failed to create point for '{entry.get('title')}': {e}")


if __name__ == "__main__":
    process_json_files(JSON_FOLDER)


