from django.shortcuts import render
from django.http import JsonResponse
import fitz  # PyMuPDF
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return render(request, 'converter/index.html')

def extract_images_from_pdf(pdf_path):
    """ Extract images from a given PDF and save them. """
    output_folder = os.path.join(settings.MEDIA_ROOT, "extracted_images")
    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)
    extracted_images = []

    for page_num in range(len(doc)):
        for img_index, img in enumerate(doc[page_num].get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            img_ext = base_image["ext"]  # Get image format (png, jpeg, etc.)

            # Save the extracted image
            img_filename = f"page_{page_num+1}_img_{img_index+1}.{img_ext}"
            img_path = os.path.join(output_folder, img_filename)
            with open(img_path, "wb") as img_file:
                img_file.write(image_bytes)

            extracted_images.append(settings.MEDIA_URL + "extracted_images/" + img_filename)

    return extracted_images

@csrf_exempt  # Add this line to disable CSRF for this function
def upload_pdf(request):
    """ Handle PDF file upload and extract images. """
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]
        file_path = default_storage.save("temp_pdfs/" + pdf_file.name, ContentFile(pdf_file.read()))

        # Extract images from PDF
        extracted_images = extract_images_from_pdf(os.path.join(settings.MEDIA_ROOT, file_path))

        return JsonResponse({"message": "Images extracted successfully!", "images": extracted_images})

    return JsonResponse({"error": "No PDF file uploaded"}, status=400)