"""
Ref - if google cloud setup is needed:
https://colab.research.google.com/notebooks/snippets/gcs.ipynb
Change the variable "gcloud_project_id" in this notebook to match
your project-id.

AFTER SETUP GOOGLE CLOUD, MAKE A GOOGLE CLOUD STORAGE BUCKET
Upload a json file there and then change the gs:// URI in the
variables "gcloud_storage_path" and "dotenv_filename" in this notebook.
"""
import os
import sys
import configparser


def envsetup(dotenv_filename, gcloud_project_id=None, gcloud_storage_path=None):
"""
Setup the working environment either in Google colab or in another machine.

# NOTE: I USE DIGITAL OCEAN SPACES "S3-LIKE" OBJECT STORAGE. 
# This setup is to work with this kind of storage.
# Check their documentation at https://www.digitalocean.com/products/spaces

:param str dotenv_filename: The name of the dotenv file with secrets
:param str gcloud_project_id: The google cloud project_id name
:param str gcloud_storage_path: The gcloud storage bucket path
"""
    # This will run only in colab notebooks:
    if "google.colab" in sys.modules:
        # Get into the account.
        # NOTE => THIS WILL OPEN UP A GOOGLE AUTH MODAL IN COLAB!
        from google.colab import auth
        auth.authenticate_user()

        # Set the project in google cloud
        os.system(f"gcloud config set project {gcloud_project_id}")

        # Push keys from gcloud file and put in the right path for s3cmd to work
        dotenv_path = '/root/{dotenv_filename}'
        cmd = f"gsutil cp {gcloud_storage_path}/{dotenv_filename} {dotenv_path}"
        os.system(cmd)

    # This will setup env elsewhere:
    else:
        # Defaults to get the dotenv file in user home. leave the file there first...
        dotenv_path = os.path.join(os.environ['HOME'], dotenv_filename)

    # Setting up env:
    config = configparser.ConfigParser()
    config.read(dotenv_path)

    # Set env vars:
    os.environ['S3_ACCESS_KEY'] = config['default']['access_key']
    os.environ['S3_SECRET_KEY'] = config['default']['secret_key']
    os.environ['S3_ENDPOINT_URL'] = 'https://' + config['default']['host_base']
    os.environ['S3_REGION_NAME'] = config['default']['bucket_location']
    os.environ['GITHUB_TOKEN'] = config['github']['token']
    os.environ['INOVALIFE_ENV'] = 'true'
