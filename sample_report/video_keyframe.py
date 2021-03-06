import argparse
import pyffmpeg
import numpy as np
import StringIO
import hashlib
import json
import Image


def update_by_advancing(tree, video, videohash):
    frame_nums = []

    def get_hashes(tree):
        frame_nums.append(tree['frame_num'])
        for subtree in tree['children']:
            get_hashes(subtree)

    get_hashes(tree)

    frame_nums = sorted(frame_nums)
    hashes = {}

    for frame_num in frame_nums:
        frame = video.GetFrameNo(frame_num)

        # Find the hash of the representative image
        s = StringIO.StringIO()
        frame.save(s, 'JPEG')
        s.seek(0)
        imagehash = hashlib.md5(s.buf).hexdigest()
        hashes[frame_num] = imagehash

        # Store the image itself
        if not ARGS.imagedir is None:
            frame = Image.open(s)
            frame.thumbnail((100,100))
            with open('%s/%s.jpg' % (ARGS.imagedir, imagehash), 'wb') as f:
                frame.save(f, 'JPEG')
                print imagehash

    def update_tree(tree):
        tree['image'] = {
            'hash': hashes[tree['frame_num']],
            'video': {'videohash': videohash, 'frame_num': tree['frame_num']},
            'faces': [],
            'categories': [],
        }
        for subtree in tree['children']:
            update_tree(subtree)

    update_tree(tree)


def keyframe_tree(video, range=None, split=10.0, min_interval=0.2):
    """
    Args:
       video: a pyffmpeg stream
       range: (start, stop) time in seconds,
                          None indicates the entire video
    Returns:
        'videohash': <str>
        'range': (start, stop) (interval times, float),
        'frame_num': <int>
        'timestamp': <float>
        'imagehash': <str>
        'children': [<recursive>, <recursive>, ...]
    """
    if range is None:
        range = 0, stream.tv.duration() / stream.tv.get_fps()

    start, stop = range

    # Pick a representative frame from the center of the range
    frame_num = int((start+stop) / 2.0 * stream.tv.get_fps())
    timestamp = frame_num / stream.tv.get_fps()

    # Sub divid the interval
    interval = max((stop-start)/split, min_interval)
    subints = list(np.arange(start, stop, interval)) + [stop]
    subints = zip(subints[:-1], subints[1:])

    if len(subints) > 2:
        children = [keyframe_tree(video, subint, split, min_interval)
                    for subint in subints]
    else:
        children = []

    return {
        'range': (start, stop),
        'frame_num': frame_num,
        'timestamp': timestamp,
        #'imagehash': imagehash,
        'children': children,
        }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='split a video into keyframes and ranges')

    # Input video
    parser.add_argument('videofile', type=str, help='input video file')

    # JSON Output
    parser.add_argument('--outfile', type=str,
                        help='save Video json to this file',
                        default=None)

    # Image directory output
    parser.add_argument('--imagedir', type=str,
                        help='store images here rather than on cassandra')

    ARGS = parser.parse_args()

    with open(ARGS.videofile, 'r') as f:
        videohash = hashlib.md5(f.read()).hexdigest()

    stream = pyffmpeg.VideoStream()
    stream.open(ARGS.videofile)

    keyframes = [keyframe_tree(stream)]
    update_by_advancing(keyframes[0], stream, videohash)

    video = {
        'hash': videohash,
        'duration': stream.tv.duration() / stream.tv.get_fps(),
        'frames': stream.tv.duration(),
        'fps': stream.tv.get_fps(),
        'keyframes': keyframes
        }

    if not ARGS.outfile is None:
        with open(ARGS.outfile, 'w') as f:
            f.write(json.dumps(video))
    else:
        print json.dumps(video)
