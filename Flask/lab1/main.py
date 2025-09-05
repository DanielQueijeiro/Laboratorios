from flask import Flask
from flask_restful import Resource, Api, reqparse, abort

import json

app = Flask("VideoAPI")
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('title', required = True)
parser.add_argument('uploadDate', type=int, required = False)

'''videos = {
    'video1': {'title': 'Hello World in Python','uploadDate':20210917},

    'video2': { 'title': 'Why Matlab is the best language Ever','uploadDate':20211117 }
}
'''
with open("videos.json", 'r') as f:
    videos = json.load(f)

def write_changes_to_file():
    global videos
    videos = { k: v for k, v in sorted(videos.items(),key=lambda video: video[1]["uploadDate"])}
    with open("videos.json", 'w') as f:
        json.dump(videos, f)
#write_changes_to_file()



class Index(Resource):
    def get(self):
        return "Hello World!", 200

class AllVideos(Resource):
    def get(self):
        return videos, 200

class IdVideo(Resource):
    def get(self,video_id):
        allIds = videos.keys()
        if(not video_id in allIds):
            abort(404, message =f"Video {video_id} not found!")
        else:
            return videos[video_id],200

    def put(self, video_id):
        args = parser.parse_args()
        new_video = {'title':args['title'],
                     'uploadDate':args['uploadDate']}
        videos[video_id] = new_video
        write_changes_to_file()
        return {video_id: videos[video_id]}, 201

    def delete(self,video_id):
        if video_id not in videos:
            abort(404, message =f"Video {video_id} not found!")
        del videos[video_id]
        write_changes_to_file()
        return "", 204

class VideoSchedule(Resource):
    def post(self):
        args = parser.parse_args()
        new_video = {'title':args['title'],
                     'uploadDate':args['uploadDate']}
        video_id = max(int(v.lstrip('video')) for v in videos.keys()) + 1
        video_id = f"video{video_id}"
        videos[video_id] = new_video
        write_changes_to_file()
        return videos[video_id], 201

api.add_resource(Index, "/")
api.add_resource(AllVideos,"/videos")
api.add_resource(VideoSchedule,"/videos")
api.add_resource(IdVideo,"/video/<video_id>")

if __name__ == "__main__":
    app.run()