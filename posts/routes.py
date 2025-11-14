from flask import Blueprint, request, jsonify
from extensions import db
from posts.models import Post
from flask_jwt_extended import jwt_required, get_jwt_identity

posts_bp = Blueprint("posts", __name__)

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
