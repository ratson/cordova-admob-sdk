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

        shutil.move(os.path.join(
            sdk_dir, 'GoogleMobileAds.framework', 'Modules'), framework_dir)
        shutil.move(os.path.join(
            sdk_dir, 'GoogleMobileAds.framework',
            'Versions', 'A', 'GoogleMobileAds'), framework_dir)
        shutil.move(os.path.join(
            sdk_dir, 'GoogleMobileAds.framework',
            'Versions', 'A', 'Headers'), framework_dir)


def print_release_notes():
    url = 'https://firebase.google.com/docs/admob/release-notes'
    print('fetching {}'.format(url))
    doc = pq(url)
    for h2 in doc('.devsite-article-body > h2').items():
        td_items = list(h2.next('table').find('tr').eq(1).items('td'))
        print(h2.text(), td_items[0].text(), td_items[1].text())
        print(td_items[2].text())
        print()


def ensure_git_clean():
    try:
        subprocess.check_call([
            'git', 'diff-index', '--name-status', '--exit-code', 'HEAD', '--'])
    except subprocess.CalledProcessError as ex:
        print('Error: Git working directory not clean.')
        exit(ex.returncode)


def main():
    print_release_notes()
    ensure_git_clean()

    versions_file = os.path.join(
        os.path.dirname(__file__), 'sdk-versions.json')
    try:
        current_versions = json.load(open(versions_file))
    except FileNotFoundError:
        current_versions = {}

    platform = 'iOS'
    p = platform.lower()
    url = 'https://developers.google.com/admob/{}/download'.format(p)
    print('fetching {}'.format(url))
    doc = pq(url)
    tr = doc('#download{}'.format(p))
    version = tr.find('td').eq(0).text().split(' v')[-1]
    if not version:
        tr0 = doc('table.responsive tr').eq(0)
        version = tr0.text().split(' ')[-1]
        tr = doc('table.responsive tr').eq(1)
    if version in current_versions.get(p, ''):
        return
    download_url = tr.find('td a').attr('href')
    print(platform, version, download_url)
    filehandle, _ = urllib.request.urlretrieve(download_url)
    z = zipfile.ZipFile(filehandle, 'r')
    extract_ios(z, version)
    current_versions[p] = version

    with open(versions_file, 'w') as f:
        json.dump(current_versions, f, sort_keys=True, indent=2)
        f.write('\n')
    subprocess.check_call(['git', 'add', '.'])
    commit_msg = 'Update iOS SDK to v{version}'.format(version=version)
    subprocess.check_call(['git', 'commit', '-m', commit_msg])


if __name__ == '__main__':
    main()
