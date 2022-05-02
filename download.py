import io
import os
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pathvalidate import sanitize_filename
from googleapiclient.http import MediaIoBaseDownload

# take environment variables from .env.
load_dotenv(override=True)

# Load env variables
SCOPES = os.environ.get('GOOGLE_DRIVE_SCOPES', '').split(',')
KEY_FILEPATH = os.environ.get('GOOGLE_SPREADHSEEET_SERVICE_ACCOUNT_KEY', '')
INITIAL_PATH = os.environ.get('GOOGLE_DRIVE_INITIAL_PATH', '')
DOWNLOADABLE_MIMETYPES = os.environ.get(
    'DOWNLOADABLE_MIMETYPES',
    'image/jpg,application/pdf,image/tiff').split(',')

print(
    'Welcome to Drive Fever!\n\n',
    'DRIVE_FEVER_GIT_TAG:',
    os.environ.get('DRIVE_FEVER_GIT_TAG', 'no tag'), '\n',
    'DRIVE_FEVER_GIT_BRANCH:',
    os.environ.get('DRIVE_FEVER_GIT_BRANCH', 'no branch'), '\n',
    'DRIVE_FEVER_GIT_REVISION',
    os.environ.get('DRIVE_FEVER_GIT_REVISION', 'no revision'), '\n',
    'GOOGLE_DRIVE_SCOPES:', SCOPES, '\n',
    'GOOGLE_SPREADHSEEET_SERVICE_ACCOUNT_KEY:', KEY_FILEPATH, '\n',
    'GOOGLE_DRIVE_INITIAL_PATH:', INITIAL_PATH, '\n',
    'DOWNLOADABLE_MIMETYPES:', DOWNLOADABLE_MIMETYPES
)

if not KEY_FILEPATH or not os.path.exists(KEY_FILEPATH):
    os._exit('credentials file not found, check GOOGLE_SPREADHSEEET_SERVICE_ACCOUNT_KEY env...')

FOLDER = 'application/vnd.google-apps.folder'

credentials = ServiceAccountCredentials.from_json_keyfile_name(
            KEY_FILEPATH, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)


def get_items_in_folder(folder_id, pageToken=None, offset=0):
    results = service.files().list(
        pageSize=10,
        pageToken=pageToken,
        fields="nextPageToken, files(id, name, mimeType)",
        q=f"'{folder_id}' in parents"
    ).execute()
    items = results.get('files', [])
    print(
        f'get_items_in_folder id:{folder_id} offset:{offset}'
        f'\n- items n.:', len(items))
    offset = offset + len(items)
    if results.get('nextPageToken', None) is not None:
        next_items = get_items_in_folder(
            folder_id=folder_id,
            pageToken=results.get('nextPageToken'),
            offset=offset)
        return items + next_items
    return items


def download_file(file_id, file_path, skip_if_exists=True):
    print(f'\ndownload_file {file_id} to {file_path}')
    if skip_if_exists and os.path.exists(file_path):
        print('...skipping, file exists already and skip_if_exists=True')
        return
    fh = io.FileIO(file_path, 'wb')
    request = service.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%")


def download_items(items=[], path='./data'):
    os.makedirs(path, exist_ok=True)
    failed_items = []
    done_items = []
    for item in items:
        file_path = os.path.join(
            path, sanitize_filename(item.get('name')))
        file_id = item.get('id')
        print(file_path, file_id, item.get('mimeType', ''))
        if item.get('mimeType', None) == FOLDER:
            print('create folder:', file_path)
            os.makedirs(file_path, exist_ok=True)
            folder_items = get_items_in_folder(item.get('id'))
            done, failed = download_items(items=folder_items, path=file_path)
            failed_items = failed_items + failed
            done_items = done_items + done
        elif item.get('mimeType', None) in DOWNLOADABLE_MIMETYPES:
            download_file(
                file_id=file_id, file_path=file_path, skip_if_exists=True)
            done_items.append({
                'file_path': file_path,
                'file_id': file_id,
                'mimeType': item.get('mimeType', None)
            })
        else:
            print('could not download item', item)
            failed_items.append({
                'file_path': file_path,
                'file_id': file_id,
                'mimeType': item.get('mimeType', None)
            })
    return done_items, failed_items


if __name__ == '__main__':
    items = get_items_in_folder(INITIAL_PATH)
    done_items, failed_items = download_items(items=items)
    print(f'Done: {len(done_items)}, failed:{len(failed_items)}')
    print(json.dumps(failed_items, indent=4))
