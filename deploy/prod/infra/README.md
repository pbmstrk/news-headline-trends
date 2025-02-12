# Deploying Infrastructure

Most of the cloud resources are managed using Terraform. This includes the databases (CockroachDB and Redis), the cloud run job as well as the storage account used for backups.

In most cases, the infrastructure can be updated using the usual plan-apply cycle. Special care only needs to be taken when first deploying resources. To create the initial deployment:

First, deploy the container registry:

```bash
terraform apply -target=google_artifact_registry_repository.dataload_repo
```

Configure Docker authentication and build/push the container:

```bash
gcloud auth configure-docker europe-west1-docker.pkg.dev

gcloud builds submit --tag europe-west1-docker.pkg.dev/{project-id}/data-load/data-load:latest
```

Deploy all other cloud resources:

```bash
terraform apply
```

## Creating backups from CockroachDB

Data can be exported to cloud storage using the [EXPORT](https://www.cockroachlabs.com/docs/stable/export?filters=cloud) command. There are a [couple options for authenticating](hhttps://www.cockroachlabs.com/docs/stable/cloud-storage-authentication?filters=gcs).

We'll use the service account key created by Terraform (which is already base64 encoded).

To retrieve the encoded secret key run:

```bash
terraform output service_account_key
```

Then to export data to the GCS bucket run the following in the CockroachDB SQL shell:

```text
EXPORT INTO CSV 'gs://news_headline_trends_data_backup/export/headlines?AUTH=specified&CREDENTIALS={encoded key}'
  FROM SELECT uri, headline, pub_date, web_url, section_name FROM nyt_data.headlines;
```

Importing the data works similarly,

```text
IMPORT INTO nyt_data.headlines (uri, headline, pub_date, web_url, section_name)
  CSV DATA ('gs://news_headline_trends_data_backup/export/*.csv?AUTH=specified&CREDENTIALS={encoded key}')
```

> [!Note]
> Use the [ccloud cluster sql](https://www.cockroachlabs.com/docs/cockroachcloud/ccloud-get-started.html#use-a-sql-client-with-a-cluster-using-ccloud-cluster-sql) command to create a connection to the database.