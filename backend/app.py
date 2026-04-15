from flask import Flask, render_template, request, send_file, abort
import pandas as pd
from datetime import datetime
import os
import tempfile
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "frontend"))
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "ss-solutions-uploads")
ALLOWED_EXTENSIONS = {".xlsx", ".xls"}
REQUIRED_COLUMNS = {"Date", "Ledger", "Amount", "DrCr", "VoucherType"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(
    __name__,
    template_folder=FRONTEND_DIR,
    static_folder=FRONTEND_DIR,
    static_url_path="",
)


def format_date(value):
    if pd.isna(value):
        raise ValueError("The Date column contains an empty value.")

    parsed = pd.to_datetime(value, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        raise ValueError(f"Unsupported date value: {value}")

    return parsed.strftime("%Y%m%d")


def create_tally_xml(df):
    xml = """<ENVELOPE>
 <HEADER>
  <TALLYREQUEST>Import Data</TALLYREQUEST>
 </HEADER>
 <BODY>
  <IMPORTDATA>
   <REQUESTDESC>
    <REPORTNAME>Vouchers</REPORTNAME>
   </REQUESTDESC>
   <REQUESTDATA>
"""

    for _, row in df.iterrows():
        date = format_date(row["Date"])
        ledger = str(row["Ledger"])
        amount = float(row["Amount"])
        drcr = str(row["DrCr"]).strip().lower()
        voucher_type = str(row["VoucherType"])

        if drcr not in {"dr", "cr"}:
            raise ValueError("DrCr must contain only 'Dr' or 'Cr'.")

        amt_value = amount if drcr == "dr" else -amount

        xml += f"""
    <TALLYMESSAGE>
     <VOUCHER VCHTYPE="{voucher_type}" ACTION="Create">
      <DATE>{date}</DATE>
      <LEDGERENTRIES.LIST>
       <LEDGERNAME>{ledger}</LEDGERNAME>
       <AMOUNT>{amt_value}</AMOUNT>
      </LEDGERENTRIES.LIST>
     </VOUCHER>
    </TALLYMESSAGE>
"""

    xml += """
   </REQUESTDATA>
  </IMPORTDATA>
 </BODY>
</ENVELOPE>
"""
    return xml


def read_excel_file(filepath, extension):
    if extension == ".xls":
        return pd.read_excel(filepath, engine="xlrd")
    return pd.read_excel(filepath, engine="openpyxl")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/tally", methods=["GET", "POST"])
def tally():
    if request.method == "POST":
        file = request.files.get("file")

        if file is None or not file.filename:
            abort(400, description="Please choose an Excel file to convert.")

        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            abort(400, description="Please upload a .xlsx or .xls Excel file.")

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            df = read_excel_file(filepath, extension)
        except ImportError:
            abort(400, description="This Excel format is not supported by the current server configuration.")
        except Exception as exc:
            abort(400, description=f"Could not read the Excel file: {exc}")

        missing_columns = REQUIRED_COLUMNS - set(df.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            abort(400, description=f"Missing required columns: {missing}")

        try:
            xml_data = create_tally_xml(df)
        except ValueError as exc:
            abort(400, description=str(exc))
        except Exception as exc:
            abort(400, description=f"Could not convert the Excel data: {exc}")

        xml_path = os.path.join(UPLOAD_FOLDER, "tally_import.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_data)

        return send_file(xml_path, as_attachment=True)

    return render_template("tally.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
