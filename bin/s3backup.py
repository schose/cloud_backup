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


@Configuration()
class runme(GeneratingCommand):

    apps = Option(require=True)
    s3_key = Option(require=True)
    s3_secret = Option(require=True)
    s3_region = Option(require=True)
    s3_bucket_name =  Option(require=True)
    s3_endpoint_url =  Option(require=False)
    s3_backup_prefix = Option(require=False)
    userdirs = Option(require=False)

    def generate(self):
        apps = self.apps.split(",")
        self.logger.debug("starting backup for apps: " + self.apps)

        # import sys, os
        # sys.path.append(os.path.join(os.environ['SPLUNK_HOME'],'etc','apps','SA-VSCode','bin'))
        # import splunk_debug as dbg
        # dbg.enable_debugging(timeout=25)

        if self.userdirs == None:
            userdirs = False
        else:
            if self.userdirs.lower() == "t" or self.userdirs.lower() == "true":
                userdirs = True
            else:
                userdirs = False

        if self.s3_backup_prefix is None:
            s3_backup_prefix = "splunk-backups-"
        else:
            s3_backup_prefix = self.s3_backup_prefix

        if self.s3_endpoint_url == None:
            s3_endpoint_url = "https://s3.amazonaws.com"
        else:
            s3_endpoint_url = self.s3_endpoint_url
    
        if apps[0] == '*':
            apps = os.listdir(os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps'))
            self.logger.debug("backup all apps: " + str(apps))

        # my path
        # dp0 = os.path.dirname(__file__)
        splunk_home = os.environ.get('SPLUNK_HOME')
        filename_date = s3_backup_prefix + time.strftime("%Y%m%d-%H%M%S")
        
        # if not os.path.isdir(os.path.join(splunk_home, 'var', 'run', 'tmp')):
        #     os.path.os.mkdir(os.path.join(splunk_home, 'var', 'run', 'tmp'))
        
        # we have to backup to /tmp as /splunk/var/run/tmp is read only fs
        file_path = os.path.join('/','tmp', filename_date +'.tar.gz')

        appdirs = []
        for app in apps:
            appdirs.append(os.path.join(splunk_home, 'etc', 'apps', app))
            if userdirs == True:
                subfolders = search_foldername_recursive(os.path.join(splunk_home, 'etc', 'users'), app)
                for subfolder in subfolders:
                    appdirs.append(subfolder)

        output = "backup folders:" + str(appdirs)
        yield {'_time': time.time(), '': 1, '_raw': output}

        make_tarfile(file_path, appdirs)        

        filesize_in_mb = round(os.path.getsize(file_path) / 1024 / 1024,2)
        filename_only = os.path.basename(file_path) 
        output = "backup done for apps: " + str(apps) + " size: " + str(filesize_in_mb) + " MB" 
        yield {'_time': time.time(), 'event_no': 1, '_raw': output}

        output = "copy to s3 bucket: " + str(file_path)
        upload_to_s3_bucket(s3_endpoint_url, self.s3_key, self.s3_secret, self.s3_region, self.s3_bucket_name, file_path, filename_only)

dispatch(runme, sys.argv, sys.stdin, sys.stdout, __name__)
