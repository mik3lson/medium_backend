from flask import Blueprint, request, jsonify
from extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from users.models import SavedPost, Follower
from auth.models import User
from posts.models import Post

users_bp = Blueprint("users", __name__)

# GET USER PROFILE
@users_bp.get("/<int:id>")
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "profile_picture": user.profile_picture
    })


# FOLLOW USER
@users_bp.post("/follow/<int:id>")
@jwt_required()
def follow_user(id):
    user_id = get_jwt_identity()

    if id == user_id:
        return jsonify({"error": "You cannot follow yourself"}), 400

    if Follower.query.filter_by(follower_id=user_id, following_id=id).first():
        return jsonify({"message": "Already following"}), 200

    follow = Follower(follower_id=user_id, following_id=id)
    db.session.add(follow)
    db.session.commit()

    return jsonify({"message": "Followed"})


# UNFOLLOW
@users_bp.post("/unfollow/<int:id>")
@jwt_required()
def unfollow_user(id):
    user_id = get_jwt_identity()

    relation = Follower.query.filter_by(follower_id=user_id, following_id=id).first()
    if not relation:
        return jsonify({"error": "Not following"}), 404

    db.session.delete(relation)
    db.session.commit()

    return jsonify({"message": "Unfollowed"})


# SAVE POST
@users_bp.post("/save/<int:post_id>")
@jwt_required()
def save_post(post_id):
    user_id = get_jwt_identity()

    if SavedPost.query.filter_by(user_id=user_id, post_id=post_id).first():
        return jsonify({"message": "Already saved"}), 200

    save = SavedPost(user_id=user_id, post_id=post_id)
    db.session.add(save)
    db.session.commit()

    return jsonify({"message": "Post saved"})


# GET SAVED POSTS
@users_bp.get("/saved")
@jwt_required()
def get_saved_posts():
    user_id = get_jwt_identity()

    saved = SavedPost.query.filter_by(user_id=user_id).all()
    post_ids = [s.post_id for s in saved]

    posts = Post.query.filter(Post.id.in_(post_ids)).all()

    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "author": p.author.username,
            "claps": p.claps,
            "image": p.image,
            "content": p.content[:150] + "...",
            "tags": p.tags,
        }
        for p in posts
    ])

# GET ALL USERS
@users_bp.get("/")
def get_all_users():
    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "userImg": u.profile_picture
        }
        for u in users
    ])
