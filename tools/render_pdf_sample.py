from pathlib import Path

from app.services.pdf_report_service import PDFReportService
from tests.test_pdf_report import sample_report_data


def main() -> None:
    output = Path("output/pdf/sample-approved-report.pdf")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(PDFReportService().build(sample_report_data()))
    print(output.resolve())


if __name__ == "__main__":
    main()
