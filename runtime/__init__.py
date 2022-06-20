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


def envsetup(dotenv_filename=".s3cfg", gcloud_project_id=None, gcloud_storage_path=None):
    """
    Setup the working environment either in Google colab or in another machine.

    # NOTE: I USE DIGITAL OCEAN SPACES "S3-LIKE" OBJECT STORAGE. 
    # This setup is to work with this kind of storage.
    # Check their documentation at https://www.digitalocean.com/products/spaces

    :param str dotenv_filename: The name of the dotenv file with secrets
    :param str gcloud_project_id: The google cloud project_id name
    :param str gcloud_storage_path: The gcloud storage bucket path e.g. "gs://my-storage-path"
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

    
def setup_s3(dotenv_filename=".s3cfg", gcloud_project_id=None, gcloud_storage_path=None):
    """
    Setup S3 support for Digital Ocean in Google colab or in another machine.
    
    Returns a "s3" file system object. You can use it like the example:
    # TO READ:
    import pandas as pd
    from runtime import setup_s3
   
    
    s3 = setup_s3(".s3cfg", "project-id", "gs://my-storage-path")
    
    df = pd.read_csv(
        s3.open("s3://your-bucket-name/your-file.txt"),
        sep='==',
        header=None)

    # TO WRITE:
    df.to_csv(
        s3.open("s3://your-bucket-name/your-new-file.txt", 'w'),
        index=None)
    

    # NOTE: I USE DIGITAL OCEAN SPACES "S3-LIKE" OBJECT STORAGE. 
    # This setup is to work with this kind of storage.
    # Check their documentation at https://www.digitalocean.com/products/spaces

    :param str dotenv_filename: The name of the dotenv file with secrets
    :param str gcloud_project_id: The google cloud project_id name
    :param str gcloud_storage_path: The gcloud storage bucket path like "gs://my-storage-path"
    """
    import s3fs
    
    
    if os.environ.get('INOVALIFE_ENV') != 'true':
        envsetup(dotenv_filename, gcloud_project_id=None, gcloud_storage_path=None)
    
    return s3fs.S3FileSystem(
        key=os.environ['S3_ACCESS_KEY'],
        secret=os.environ['S3_SECRET_KEY'],
        client_kwargs={
            'endpoint_url': os.environ['S3_ENDPOINT_URL'],
            'region_name': os.environ['S3_REGION_NAME']
        }
    )


def setup_spark(dotenv_filename=".s3cfg", gcloud_project_id=None, gcloud_storage_path=None):
    """
    Setup PySpark S3 support for Digital Ocean in Google colab or in another machine.

    # NOTE: I USE DIGITAL OCEAN SPACES "S3-LIKE" OBJECT STORAGE. 
    # This setup is to work with this kind of storage.
    # Check their documentation at https://www.digitalocean.com/products/spaces

    :param str dotenv_filename: The name of the dotenv file with secrets
    :param str gcloud_project_id: The google cloud project_id name
    :param str gcloud_storage_path: The gcloud storage bucket path like "gs://my-storage-path"
    """
    from pyspark.sql import SparkSession
    
    
    if os.environ.get('INOVALIFE_ENV') != 'true':
        envsetup(dotenv_filename, gcloud_project_id=None, gcloud_storage_path=None)
    
    return (SparkSession
        .builder
        .appName('pyspark-with-s3-support')
        .config('spark.jars.packages', 'com.amazonaws:aws-java-sdk-bundle:1.11.819,org.apache.hadoop:hadoop-aws:3.2.0')
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.committer.name", "directory")
        .config("spark.hadoop.fs.s3a.committer.staging.tmp.path", "/tmp/staging")
        .config("spark.hadoop.mapreduce.reduce.speculative","false")
        .config("spark.hadoop.fs.s3a.endpoint", os.environ['S3_ENDPOINT_URL'])
        .config("spark.hadoop.fs.s3a.access.key", os.environ['S3_ACCESS_KEY'])
        .config("spark.hadoop.fs.s3a.secret.key", os.environ['S3_SECRET_KEY'])
        .getOrCreate()
       )
