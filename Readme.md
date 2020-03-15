# Python Flask App to process video for DASH Streaming


1. Folder app has all the key components
    * __init__.py has flask app and configs
    * config.py has db SQLite configuration
    * models.py has db model __[id|media_id|key|keyid|status]__
    * process_media.py has several utility functions to process video
    * process_queue.py has Queue decleration
    * routes.py has API routes
2. Bin has MP4 Dash utilities [https://www.bento4.com/]
3. MediaContent is saved in **content** folder
    * content/uuid/<uuid.mp4>: Original uploaded content
    * content/uuid/out* : ABR files
    * content/uuid/parts: MPEG-DASH files
4. Processing:
       * **Upload Video -> ABR-Q -> ABR VIDEO -> DASH-Q -> MPEG-DASH -> READY**
5. ABR processing generates 3 renditions 5mbps, 2mbps and 1mbps
   
#Running the App

1. docker build . -t rktn_assignment
2. docker run -it -p 5000:5000 rktn_assignment:latest
3. Import postman collection from "postman_collection"