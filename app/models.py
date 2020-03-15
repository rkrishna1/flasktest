from app import db
import enum


class Status(enum.Enum):
    UPLOADED = 0  # Uplaoded and ready for processing
    ABRVIDEO = 2  # Transcoding to ABR video done
    FAILED = 3  # Failed at some stage
    READY = 4  # Ready for streaming this state is after encryption
    UNKNOWN = 5 #Unknown state Reserved


# Model for saving media files and respective file status
# For ease of use this uses a stand-alone SQLite DB
# @id:auto increment unique id
# @media_id: auto generated uuid for saving media files in file system
# @key: encryption KEY supplied by user
# @keyid: Key ID supplied by user for encryption
# @status: Status of the new upload file [UPLOADED, ABRVIDEO, READY, FAILED, UNKNOWN]
class MediaFiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.String(128))
    key = db.Column(db.String(128))
    keyid = db.Column(db.String(128))
    status = db.Column(db.Enum(Status), default=Status.UNKNOWN)

    def __repr__(self):
        return '<MediaFile {}>'.format(self.media_id)
