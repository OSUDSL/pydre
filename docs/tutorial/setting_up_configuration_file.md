---
title: Setting up Configuration File 
---

# Setting up the `.env` configuration file

When using DuckLake as the data source, pydre requires a `.env` file containing the credentials and configuration values needed to connect to the DuckLake metadata database and S3 data storage.

The following variables can be configured in the `.env` file:

* `DB_USERNAME`: PostgreSQL username used to connect to the DuckLake metadata database. 
* `DB_PASSWORD`: Password for the PostgreSQL user. 
* `DUCKLAKE_HOST`: Hostname or IP address of the PostgreSQL server.
* `DUCKLAKE_PORT`: Port used by the PostgreSQL server. Defaults to `5432`.
* `DUCKLAKE_DATABASE`: Name of the PostgreSQL database containing the DuckLake metadata. 
* `DUCKLAKE_METADATA_SCHEMA`: Schema containing the DuckLake metadata tables. 
* `DUCKLAKE_DATA_PATH`: Data storage path. When using S3 as the data storage backend, the S3 bucket is used to construct the data path. 
* `DUCKLAKE_STORAGE_BACKEND`: Storage backend used by DuckLake. Currently, only `s3` is supported. 
* `DUCKLAKE_S3_ENDPOINT`: S3 service endpoint. 
* `DUCKLAKE_S3_BUCKET`: Name of the S3 bucket containing the data. 
* `DUCKLAKE_S3_KEY_ID`: S3 access key ID. 
* `DUCKLAKE_S3_SECRET`: S3 secret access key. 
* `DUCKLAKE_S3_VERIFY_SSL`: Whether SSL certificate verification is enabled for the S3 connection. 