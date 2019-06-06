import cv2
import zmq
import json
import numpy as np
import base64
import time
import youtube_dl

ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})

with ydl:
    result = ydl.extract_info(
        'https://www.youtube.com/watch?v=jbYHrhTi1F4',
        # 'https://www.youtube.com/watch?v=-NxlCCW8T8U',
        download=True # We just want to extract the info
    )

if 'entries' in result:
    # Can be a playlist or a list of videos
    video = result['entries'][0]
else:
    # Just a video
    video = result


# video_name = result["id"] + video["ext"] + ".mp4"
video_name = result["id"] + video["ext"] + ".mkv"
print(video_name)

print(video["fps"])
print(video["height"])
print(video["width"])

fps = video["fps"]

# __      ___     _              ______            _
# \ \    / (_)   | |            |  ____|          | |
#  \ \  / / _  __| | ___  ___   | |__ ___  ___  __| |
#   \ \/ / | |/ _` |/ _ \/ _ \  |  __/ _ \/ _ \/ _` |
#    \  /  | | (_| |  __/ (_) | | | |  __/  __/ (_| |
#     \/   |_|\__,_|\___|\___/  |_|  \___|\___|\__,_|

vidcap = cv2.VideoCapture(video_name)
# vidcap = cv2.VideoCapture('hello.mp4')
width = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
x, y, h, w = int(width - 250), 300, 250, 250
# x, y, h, w = int(width - 600), 300, 600, 600
frame_count = 0


#  __________  __  __   _______ ____     ____   _____ _____
# |___  / __ \|  \/  | |__   __/ __ \   / __ \ / ____|  __ \
#    / / |  | | \  / |    | | | |  | | | |  | | |    | |__) |
#   / /| |  | | |\/| |    | | | |  | | | |  | | |    |  _  /
#  / /_| |__| | |  | |    | | | |__| | | |__| | |____| | \ \
# /_____\___\_\_|  |_|    |_|  \____/   \____/ \_____|_|  \_\


pub = zmq.Context()
queue = pub.socket(zmq.PUB)
queue.connect('tcp://localhost:6748')
queue.bind('tcp://127.0.0.1:6748')

# we need this helper to seralize the np image


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """

    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,
                              np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):  # This is the fix
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

 #  __  __          _____ _   _   _      ____   ____  _____
 # |  \/  |   /\   |_   _| \ | | | |    / __ \ / __ \|  __ \
 # | \  / |  /  \    | | |  \| | | |   | |  | | |  | | |__) |
 # | |\/| | / /\ \   | | | . ` | | |   | |  | | |  | |  ___/
 # | |  | |/ ____ \ _| |_| |\  | | |___| |__| | |__| | |
 # |_|  |_/_/    \_\_____|_| \_| |______\____/ \____/|_|


while True:
    
    try:
        success, frame = vidcap.read()
        if success:

            # only every 5th frame
            # if frame_count%60==0:
            if frame_count%fps==0: # 1 frame per second
                
                frame = np.asarray(frame)
                crop_img = frame[y:y+h, x:x+w].copy()

                frame = cv2.resize(crop_img, (480, 480))  # resize the frame
                # frame = cv2.resize(crop_img, (640, 480))  # resize the frame

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.bitwise_not(frame)

                encoded, buffer = cv2.imencode('.jpg', frame)
                # footage_socket.send_string(base64.b64encode(buffer))
                # topic = "1"
                messagedata = base64.b64encode(buffer)

                # queue.send_json({"img": crop_img}, cls=NumpyEncoder)
                # queue.send(base64.b64encode(b'david'))
                queue.send(messagedata)

                cv2.imshow('frame', frame)
                time.sleep(2)
        else:
            break
        print(frame_count)
        frame_count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except KeyboardInterrupt:
        print("\n\nBye bye\n")
        break
