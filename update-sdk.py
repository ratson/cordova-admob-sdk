"""
pip install requests pyquery
"""
import json
import urllib
import subprocess
import zipfile

from pyquery import PyQuery as pq

try:
    current_versions = json.load(open('update-sdk.json'))
except FileNotFoundError:
    current_versions = {}

for platform, folder in (
    ('ios', 'src/ios'),
    ('wp', 'src/wp8'),
):
    url = 'https://developers.google.com/admob/{}/download'.format(platform)
    doc = pq(url)
    tr = doc('#download{}'.format(platform))
    version = tr.find('td').eq(0).text().split(' v')[-1]
    if version in current_versions.get(platform, ''):
        continue
    download_url = tr.find('td a').attr('href')
    filehandle, _ = urllib.request.urlretrieve(download_url)
    z = zipfile.ZipFile(filehandle, 'r')
    z.extractall(folder)
    print(version, download_url)
    current_versions[platform] = version

json.dump(current_versions, open('update-sdk.json', 'w'))
