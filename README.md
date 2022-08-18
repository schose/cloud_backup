cloud backup for splunk
========================================

This app will create backup of your apps and kvstore running in Splunk Cloud or onprem.


#### Amazon S3 ####

configuration parameters

s3_endpoint
s3_accesskey
s3_secretkey
s3_path

### S3 setup ###

#### create a bucket ####

- create bucket
```
aws s3api create-bucket \
    --bucket bw-dev-splunk-backup \
    --region eu-central-1 \
    --create-bucket-configuration LocationConstraint=eu-central-1
```

- arn name = arn:aws:s3:::bw-dev-splunk-backup

#### create a policy ####

- go [Policy generator](https://awspolicygen.s3.amazonaws.com/policygen.html)
- add arn `arn:aws:s3:::bw-dev-splunk-backup,arn:aws:s3:::bw-dev-splunk-backup/*`
- go iam -> create policy

```json
{
  "Id": "Policy1659451801411",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1659451797915",
      "Action": "s3:*",
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::bw-dev-splunk-backup",
        "arn:aws:s3:::bw-dev-splunk-backup/*"
      ]
    }
  ]
}
```
- name devbackup
- create a group devbackup -> assign policy
- create user -> assign group devbackup

#### create a service user ####

https://us-east-1.console.aws.amazon.com/iam/home#/users$new?step=details


### examples ###

- backup all apps without user data to a custom endpoint. ensure connectivity using Network Access Controls:

``` 
| s3backup apps="*" s3_endpoint_url="http://1.2.3.4:9000" s3_key="mykey" s3_region="US" s3_secret="mysecret" s3_bucket_name="appbackups"
```

- get latest kvstore full backup and copy to s3 bucket

``` 
| kvlbackupp s3_endpoint_url="http://1.2.3.4:9000" s3_key="mykey" s3_region="US" s3_secret="mysecret" s3_bucket_name="appbackups"
```

### setup ###

```
| makeresults 
| eval name = "test"
| eval s3_endpoint_url = "http://192.168.53.49:9000"
| eval s3_key = "mykey"
| eval s3_secret = "mysecret"
| eval s3_region = "myregion"
| eval s3_bucket_name = "mybucketname"
| eval s3_backup_prefix = "myprefix"
| outputlookup backupconfig
```