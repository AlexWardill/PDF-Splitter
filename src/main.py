from flask import Flask, render_template, request, redirect, url_for, flash, send_file, send_from_directory 
from werkzeug.utils import secure_filename
import os
from zipfile import ZipFile
from PyPDF2 import PdfFileReader, PdfFileWriter
from pathlib import Path


app = Flask(__name__)
# UPLOAD_FOLDER = "Downloads"
UPLOAD_FOLDER = "Downloads"
ALLOWED_EXTENSIONS = {'pdf'}
secret_key = os.urandom(12).hex()
app.config['SECRET_KEY'] = secret_key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def removeZips():
    home_directory = os.getcwd()
    files_in_directory = os.listdir(home_directory)
    filtered_files = [ file for file in files_in_directory if file.endswith(".zip") ]
    for file in filtered_files:
        path = os.path.join(home_directory, file)
        os.remove(path)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/download", methods=["GET", "POST"])
def download_file():
    removeZips()
    if request.method == "POST":
        file = request.files['file']

        filename = secure_filename(file.filename)
        
        filename = filename.rsplit(".pdf",1)[0] 
        input_pdf = PdfFileReader(file)

        zipObj = ZipFile(f"{filename}_pages.zip", "w")

        for i in range(input_pdf.getNumPages()):
            output_filename = f"{filename} page {i+1}.pdf"
            pdf_writer = PdfFileWriter()
            pdf_writer.addPage(input_pdf.getPage(i))
            with Path(os.getcwd(), output_filename).open(mode="wb+") as output_file:
                pdf_writer.write(output_file)
            zipObj.write(output_filename)
            os.remove(os.path.join(os.getcwd(), output_filename))

        zipObj.close()
        return send_from_directory(os.getcwd(), f"{filename}_pages.zip", as_attachment=True, mimetype="zip") 

    return render_template("index.html")


if __name__ == '__main__':
    app.run()