#@Ns
import os
import json
import requests
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import base64

class WidevineDecrypter:
    def __init__(self, video_url, ott_platform):
        self.video_url = video_url
        self.ott_platform = ott_platform
        self.eme_data = None
        self.init_data = None
        self.session_id = None
        self.license_url = None
        self.decryption_keys = None
        self.widevine_config = None

    def extract_eme_data(self):
        # Extract EME data from video stream
        mpd_manifest = requests.get(self.video_url + '/manifest.mpd').text
        pssh_data = mpd_manifest.split('<cenc:pssh>')[1].split('</cenc:pssh>')[0]
        self.eme_data = base64.b64decode(pssh_data)

    def parse_eme_data(self):
        # Parse EME data
        self.init_data = self.eme_data[:16]
        self.session_id = self.eme_data[16:32]

    def generate_license_request(self):
        # Generate license request
        license_request = {
            'init_data': base64.b64encode(self.init_data).decode(),
            'session_id': base64.b64encode(self.session_id).decode(),
            'ott_platform': self.ott_platform
        }
        return json.dumps(license_request)

    def send_license_request(self, encrypted_license_request):
        # Send license request to license server
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.license_url, data=encrypted_license_request, headers=headers)
        return response.text

    def decrypt_license_response(self, license_response):
        # Decrypt license response
        encrypted_license_response = base64.b64decode(license_response)
        cipher = AES.new(self.decryption_keys, AES.MODE_GCM, self.session_id)
        decrypted_license_response = cipher.decrypt_and_verify(encrypted_license_response, self.init_data)
        return decrypted_license_response

    def extract_decryption_keys(self, decrypted_license_response):
        # Extract decryption keys
        self.decryption_keys = decrypted_license_response[:16]
