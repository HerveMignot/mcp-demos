# Deployment Guide for Spare Parts Retailer MCP Server

This guide provides instructions on how to deploy the Spare Parts Retailer Model Context Protocol (MCP) server to Google Cloud Run.

## Prerequisites

Before you begin, ensure you have the following:

*   A Google Cloud Platform (GCP) project.
*   The `gcloud` CLI installed and configured for your GCP project.
*   Docker installed on your local machine.
*   Permissions to create and manage Cloud Run services, Cloud Build, and Artifact Registry/Container Registry in your GCP project.


## 1. Enable Google Cloud APIs

First, enable the necessary Google Cloud APIs for Cloud Build, Cloud Run, and Artifact Registry (or Container Registry) in your GCP project:

```bash
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com --project PROJECT_ID
```

**Important**: Make sure to replace `PROJECT_ID` with your actual Google Cloud Project ID in all gcloud commands.


## 2. Build and Push Docker Image

### 2.1 Create a Artifact Registry for your MCP Servers

You can create a Artifact Registry to store all your MCP servers images.

**Important**: Select your region for creating your registry (e.g.: europe-west1).

```bash
gcloud artifacts repositories create mcp-servers \
    --repository-format=docker \
    --project=PROJECT_ID \
    --location=REGION \
    --description="MCP Servers" \
    --immutable-tags \
    --async
```

### 2.2 Build the Docker image

Navigate to the `servers/spare-parts-retailer` directory, which contains your `Dockerfile` and application code. Then, build your Docker image and push it to your Artifact Registry.

**Important**: Replace `PROJECT_ID` with your actual Google Cloud Project ID, and `REGION` with the region you chose.

```bash
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/mcp-servers/spare-parts-retailer:latest .
```


## 3. Configure `deploy-cloudrun.yaml`

The `deploy-cloud.yaml` file defines your Cloud Run service. Before deploying, you need to update the placeholders in this file:

*   **`PROJECT_ID`**: In the `image` field (`REGION-docker.pkg.dev/PROJECT_ID/spare-parts-retailer:latest`), replace `PROJECT_ID` with your Google Cloud Project ID, and do the same with `REGION`.
*   **`REGION`**: In the `cloud.googleapis.com/location` label, replace `REGION` with your desired Google Cloud region (e.g., `europe-west1`, `us-east1`).

Open `servers/spare-parts-retailer/deploy-cloudrun.yaml` and make these necessary edits.


## 4. Deploy to Cloud Run

Once your Docker image is pushed and `deploy-cloudrun.yaml` is configured, you can deploy your service to Cloud Run using the `gcloud run services replace` command. Ensure you are still in the `servers/spare-parts-retailer` directory.

**Important**: Replace `REGION` and `PROJECT_ID` with your specific values.

```bash
gcloud run services replace deploy-cloudrun.yaml --region REGION --project PROJECT_ID
```

## 5. Verify Deployment

After the deployment command completes, it will output the URL of your newly deployed Cloud Run service. You can also find this URL and check the service status in the Google Cloud Console under Cloud Run.

To get the service URL via the CLI:

```bash
gcloud run services describe spare-parts-retailer-service --region REGION --project PROJECT_ID --format 'value(status.url)'
```

### Port Usage

While you may provide information about which port your MCP server is listening on, Cloud Run will do the mapping between the
https port and the internal port of your MCP server. You do not have to specify the port number when using the Cloud Run service
URL.


## 6. Testing the Service

You can test your deployed MCP server using `curl`.

### Ping/Health Check

To perform a basic health check, send a GET request to the `/health` endpoint:

```bash
curl -X GET <YOUR_CLOUD_RUN_SERVICE_URL>/health
```

In general, you will get a `Not Found` message, but this means the server is listening.

**Note:** `https` URLs from Cloud Run work fine from MCP clients.

### Invoke a Tool (Example: `check_availability`)

We strongly advise to use MCP Inspection tool to test the server, as the use of curl can be harsh due to session
initialization and session id management.

To run MCP Inspection tool:

```bash
npx @modelcontextprotocol/inspector
```

## 7. Cleanup (Optional)

If you wish to remove the deployed service and the Docker image, you can do so with the following commands:

### Delete Cloud Run Service

```bash
gcloud run services delete spare-parts-retailer-service --region REGION --project PROJECT_ID
```

### Delete Docker Image from the Artifact Registry

```bash
gcloud container images delete REGION-docker.pkg.dev/PROJECT_ID/spare-parts-retailer:latest --force-delete-tags --quiet
```

Replace `REGION` and `PROJECT_ID` with your specific values.