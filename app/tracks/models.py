from sqlalchemy.orm import relationship
from app import db

import geoalchemy2
from app.track_points.models import TrackPoints


class Tracks(db.Model):
    __tablename__ = 'tracks'
    id = db.Column('id', db.BigInteger, db.Sequence('tracks_id_seq'), primary_key=True, index=True, unique=True, autoincrement=True)
    created = db.Column(db.TIMESTAMP, nullable=False)
    uploaded = db.Column(db.TIMESTAMP, nullable=False)
    length = db.Column(db.Numeric(16, 8), nullable=False)
    duration = db.Column(db.BigInteger, nullable=False)
    num_points = db.Column(db.BigInteger, nullable=False)
    public = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.Text)
    comment = db.Column(db.Text)
    city = db.Column(db.Text)
    data_hash = db.Column(db.Text, unique=True)
    extension_geom = db.Column(geoalchemy2.Geometry('POLYGON'), index=True)  # geo index?
    track_geom = db.Column(geoalchemy2.Geometry('LINESTRING'))
    children = relationship("TrackPoints", cascade="all,delete", backref="parent")

    def __init__(self, created, uploaded, length, duration, num_points, public, name, comment, city, data_hash,
                 extension_geom, track_geom):
        # 'id' auto increment
        self.created = created
        self.uploaded = uploaded
        self.length = length
        self.duration = duration
        self.num_points = num_points
        self.public = public
        self.name = name
        self.comment = comment
        self.city = city
        self.data_hash = data_hash
        self.extension_geom = extension_geom
        self.track_geom = track_geom

    def __repr__(self):
        return '<track %i>' % self.id

    def to_dict_short(self):
        return {
                'id': self.id,
                'name': self.name,
               }

    def to_dict_long(self, geometry_short=False):
        if geometry_short:
            geometry = [point.to_dict_short() for point in TrackPoints.query.filter(TrackPoints.id == self.id).all()]
        else:
            geometry = [point.to_dict_long() for point in TrackPoints.query.filter(TrackPoints.id == self.id).all()]
        return {
            'id': self.id,
            'name': self.name,
            'comment': self.comment,
            'created': self.created,
            'length': self.length,
            'duration': self.duration,
            'num_points': self.num_points,
            'geometry': geometry,
               }
