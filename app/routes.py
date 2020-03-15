import os
import uuid

from flask import request, jsonify, make_response

from app import app
from app import db
from app import process_queue
from app.models import MediaFiles
from app.models import Status
import threading
from app.process_media import process_dash_queue, process_abr_queue

ALLOWED_EXTENSIONS = {'mp4', 'mov'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_first_request
def start_queue():
    abr_thread = threading.Thread(target=process_abr_queue)
    dash_thread = threading.Thread(target=process_dash_queue)
    abr_thread.start()
    dash_thread.start()


#POST large file with and process the file
#@insert row in DB
@app.route('/upload_content', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        print("IN Post")
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return jsonify({'input_content_id': "NULL"}), 500
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print('No selected file')
            return jsonify({'input_content_id': "NULL"}), 500
        if file and allowed_file(file.filename):
            content_id = str(uuid.uuid1())
            print(content_id)
            content_dir = app.config['UPLOAD_FOLDER'] + "/" + content_id
            os.makedirs(content_dir)
            print(content_dir)
            file.save(content_dir + '/' + content_id + '.mp4')
            # Async call to ffmpeg for manifest creation
            process_queue.abr_queue.put(content_id)
            item = MediaFiles(media_id=content_id, key="", keyid="", status=Status.UPLOADED)
            db.session.add(item);
            db.session.commit();
        return jsonify({'input_content_id': content_id}), 201


@app.route('/packaged_content', methods=['POST'])
def package_content():
    print("In Package")
    request_ok = False
    key = request.form.get('key')
    keyid = request.form.get('keyid')
    input_content_id = request.form.get('input_content_id')

    if key is not None and len(key) != 32:
        return "Key should be 32 Bytes", 400

    if request.method == 'POST' and \
            key is not None \
            and keyid is not None \
            and input_content_id is not None:
        item = MediaFiles.query.filter_by(media_id=input_content_id).first()
        if item is not None:
            item.key = key
            item.keyid = keyid
            db.session.commit()
            if item.status is Status.ABRVIDEO:
                process_queue.dash_queue.put(input_content_id)
            request_ok = True
        else:
            request_ok = False
    else:
        request_ok = False

    if request_ok:
        return jsonify({"packaged_content_id": input_content_id}), 200
    else:
        return "", 500



@app.route('/packaged_content/<content_id>', methods=['GET'])
def packaged_content(content_id):
    print("IN PackedContent")
    host_url = request.host_url
    item = MediaFiles.query.filter_by(media_id=content_id).first()
    if item is not None and item.status == Status.READY:
        print("Got Item details")
        mpd_path = host_url + app.config['UPLOAD_FOLDER'] + '/' \
                   + content_id + app.config['MANIFEST_SUFFIX'] + '/stream.mpd'
        key = item.key
        keyid = item.keyid
        res = jsonify({"url": mpd_path, "key": key, "kyeid": keyid})
        return res, 200
    elif item is not None:
        return "", 503
    else:
        return "", 404

@app.route('/content/<content_id>/parts/stream.mpd', methods=['GET'])
def getmanifest(content_id):
    manifestfile = app.config['UPLOAD_FOLDER'] + '/' \
                   + content_id + app.config['MANIFEST_SUFFIX'] + \
                   '/stream.mpd'
    data = ''
    if not os.path.exists(manifestfile):
        return "", 500
    with open(manifestfile, 'r') as myfile:
        data = myfile.read()
    response = make_response(data)
    response.headers['Content-Type'] = 'text/xml; charset=utf-8'
    return response

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                filename)
