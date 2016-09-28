import json
import os
import shutil
import subprocess
import tempfile
import urllib
import zipfile

try:
    from pyquery import PyQuery as pq
except ImportError:
    print("Run `pip install pyquery`")
    exit()


def extract_ios(zip_file, version):
    dest = 'src/ios'
    framework_dir = os.path.join(dest, 'GoogleMobileAds.framework')
    try:
        shutil.rmtree(dest)
    except FileNotFoundError:
        pass
    finally:
        os.makedirs(framework_dir)
    with tempfile.TemporaryDirectory() as tmpdirname:
        zip_file.extractall(tmpdirname)
        sdk_dir = os.path.join(
            tmpdirname, 'GoogleMobileAdsSdkiOS-{}/'.format(version))
        shutil.move(os.path.join(sdk_dir, 'Mediation Adapters'), dest)

        shutil.move(os.path.join(
            sdk_dir, 'GoogleMobileAds.framework', 'Modules'), framework_dir)
        shutil.move(os.path.join(
            sdk_dir, 'GoogleMobileAds.framework',
            'Versions', 'A', 'GoogleMobileAds'), framework_dir)
        shutil.move(os.path.join(
            sdk_dir, 'GoogleMobileAds.framework',
            'Versions', 'A', 'Headers'), framework_dir)


def extract_wp8(zip_file, version):
    dest = 'src/wp8'
    try:
        os.makedirs(dest)
    except FileExistsError:
        pass
    with tempfile.TemporaryDirectory() as tmpdirname:
        for member in zip_file.namelist():
            if 'lib/windowsphone8' in member:
                filename = zip_file.extract(member, path=tmpdirname)
                if os.path.isfile(filename):
                    shutil.move(filename, dest)


versions_file = 'sdk-versions.json'
try:
    current_versions = json.load(open(versions_file))
except FileNotFoundError:
    current_versions = {}

for platform, extract in (
    ('ios', extract_ios),
    ('wp', extract_wp8),
):
    url = 'https://developers.google.com/admob/{}/download'.format(platform)
    doc = pq(url)
    tr = doc('#download{}'.format(platform))
    version = tr.find('td').eq(0).text().split(' v')[-1]
    if not version:
        tr0 = doc('table.responsive tr').eq(0)
        version = tr0.text().split(' ')[-1]
        tr = doc('table.responsive tr').eq(1)
    if version in current_versions.get(platform, ''):
        continue
    download_url = tr.find('td a').attr('href')
    print(platform, version, download_url)
    filehandle, _ = urllib.request.urlretrieve(download_url)
    z = zipfile.ZipFile(filehandle, 'r')
    extract(z, version)
    current_versions[platform] = version

json.dump(current_versions, open(versions_file, 'w'), sort_keys=True)
