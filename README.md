# CloudPix — Cloud-Based Photo Gallery

**CodeAlpha Cloud Computing Internship — project starter**

A simple photo gallery built with Python Flask and Amazon S3. It demonstrates cloud object storage, photo uploads, listing stored objects, temporary download/view links, and deletion.

## Features
- Responsive gallery interface
- Image type validation (PNG, JPG, JPEG, GIF, WEBP)
- 8 MB upload limit
- Unique object names to avoid accidental overwrites
- Amazon S3 upload and listing
- Short-lived pre-signed URLs for viewing photos
- Delete photo action (when S3 is configured)
- Demo mode for checking the UI before AWS setup

## Tech stack
- Python 3.10+
- Flask
- Boto3
- Amazon S3
- HTML and CSS

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create and activate a virtual environment:

   **Windows**
   ```bash
   py -m venv .venv
   .venv\\Scripts\\activate
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   python app.py
   ```
6. Open `http://127.0.0.1:5000`.

Without AWS credentials, the app starts in demo mode so you can inspect the interface. Demo mode does not persist uploaded image bytes and is not the cloud-storage demonstration.

## Configure Amazon S3
1. Sign in to AWS and open the S3 console: https://console.aws.amazon.com/s3/
2. Create a bucket in your chosen region. Bucket names must be globally unique.
3. Keep Block Public Access enabled. This app uses pre-signed URLs rather than making the bucket public.
4. Create an IAM identity with only the required permissions for your bucket: `s3:ListBucket` on the bucket and `s3:PutObject`, `s3:GetObject`, and `s3:DeleteObject` on `arn:aws:s3:::YOUR_BUCKET/photos/*`.
5. Configure the environment variables shown in `.env.example`:
   - `AWS_REGION`
   - `S3_BUCKET`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `FLASK_SECRET_KEY`

   Do not commit `.env`, access keys, or passwords to GitHub. For deployment, prefer the host's secret manager or an IAM role over long-lived access keys.
6. Restart the app and upload a photo. The gallery should list objects from S3.

## GitHub submission
1. Create a public repository named `CodeAlpha_CloudPhotoGallery` (or use the exact repository naming convention your coordinator gave you).
2. Upload the project files, excluding `.venv/`, `.env`, credentials, and personal data.
3. Add screenshots of the running application to a `screenshots/` folder if you can.
4. In your internship submission form, paste the repository URL if it asks for a GitHub link.
5. If asked for a demo video, record a short explanation of the app, upload flow, and S3 bucket object list. Do not show access keys in the video.

## Project explanation for viva
**Problem:** Users need a simple way to keep and view image files in cloud storage.

**Solution:** A Flask web app accepts image uploads and sends them to Amazon S3. The app lists stored images and creates time-limited pre-signed URLs so the bucket does not need to be public.

**Cloud concept:** S3 stores files as objects inside a bucket. Flask handles the web interface and Boto3 communicates with AWS.

**Limitations:** This is a learning starter, not production-ready. It has no user authentication, uses no persistent database for ownership/metadata, and needs deployment hardening before public use. Test only with non-sensitive photos.

## Important
This is a suggested project, not confirmation that it matches your assigned CodeAlpha task. Check your internship task sheet or coordinator's instructions before submitting. Different CodeAlpha batches may have different task lists.
