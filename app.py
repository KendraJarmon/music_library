from dataclasses import fields
from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import environ

from marshmallow import ValidationError, post_load, fields

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models

class Music(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    album = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.Date)
    genre = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'{self.title} {self.artist} {self.album} {self.release_date} {self.genre}'

# Schemas

class MusicSchema(ma.Schema):
    id = fields.Integer(primary_key=True)
    title = fields.String(required=True)
    artist = fields.String(required=True)
    album = fields.String(required=True)
    release_date = fields.Date()
    genre = fields.String(required=True)

    class Meta:
        fields = ('id', 'title', 'artist', 'album', 'release_date', 'genre')

    @post_load
    def create_Music(self, data, **kwargs):
        return Music(**data)

music_schema = MusicSchema()
music_list_schema = MusicSchema(many=True)

# Resources
class MusicListResource(Resource):
    def get(self):
        all_music = Music.query.all()
        return music_list_schema.dump(all_music)

    def post(self):
        form_data = request.get_json()
        try:
            new_music = music_schema.load(form_data)
            db.session.add(new_music)
            db.session.commit()
            return music_schema.dump(new_music), 201
        except ValidationError as err:
            return err.messages, 400
    
class MusicResource(Resource):
    def get(self, music_id):
        music_from_db =Music.query.get_or_404(music_id)
        return music_schema.dump(music_from_db)

    def delete(self, music_id):
        music_from_db = Music.query.get_or_404(music_id)
        db.session.delete(music_from_db)
        return "", 204

    def put(self, music_id):
        music_from_db = Music.query.get_or_404(music_id)
        if 'title' in request.json:
            music_from_db.title = request.json['title']
        if 'artist' in request.json:
            music_from_db.artist = request.json['artist']
        if 'album' in request.json:
            music_from_db.album = request.json['album']
        if 'release_date' in request.json:
            music_from_db.release_date = request.json['release_date']
        if 'genre' in request.json:
            music_from_db.genre = request.json['genre']
        db.session.commit()
        return music_schema.dump(music_from_db)
    
    

# Routes
api.add_resource(MusicListResource,"/api/music")
api.add_resource(MusicResource, '/api/music/<int:music_id>')

