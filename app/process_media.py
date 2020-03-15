import subprocess
import os
import time
from app import app
from app import  process_queue
from app.models import db, Status, MediaFiles
from app import abr_files, frag_files


# Command runner function
def run_cmd(cmd):
    stdout = ''
    stderr = ''
    try:
        res = subprocess.Popen(["stdbuf -o0 " + cmd], shell=True,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               close_fds=True)
        stdout, stderr = res.communicate()
        retcode = res.returncode
        retcode = retcode if retcode < 127 else (256 - retcode) * -1
        if retcode:
            print(stdout)
            print(stderr)
            return False
    except BaseException as ex:
        print("Exception")
        print(stderr)
        print(stdout)
        return False
    return True


# Transcoder command to convert input video file into MPEG-DASH
# With 4 manifest files.
def transcode(content_id):
    print(app.config['UPLOAD_FOLDER'])
    content_dir = app.config['UPLOAD_FOLDER'] + '/' + content_id
    # content_parts_dir = app.config['UPLOAD_FOLDER'] + '/' + content_id + '/' + app.config['MANIFEST_SUFFIX']
    # if not os.path.exists(content_parts_dir):
    #     os.makedirs(content_parts_dir)
    file = content_dir + '/' + content_id + '.mp4'
    cmd = app.config['FFMPEG_PATH'] + file + \
          app.config['DASH_VIDEO_5000'] + content_dir + abr_files[0] + \
          app.config['DASH_VIDEO_2000'] + content_dir + abr_files[1] + \
          app.config['DASH_VIDEO_1000'] + content_dir + abr_files[2]
    print("Calling " + " " + cmd)
    ret = run_cmd(cmd)
    print("Video processing finished")
    item = MediaFiles.query.filter_by(media_id=content_id).first()
    if ret is True and item is not None:
        item.status = Status.ABRVIDEO
        db.session.commit()
        if item.key != '' and item.keyid != '':
            process_queue.dash_queue.put(content_id)
    elif ret is False and item is not None:
        item.status = Status.FAILED
        db.session.commit()
    return


# Package content in DASH+CENC
def dash_packer(content_id):
    print(app.config['UPLOAD_FOLDER'])
    item = MediaFiles.query.filter_by(media_id=content_id).first()
    content_dir = app.config['UPLOAD_FOLDER'] + '/' + content_id
    content_parts_dir = content_dir + app.config['MANIFEST_SUFFIX']
    if not os.path.exists(content_parts_dir):
        os.makedirs(content_parts_dir)
    if item is None:
        return False
    file_index = 0
    fragmented_files = ''
    for file in abr_files:
        in_file = content_dir + file;
        out_file = content_dir + frag_files[file_index]
        cmd = app.config['MP4_FRAG'] + in_file + ' ' + out_file
        print(cmd)
        ret = run_cmd(cmd)
        if ret is False:
            item.status = Status.FAILED
            db.session.commit()
            return False
        fragmented_files += out_file + ' '
        file_index += 1
    print(fragmented_files)
    cmd = app.config['MP4_DASH'] + fragmented_files + " --profiles=no-demand --encryption-key=" + \
          item.keyid+':'+item.key + " -f --output-dir=" + content_parts_dir
    print(cmd)
    ret = run_cmd(cmd)
    if ret is False:
        item.status = Status.FAILED
        db.session.commit()
        return False
    item.status = Status.READY
    db.session.commit()
    return True


# Process DASH packager Queue
# Read new jobs content_id and send job to DASH packager
def process_dash_queue():
    while True:
        print("Checking for new dash packing command")
        if process_queue.dash_queue.empty():
            time.sleep(10)
        else:
            content_id = process_queue.dash_queue.get()
            print("Packaging ID " + content_id)
            dash_packer(content_id)
            print("Done packaging " + content_id)


# Generate ABR MPEG-DASH Content for input file
# Watch the abr Q for new jobs and process each job
def process_abr_queue():
    count = 0
    while True:
        print("Checking for new ABR streaming commands" + str(count))
        count += 1
        if process_queue.abr_queue.empty():
            time.sleep(30)
        else:
            content_id = process_queue.abr_queue.get()
            print("Processing ID " + content_id)
            transcode(content_id)
            print("Done processing video for ABR streaming " + content_id)