from db import db

class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relationship with PlaylistModel
    playlists = db.relationship('PlaylistModel', back_populates='user',lazy='dynamic',cascade='all, delete') 
