import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-before-deployment")

AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
S3_BUCKET = os.environ.get("S3_BUCKET", "").strip()
AWS_CONFIGURED = bool(S3_BUCKET and os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"))

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8 MB
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

s3 = boto3.client("s3", region_name=AWS_REGION) if AWS_CONFIGURED else None
# Demo-only local metadata. For a real multi-user deployment, use a database.
local_photos = []

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    photos = []
    storage_mode = "Amazon S3" if AWS_CONFIGURED else "Demo mode (local metadata only)"
    if AWS_CONFIGURED:
        try:
            result = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix="photos/")
            for item in result.get("Contents", []):
                key = item["Key"]
                if key.endswith("/"):
                    continue
                url = s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": S3_BUCKET, "Key": key},
                    ExpiresIn=3600,
                )
                photos.append({
                    "key": key,
                    "name": key.split("/", 1)[-1],
                    "url": url,
                    "size": item.get("Size", 0),
                    "date": item.get("LastModified", datetime.now(timezone.utc)).strftime("%d %b %Y"),
                })
        except (BotoCoreError, ClientError) as exc:
            app.logger.exception("Could not list S3 photos")
            flash("S3 se photos load nahi ho paaye. AWS credentials aur bucket permissions check karein.", "error")
    else:
        photos = list(reversed(local_photos))
    return render_template("index.html", photos=photos, storage_mode=storage_mode, aws_configured=AWS_CONFIGURED)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("photo")
    if not file or not file.filename:
        flash("Pehle ek photo select karein.", "error")
        return redirect(url_for("index"))
    if not allowed_file(file.filename):
        flash("Sirf PNG, JPG, JPEG, GIF aur WEBP images allowed hain.", "error")
        return redirect(url_for("index"))

    safe_name = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    content = file.read()
    if len(content) > MAX_FILE_SIZE:
        flash("Photo 8 MB se chhoti honi chahiye.", "error")
        return redirect(url_for("index"))

    if AWS_CONFIGURED:
        try:
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=f"photos/{unique_name}",
                Body=content,
                ContentType=file.mimetype or "application/octet-stream",
            )
            flash("Photo Amazon S3 cloud storage par upload ho gayi!", "success")
        except (BotoCoreError, ClientError):
            app.logger.exception("S3 upload failed")
            flash("Upload fail hua. Bucket name, IAM permissions aur AWS credentials check karein.", "error")
    else:
        # Local preview fallback so the interface can be tested before AWS setup.
        # The file bytes are intentionally not persisted in this demo mode.
        local_photos.append({
            "key": unique_name,
            "name": safe_name,
            "url": "",
            "size": len(content),
            "date": datetime.now().strftime("%d %b %Y"),
        })
        flash("Demo entry add ho gayi. Actual cloud upload ke liye README mein AWS S3 setup karein.", "success")
    return redirect(url_for("index"))

@app.route("/delete", methods=["POST"])
def delete():
    key = request.form.get("key", "")
    if not key.startswith("photos/"):
        flash("Invalid photo key.", "error")
        return redirect(url_for("index"))
    if not AWS_CONFIGURED:
        flash("Delete ke liye AWS S3 configure karna hoga.", "error")
        return redirect(url_for("index"))
    try:
        s3.delete_object(Bucket=S3_BUCKET, Key=key)
        flash("Photo delete kar di gayi.", "success")
    except (BotoCoreError, ClientError):
        app.logger.exception("S3 delete failed")
        flash("Photo delete nahi hui. Permissions check karein.", "error")
    return redirect(url_for("index"))

@app.errorhandler(413)
def too_large(_error):
    flash("Photo 8 MB se chhoti honi chahiye.", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
