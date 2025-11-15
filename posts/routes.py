from flask import Blueprint, request, jsonify
from extensions import db
from posts.models import Post
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from flask import current_app, url_for
import os
from werkzeug.utils import secure_filename

posts_bp = Blueprint("posts", __name__)
"""
@posts_bp.post("/")
@jwt_required()
def create_post():
    data = request.json
    user_id = get_jwt_identity()

    post = Post(
        title=data["title"],
        content=data["content"],
        image=data.get("image"),
        tags=data.get("tags", []),
        author_id=user_id
    )

    db.session.add(post)
    db.session.commit()

    return jsonify({"message": "Post created", "post_id": post.id})
"""
@posts_bp.post("/")
@jwt_required()
def create_post():
    user_id = get_jwt_identity()
    
    # 1. Get Text Data
    title = request.form.get("title")
    content = request.form.get("content")
    tags_string = request.form.get("tags", "[]")
    
    tags_list = []
    if tags_string and tags_string.strip():
        try:
            tags_list = json.loads(tags_string)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid tags format"}), 422

    # 2. Get Image File
    image_file = request.files.get("photo")
    image_url = None
    
    # 🛑 REPLACE PLACEHOLDER WITH FILE SAVING LOGIC 🛑
    if image_file and image_file.filename:
        # Sanitize filename (highly recommended in production!)
        filename = secure_filename(image_file.filename) 
        
        # Define the local path where the file will be saved
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file to the disk
        image_file.save(upload_dir)
        
        # Generate the public URL to be stored in MySQL
        # The 'static' endpoint maps to the static folder defined in your Flask app.
        image_url = url_for('static', filename=f'uploads/{filename}', _external=True) 
    
    # Simple validation check
    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 422
        
    # 3. Create the Post (MySQL INSERT happens here)
    post = Post(
        title=title,
        content=content,
        image=image_url,  # <-- Storing the public URL in the database
        tags=tags_list,
        author_id=user_id
    )

    db.session.add(post)
    db.session.commit()

    return jsonify({"message": "Post created", "post_id": post.id}), 201

@posts_bp.get("/")
def get_posts():
    posts = Post.query.order_by(Post.datetime.desc()).all()
    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "content": p.content[:150] + "...",
            "author": p.author.username,
            "claps": p.claps,
            "tags": p.tags,
        }
        for p in posts
    ])

@posts_bp.post("/<int:id>/clap")
@jwt_required()
def clap_post(id):
    post = Post.query.get_or_404(id)
    post.claps += 1
    db.session.commit()
    return jsonify({"message": "Clapped!"})
