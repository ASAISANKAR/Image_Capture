import os
import cv2
from datetime import datetime
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =  'mysql://root:admin@localhost:3306/camera_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def capture_image():
    camera = cv2.VideoCapture(0) 
    ret, frame = camera.read()
    if ret:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        cv2.imwrite(filepath, frame)  # Save image
        camera.release()
        return filename
    camera.release()
    return None

@app.route('/capture', methods=['POST'])
def capture():
    filename = capture_image()
    if filename:
        new_image = Image(image_path=f"static/uploads/{filename}")
        db.session.add(new_image)
        db.session.commit()
    return redirect('/')

@app.route('/')
def index():
    images = Image.query.order_by(Image.timestamp.desc()).all()
    return render_template('index.html', images=images)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if not exists
    app.run(debug=True)
