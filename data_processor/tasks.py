import logging
from datetime import datetime, timedelta

from celery import shared_task
import xml.etree.ElementTree as ET

from navigation.models import DataCycle
from .models import ArincFile
from .parsers import ARINCParser

logger = logging.getLogger(__name__)


@shared_task
def process_arinc_file(file_id):
    arinc_file = None
    try:
        arinc_file = ArincFile.objects.get(id=file_id)
        arinc_file.status = "PROCESSING"
        arinc_file.save()

        tree = ET.parse(arinc_file.file.path)
        root = tree.getroot()

        cycle_id = root.get("cycle")
        effective_date = datetime.strptime(root.get("effective_date"), "%Y-%m-%d").date()
        expiry_date = effective_date + timedelta(days=28)

        data_cycle, created = DataCycle.objects.get_or_create(
            cycle_id=cycle_id,
            defaults={
                "effective_date": effective_date,
                "expiry_date": expiry_date,
                "source": root.find(".//DATA_SOURCE").text if root.find(".//DATA_SOURCE") is not None else "UNKNOWN",
            },
        )

        arinc_file.cycle = data_cycle
        arinc_file.save()

        parser = ARINCParser(data_cycle)
        parser.parse_file(root)

        arinc_file.status = "COMPLETED"
        arinc_file.save()
        return f"Successfully processed file {arinc_file.file.name}"
    except Exception as e:
        logger.error(f"Error processing file {file_id}: {str(e)}")
        if arinc_file:
            arinc_file.status = "FAILED"
            arinc_file.processing_errors = {"error": str(e)}
            arinc_file.save()
        raise
