import os, sys
import time
import tarfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators
from splunklib.six.moves import range

def make_tarfile(output_filename, source_dirs):
    with tarfile.open(output_filename, "w:gz", bufsize=10240) as tar:
        for source_dir in source_dirs:
            tar.add(source_dir, arcname=os.path.basename(source_dir))

def upload_to_s3_bucket(endpoint_url, s3_key, s3_secret, s3_region, s3_bucket_name, s3_file, s3_key_name):
    import boto3
    s3 = boto3.client('s3', endpoint_url=endpoint_url, region_name=s3_region, aws_access_key_id=s3_key, aws_secret_access_key=s3_secret)
    s3.upload_file(s3_file, s3_bucket_name, s3_key_name)

def search_foldername_recursive(path, name):
    folders = []
    for root, dirs, files in os.walk(path):
        if name in dirs:
            folders.append(os.path.join(root, name))

    return folders

def determine_latest_file_in_dir(dir):
    files = os.listdir(dir)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(dir, x)))
    return files[-1]

def determin_latest_file_in_dir_extension(dir, extension):
    files = os.listdir(dir)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(dir, x)))
    for file in files:
        if file.endswith(extension):
            return file
    return None


@Configuration()
class runme(GeneratingCommand):

    s3_key = Option(require=True)
    s3_secret = Option(require=True)
    s3_region = Option(require=True)
    s3_bucket_name =  Option(require=True)
    s3_endpoint_url =  Option(require=False)
    s3_backup_prefix = Option(require=False)

    def generate(self):
        self.logger.debug("starting kvbackup")

        # import sys, os
        # sys.path.append(os.path.join(os.environ['SPLUNK_HOME'],'etc','apps','SA-VSCode','bin'))
        # import splunk_debug as dbg
        # dbg.enable_debugging(timeout=25)

        if self.s3_backup_prefix is None:
            s3_backup_prefix = "splunk-backups-"
        else:
            s3_backup_prefix = self.s3_backup_prefix

        if self.s3_endpoint_url == None:
            s3_endpoint_url = "https://s3.amazonaws.com"
        else:
            s3_endpoint_url = self.s3_endpoint_url

        # my path
        # dp0 = os.path.dirname(__file__)
        latest_backup_filename = determine_latest_file_in_dir(os.path.join(os.environ['SPLUNK_HOME'], 'var', 'lib', 'splunk','kvstorebackup'))
        latest_backup_path = os.path.join(os.environ['SPLUNK_HOME'], 'var', 'lib', 'splunk','kvstorebackup',latest_backup_filename)
        filename_date = s3_backup_prefix + time.strftime("%Y%m%d-%H%M%S")
        output = "backupfile: " + str(latest_backup_path)
        yield {'_time': time.time(), '_raw': output}


        filesize_in_mb = round(os.path.getsize(latest_backup_path) / 1024 / 1024,2)
        filename_only = s3_backup_prefix + time.strftime("%Y%m%d-%H%M%S") + '.tar.gz'
        output = "kvstore backup determinded: " + str(latest_backup_path) + " size: " + str(filesize_in_mb) + " MB" 
        yield {'_time': time.time(), '_raw': output}

        output = "copy to s3 bucket: " + str(latest_backup_path)
        yield {'_time': time.time(), '_raw': output}
        upload_to_s3_bucket(s3_endpoint_url, self.s3_key, self.s3_secret, self.s3_region, self.s3_bucket_name, latest_backup_path, filename_only)

dispatch(runme, sys.argv, sys.stdin, sys.stdout, __name__)
