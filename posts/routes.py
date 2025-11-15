from flask import Blueprint, request, jsonify
from extensions import db
from posts.models import Post
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from flask import current_app, url_for
import os
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


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
    # 1. AUTHENTICATION CHECK
    user_id = get_jwt_identity()
    if user_id is None:
        return jsonify({"error": "Invalid or expired token claims"}), 401
    
    # 2. DATA EXTRACTION & VALIDATION
    # Use .get("key", "") to ensure we start with an empty string, then strip
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not title:
        return jsonify({"error": "Title is required and cannot be empty."}), 422
    if not content:
        return jsonify({"error": "Content is required and cannot be empty."}), 422
    
    tags_string = request.form.get("tags", "[]")
    tags_list = []
    if tags_string and tags_string.strip():
        try:
            tags_list = json.loads(tags_string)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid tags format."}), 422

    image_file = request.files.get("photo")
    image_url = None
    
    try:
        # 3. FILE SAVING LOGIC
        if image_file and image_file.filename:
            # Check if file has an allowed extension (optional but recommended)
            
            filename = secure_filename(image_file.filename) 
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file to the disk
            image_file.save(upload_dir)
            
            # Generate the public URL
            image_url = url_for('static', filename=f'uploads/{filename}', _external=True) 

    except Exception as e:
        # Catch any file system or I/O error during saving
        print(f"File Saving Error: {e}")
        return jsonify({"error": f"Failed to save image: {e}"}), 500


    # 4. DATABASE COMMIT BLOCK
    try:
        post = Post(
            title=title,
            content=content,
            image=image_url,
            tags=tags_list,
            author_id=user_id
        )

        db.session.add(post)
        db.session.commit()
        
        # Success response
        return jsonify({"message": "Post created", "post_id": post.id}), 201

    except IntegrityError as e:
        # Catches primary SQL errors (like NOT NULL constraints)
        db.session.rollback()
        print(f"Database Integrity Error: {e}")
        
        # 🛑 THIS IS THE KEY DEBUG OUTPUT: Use the error message to find the missing field.
        # Check if the error message contains a specific column name (e.g., 'author_id')
        error_detail = "Check database constraints for author_id or other NOT NULL fields."
        return jsonify({"error": f"Post validation failed: {error_detail}"}), 422

    except SQLAlchemyError as e:
        # Catches other SQLAlchemy/DB errors
        db.session.rollback()
        print(f"SQLAlchemy Error: {e}")
        return jsonify({"error": "Database error during post creation."}), 500

    except Exception as e:
        # General unexpected errors
        print(f"Unexpected Error during commit: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

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
