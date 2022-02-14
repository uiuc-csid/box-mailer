# Boxmailer

This is a simple script for securely sharing directories or files with students using [Box](https://uofi.app.box.com/). It is FERPA compliant and therefore acceptable for sending grades to students.

## Preparation

The script has two requirements to run:

* a collection of either Box directories (default) or Box files, and
* an `input.csv` describing whom each item should be shared with.

The directories (or files) to be shared **must** exist on your Box before you can run the script. This can be done using a variety of tools such as:

* the official Box clients [Sync](https://support.box.com/hc/en-us/categories/360003187994-Box-Sync) or [Drive](https://www.box.com/resources/downloads), or
* open source tools such as [rclone](https://rclone.org/box/).

### Sharing directories (default)

The most efficient way to distribute files to students is to create a directory for each individual. This makes it easy to update files or add new feedback over time. It also reduces the clutter in a student's Box as all shared items are placed in the service's root directory.

The recommended Box structure for sharing directories is:

```none
cs100-sp20
├── cs100-sp20-netid1
│   ├── feedback1.pdf
│   ├── feedback2.pdf
│   └── ...
├── cs100-sp20-netid2
│   ├── feedback1.pdf
│   ├── feedback2.pdf
│   └── ...
└── ...
```

The corresponding `input.csv` mapping should match the following format:

```csv
login,file
netid1@illinois.edu,cs100-sp20-netid1
netid2@illinois.edu,cs100-sp20-netid2
...
```

### Sharing files

The script can also distribute bare files when the `--files` flag is set.

The recommended Box structure for sharing files is:

```none
cs100-sp20
├── cs100-sp20-netid1-feedback1.pdf
├── cs100-sp20-netid1-feedback2.docx
├── cs100-sp20-netid2-feedback1.pdf
├── cs100-sp20-netid2-feedback2.docx
└── ...
```

The corresponding `input.csv` mapping should match the following format:

```csv
login,file
netid1@illinois.edu,cs100-sp20-netid1-feedback1.pdf
netid1@illinois.edu,cs100-sp20-netid1-feedback2.docx
netid2@illinois.edu,cs100-sp20-netid2-feedback1.pdf
netid2@illinois.edu,cs100-sp20-netid2-feedback2.docx
...
```

## Running

```bash
git clone https://gitlab.engr.illinois.edu/cs-instructional-dev/box-mailer.git box-mailer
cd box-mailer
pipenv install
pipenv run python main.py <name of base folder> # 'cs100-sp20' in the example above
```

The script uses [click](https://click.palletsprojects.com/en/7.x/) for parsing and helpdocs, and the [box-sdk](https://github.com/box/box-python-sdk) to connect to the API. These can be installed manually or through [pipenv](https://pipenv.pypa.io/en/latest/) which will automatically create a virtualenv for the script and install all the requirements. The virtualenv can be accessed with `pipenv run <command>` which runs a command within it, or with `pipenv shell`, which spawns a new shell with the virtualenv actived.

### Required: Box developer token

In order to run the app you must create a [developer token](https://developer.box.com/guides/authentication/access-tokens/developer-tokens/) using the [**DEVELOPER CONSOLE**](https://uofi.app.box.com/developers/console) (If you used rclone you can use the oauth2 credentials created for that instead). This token is refreshed hourly and is scoped to your user rather than having an app-service user. You will need to create a dummy app (`boxmailer-<netid>`) with any type of authentication, and it will take you to the configuration page where you can copy your token.

The token can be passed to the application as either:

* as a command line option (`--dev-token`),
* as an environment variable (`BOXMAILER_DEV_TOKEN`),
* or via interactive prompt if not otherwise provided.

### Optional: Email notifications

The script can also send emails to students notifying them that they have feedback available. This is somewhat redundant as Box will automatically send them a notification when the share is created. However, if you would like to send customized feedback you can customize the `send_email` portion and enable `--send-email=True`. The csv input file is extendable using additional columns that will be available through the user object.
