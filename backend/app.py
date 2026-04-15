from flask import Flask, render_template, request, send_file, abort
import pandas as pd
from datetime import datetime
import os
import tempfile
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "frontend"))
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "ss-solutions-uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(
    __name__,
    template_folder=FRONTEND_DIR,
    static_folder=FRONTEND_DIR,
    static_url_path="",
)

def format_date(date_str):
    return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y%m%d")

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
        date = format_date(str(row['Date']))
        ledger = row['Ledger']
        amount = row['Amount']
        drcr = row['DrCr']

        amt_value = amount if drcr == "Dr" else -amount

        xml += f"""
    <TALLYMESSAGE>
     <VOUCHER VCHTYPE="{row['VoucherType']}" ACTION="Create">
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
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        df = pd.read_excel(filepath)
        xml_data = create_tally_xml(df)

        xml_path = os.path.join(UPLOAD_FOLDER, "tally_import.xml")
        with open(xml_path, "w") as f:
            f.write(xml_data)

        return send_file(xml_path, as_attachment=True)

    return render_template("tally.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)
