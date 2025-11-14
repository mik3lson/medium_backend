from flask import Blueprint, request, jsonify
from extensions import db
from replies.models import Reply
from flask_jwt_extended import jwt_required, get_jwt_identity

replies_bp = Blueprint("replies", __name__)

@replies_bp.post("/<int:post_id>")
@jwt_required()
def create_reply(post_id):
    data = request.json
    user_id = get_jwt_identity()

    reply = Reply(
        content=data["content"],
        post_id=post_id,
        author_id=user_id
    )

    db.session.add(reply)
    db.session.commit()

    return jsonify({"message": "Reply added"})
