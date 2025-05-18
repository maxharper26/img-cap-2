

# To use on an AWS Linux instance
# #!/bin/bash
# sudo yum install python3-pip -y
# pip install flask
# pip install mysql-connector-python
# pip install boto3 werkzeug
# sudo yum install -y mariadb105

import boto3  # AWS S3 SDK
import mysql.connector  # MySQL database connector
from flask import Flask, request, render_template, jsonify  # Web framework
from werkzeug.utils import secure_filename  # Secure filename handling
import base64  # Encoding image data for API processing
from io import BytesIO  # Handling in-memory file objects


# Flask app setup
app = Flask(__name__)

# AWS S3 Configuration, REPLACE with your S3 bucket
S3_BUCKET = "img-cap-bucket-v2"
S3_REGION = "us-east-1"


def get_s3_client():
    """Returns a new S3 client that automatically refreshes credentials if using an IAM role."""
    return boto3.client("s3", region_name=S3_REGION)


# Allowed file types for upload
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
DB_HOST = "img-caption-database.c7nv5bx3rqxu.us-east-1.rds.amazonaws.com"
DB_NAME = "mydb"
DB_USER = "admin"
DB_PASSWORD = "img-cap-pwd300"

def allowed_file(filename):

    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        return connection
    except mysql.connector.Error as err:
        print("Error connecting to database:", err)
        return None

@app.route("/")
def upload_form():
    """Render the homepage with the file upload form."""
    return render_template("index.html")

@app.route("/upload", methods=["GET", "POST"])
def upload_image():
    """
    Handles image upload, stores the file in AWS S3,
    generates a caption using Gemini API, and saves metadata in MySQL RDS.
    """
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("upload.html", error="No file selected")

        file = request.files["file"]

        if file.filename == "":
            return render_template("upload.html", error="No file selected")

        if not allowed_file(file.filename):
            return render_template("upload.html", error="Invalid file type")

        filename = secure_filename(file.filename)
        file_data = file.read()  # Read file as binary

        # Upload file to S3
        try:
            s3 = get_s3_client()  # Get a fresh S3 client
            s3.upload_fileobj(BytesIO(file_data), S3_BUCKET, filename)
        except Exception as e:
            return render_template("upload.html", error=f"S3 Upload Error: {str(e)}")


        return render_template("upload.html")

    return render_template("upload.html")

@app.route("/gallery")
def gallery():
    """
    Retrieves images and their captions from the database,
    generates pre-signed URLs for secure access, and renders the gallery page.
    """
    try:
        connection = get_db_connection()
        if connection is None:
            return render_template("gallery.html", error="Database Error: Unable to connect to the database.")
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT image_key, caption FROM captions ORDER BY uploaded_at DESC")
        results = cursor.fetchall()
        connection.close()

        images_with_captions = [
            {
                "url": get_s3_client().generate_presigned_url(
                    "get_object",
                    Params={"Bucket": S3_BUCKET, "Key": row["image_key"]},
                    ExpiresIn=3600,  # URL expires in 1 hour
                ),
                "thumbail_url": get_s3_client().generate_presigned_url(
                    "get_object",
                    Params={"Bucket": S3_BUCKET, "Key": f"thumbnails/{row['image_key']}"},
                    ExpiresIn=3600,  # URL expires in 1 hour
                ),
                "caption": row["caption"],
            }
            for row in results
        ]


        return render_template("gallery.html", images=images_with_captions)

    except Exception as e:
        return render_template("gallery.html", error=f"Database Error: {str(e)}")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
