# Boxmailer

This is a simple script for securely sharing directories or files with students using [Box](https://uofi.app.box.com/). It is FERPA compliant and therefore acceptable for sending grades to students.

## Installation

The repo can be installed directly as a python package. We recommend installing it either using [pipx](https://github.com/pypa/pipx)(recommended) or using a bare [virtualenv](https://docs.python.org/3/library/venv.html) to avoid polluting your python installation.

### pipx Installation

Pipx is a useful tool that allows you to install command line tools into isolated virtual environments while automatically creating and managing them. It also places scripts onto the user's path so that they do not have to activate the venv by hand each time they want to use the command. Because of this, it is the recommended method for installing small scripts like this.

After installing pipx following the [instructions here](https://github.com/pypa/pipx#install-pipx) you can install the package in an isolated virtual environment with a single command

```bash
pipx install git+https://github.com/uiuc-csid/box-mailer.git
box-mailer <options>
```

### Pip Installation

Find a suitable place on your machine and create a virtual environment using `python -m venv $VENV-LOCATION`.

Then activate the virtual environment and install the package. Note: You will need to activate the virtual environment before each time you use the script in order to put it on your path. If pip is out of date, the library installation may fail.

```bash
source $VENV-LOCATION/bin/activate
pip install -U pip
pip install git+https://github.com/uiuc-csid/box-mailer.git
box-mailer <options>
```

### Required: Box developer token

In order to run the app you must create a [developer token](https://developer.box.com/guides/authentication/access-tokens/developer-tokens/) using the [**DEVELOPER CONSOLE**](https://uofi.app.box.com/developers/console) (If you used rclone you can use the oauth2 credentials created for that instead). This token is refreshed hourly and is scoped to your user rather than having an app-service user. You will need to create a dummy app (`boxmailer-<netid>`) with any type of authentication, and it will take you to the configuration page where you can copy your token.

The token can be passed to the application as either:

* as a command line option (`--dev-token`),
* as an environment variable (`BOXMAILER_DEV_TOKEN`),
* or via interactive prompt if not otherwise provided.

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

### Optional: Email notifications

The script can also send emails to students notifying them that they have feedback available. This is somewhat redundant as Box will automatically send them a notification when the share is created. However, if you would like to send customized feedback you can customize the `send_email` portion and enable `--send-email=True`. The csv input file is extendable using additional columns that will be available through the user object.
