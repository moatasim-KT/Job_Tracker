from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
import os

cv_bp = Blueprint('cv', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@cv_bp.route('/cv/upload', methods=['POST'])
def upload_cv():
    if 'cv_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('main.dashboard'))
    file = request.files['cv_file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('main.dashboard'))
    if file and allowed_file(file.filename):
        filename = 'cv.' + file.filename.rsplit('.', 1)[1].lower()
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        flash('CV uploaded successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    else:
        flash('Invalid file type. Only PDF/DOC/DOCX allowed.', 'danger')
        return redirect(url_for('main.dashboard'))

@cv_bp.route('/cv/download')
def download_cv():
    # Find the uploaded CV (if any)
    for ext in ALLOWED_EXTENSIONS:
        path = os.path.join(UPLOAD_FOLDER, f'cv.{ext}')
        if os.path.exists(path):
            return send_from_directory(UPLOAD_FOLDER, f'cv.{ext}', as_attachment=True)
    flash('No CV uploaded yet.', 'warning')
    return redirect(url_for('main.dashboard'))
