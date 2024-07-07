import os
import json
import requests
from pyfork import Pyrofork

class HotstarDownloader(Pyrofork):
    def __init__(self, video_url):
        super().__init__()
        self.video_url = video_url
        self.mpd_manifest = None
        self.video_segments = []
        self.audio_segments = []
        self.subtitle_segments = []
        self.download_folder = 'downloads'
        self.upload_mode = False
        self.upload_url = None

    def get_mpd_manifest(self):
        # Get MPD manifest from video URL
        response = requests.get(self.video_url + '/manifest.mpd')
        self.mpd_manifest = response.text

    def parse_mpd_manifest(self):
        # Parse MPD manifest to extract video, audio, and subtitle segments
        mpd_xml = self.mpd_manifest
        video_segments = mpd_xml.split('<SegmentTemplate media="video">')[1].split('</SegmentTemplate>')[0]
        audio_segments = mpd_xml.split('<SegmentTemplate media="audio">')[1].split('</SegmentTemplate>')[0]
        subtitle_segments = mpd_xml.split('<SegmentTemplate media="subtitle">')[1].split('</SegmentTemplate>')[0]
        self.video_segments = [segment.split('<SegmentURL>')[1].split('</SegmentURL>')[0] for segment in video_segments.split('<Segment>')]
        self.audio_segments = [segment.split('<SegmentURL>')[1].split('</SegmentURL>')[0] for segment in audio_segments.split('<Segment>')]
        self.subtitle_segments = [segment.split('<SegmentURL>')[1].split('</SegmentURL>')[0] for segment in subtitle_segments.split('<Segment>')]

    def download_segments(self):
        # Download video, audio, and subtitle segments
        os.makedirs(self.download_folder, exist_ok=True)
        for segment in self.video_segments:
            response = requests.get(self.video_url + '/' + segment, stream=True)
            with open(os.path.join(self.download_folder, segment), 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        for segment in self.audio_segments:
            response = requests.get(self.video_url + '/' + segment, stream=True)
            with open(os.path.join(self.download_folder, segment), 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        for segment in self.subtitle_segments:
            response = requests.get(self.video_url + '/' + segment,
