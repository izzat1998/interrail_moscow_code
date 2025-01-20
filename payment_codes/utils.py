import os
import requests
from datetime import datetime

from django.conf import settings
from docxtpl import DocxTemplate
from interrail_moscow_code.settings import DOC_TO_PDF_CONVERTER_URL


def generate_application_document(application):
    """
    Generate DOCX document from template and convert to PDF using custom converter
    """
    # Path to your template
    template_path = os.path.join(
        settings.BASE_DIR, "templates", "documents", "application_template.docx"
    )

    # Create unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    docx_filename = f"application_{application.id}_{timestamp}.docx"
    pdf_filename = f"application_{application.id}_{timestamp}.pdf"

    # Path for temporary DOCX file
    temp_docx_path = os.path.join(settings.MEDIA_ROOT, "temp", docx_filename)

    # Ensure temp directory exists
    os.makedirs(os.path.join(settings.MEDIA_ROOT, "temp"), exist_ok=True)

    try:
        # Prepare context data for template
        context = {
            "order_number": application.number,
            "date": application.date.strftime("%d.%m.%Y") if application.date else "",
            "sending_type": dict(application.SENDING_TYPE_CHOICES).get(
                application.sending_type, ""
            ),
            "quantity": application.quantity,
            "departure": application.departure,
            "departure_code": application.departure_code,
            "destination": application.destination,
            "destination_code": application.destination_code,
            "cargo": application.cargo,
            "hs_code": application.hs_code,
            "etcng": application.etcng,
            "loading_type": dict(application.LOADING_TYPE_CHOICES).get(
                application.loading_type, ""
            ),
            "weight": application.weight,
            "container_type": dict(application.CONTAINER_TYPE_CHOICES).get(
                application.container_type, ""
            ),
            "paid_telegram": (
                "Прошу также предоставить проплатную телеграмму"
                if application.paid_telegram
                else ""
            ),
            "rolling_stock_1": application.rolling_stock_1,
            "rolling_stock_2": application.rolling_stock_2,
            "conditions_of_carriage": application.conditions_of_carriage,
            "agreed_rate": application.agreed_rate,
            "add_charges": application.add_charges,
            "border_crossing": application.border_crossing,
            "containers_or_wagons": application.containers_or_wagons,
            "period": application.period,
            "shipper": application.shipper,
            "consignee": application.consignee,
            "departure_country": application.departure_country,
            "destination_country": application.destination_country,
            "territories": ", ".join([t.name for t in application.territories.all()]),
            "forwarder": application.forwarder.name if application.forwarder else "",
            "manager": str(application.manager) if application.manager else "",
            "comment": application.comment,
        }

        # Generate DOCX
        doc = DocxTemplate(template_path)
        doc.render(context)
        doc.save(temp_docx_path)

        # Convert to PDF using custom converter
        pdf_relative_path = convert(temp_docx_path, pdf_filename)

        # Clean up temporary DOCX file
        if os.path.exists(temp_docx_path):
            os.remove(temp_docx_path)

        return pdf_relative_path

    except Exception as e:
        # Clean up temporary files in case of error
        if os.path.exists(temp_docx_path):
            os.remove(temp_docx_path)
        raise e


def convert(
    docx_file, file_name, path="applications", timeout=30
):  # 30 seconds default timeout
    url = DOC_TO_PDF_CONVERTER_URL
    try:
        response = requests.post(
            url,
            files={"document": open(docx_file, "rb")},
            timeout=timeout,  # Added timeout parameter
        )
        response.raise_for_status()  # Raise an exception for bad status codes

        with open(f"media/{path}/{file_name}", "wb") as f:
            f.write(response.content)
        print(f"File {file_name} uploaded successfully")
        return f"{path}/" + file_name

    except requests.Timeout:
        print(f"Request timed out after {timeout} seconds")
        raise
    except requests.RequestException as e:
        print(f"Error during conversion: {e}")
        raise
