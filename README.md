# Drive Fever

GOOGLE_SPREADHSEEET_SERVICE_ACCOUNT_KEY env variable must point to the mounted file inside docker.
In this case the JSON file is saved in the folder `private/google-service-account.json`

```sh
docker run -it \
  -e GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.metadata.readonly,https://www.googleapis.com/auth/drive.readonly \
  -e GOOGLE_DRIVE_INITIAL_PATH=<your google drive folder> \
  -e GOOGLE_SPREADHSEEET_SERVICE_ACCOUNT_KEY=/drive-fever/private/google-service-account.json
  -e DOWNLOADABLE_MIMETYPES=image/jpg,application/pdf \
  -v data:/drive-fever/data:z \
  -v private:/drive-fever/private \
  c2dhunilu/drive-fever python download.py
```

## development & test
Create an env file:
```
GOOGLE_DRIVE_INITIAL_PATH=your initialpath
GOOGLE_SPREADHSEEET_SERVICE_ACCOUNT_KEY=your path to service account key

```

If a .env file is available with all previous env variables, just:

```
pipenv run python download.py
```
