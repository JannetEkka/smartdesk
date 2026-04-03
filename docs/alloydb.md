# AlloyDB — Reference Guide

> Consolidated from Track 3 codelabs: AlloyDB Quick Setup, Real-Time Surplus Engine with Gemini 3 Flash, Configure Vector Search in AlloyDB

---

## Track 3 Overview

**Track 3 - Build AI-powered applications using AI-ready databases like AlloyDB**

**Track focus**

This track focuses on using AI-ready, fully managed databases to build and modernise applications with built-in AI capabilities. Participants learn how to use AlloyDB to enable natural language–driven data interactions. The emphasis is on simplifying data access while improving performance and scalability.

**Hands-on Labs**

Use Model Context Protocol (MCP) Tools with ADK Agents

Codelabs 1: [AlloyDB Quick Setup | Google Codelabs](https://codelabs.developers.google.com/quick-alloydb-setup?hl=en)
Codelabs 2:[Building a Real-Time Surplus Engine with Gemini 3 Flash & AlloyDB | Google Codelabs](https://codelabs.developers.google.com/gemini-3-flash-on-alloydb-sustainability-app?hl=en)

Overview

This lab teaches you how to build an AI agent using ADK that connects to external tools through an MCP server. You’ll create a tour guide agent that fetches animal data from a zoo MCP server and enriches responses using Wikipedia. The lab demonstrates how to separate AI reasoning from data and tool access using secure APIs.

**What you'll learn**

How to deploy AlloyDB for Postgres

- How to enable AlloyDB AI natural language

- How to create and tune a configuration for AI natural language

How to generate SQL queries and get results using natural language

**Google Skills Lab (Optional)**

Configure Vector Search in AlloyDB (suggested)

Google Skills Lab: [Configure Vector Search in AlloyDB](https://www.skills.google/focuses/119405?catalog_rank=%7B%22rank%22%3A6%2C%22num_filters%22%3A0%2C%22has_search%22%3Atrue%7D&parent=catalog&search_id=66805173) (suggested)
In this lab, you learn how to:

- Configure an AlloyDB database to support vector search

- Create a table and load data in AlloyDB

- Generate and store text embeddings in AlloyDB

Perform vector search in AlloyDB using text embeddings

**Project Submission **

**Problem Statement**

Build a **small AI-enabled database feature** using **AlloyDB for PostgreSQL** that enables users to **query a custom dataset using natural language** and receive meaningful results.

The goal of this mini project is to demonstrate how **AI-ready databases can be applied to a specific data use case**, beyond a guided lab environment.

**What You Must Build**

You must build **one database-centric capability** using AlloyDB that satisfies **all** of the following:

Build a simple software setup where:

- **A dataset of your choice** (different from the lab’s default dataset) is stored in AlloyDB

- **At least one table schema is modified or created by you** 

- **AlloyDB AI natural language** is enabled for this dataset

- A **natural language query related to your dataset’s context** is provided
5.The system:

- Converts the natural language input into a SQL query

- Executes the query against AlloyDB

- Returns relevant results from your dataset

**Explicit Constraint (Prevents Lab Reuse)**

- You **may use the lab as a reference**, but:
The dataset **must not be the default lab dataset**
At least **one query must be your own**, not copied from the lab

- The use case must be **described in one sentence** (e.g., “Querying sales data”, “Exploring support tickets”)

---

## Codelab 1: AlloyDB Quick Setup

AlloyDB Quick Setup Lab

About this codelab

subjectLast updated Mar 28, 2026

account_circleWritten by Author: Abirami Sukumaran

[1. Overview](https://codelabs.developers.google.com/quick-alloydb-setup?hl=en)

With this codelab, we will demonstrate a simple, easy-to-do method for setting up AlloyDB.

What you'll build

As part of this, you will create an AlloyDB instance and cluster in one click installation and you'll learn to set it up quickly in your future projects as well.

Requirements

- A browser, such as [Chrome](https://www.google.com/chrome/) or [Firefox](https://www.mozilla.org/en-US/firefox/)

- A Google Cloud project with billing enabled.

[2. Before you begin](https://codelabs.developers.google.com/quick-alloydb-setup?hl=en)

Create a project

- In the [Google Cloud Console](https://console.cloud.google.com/?utm_campaign=CDR_0x1d2a42f5_default_b419133749&utm_medium=external&utm_source=blog), on the project selector page, select or create a Google Cloud [project](https://cloud.google.com/resource-manager/docs/creating-managing-projects?utm_campaign=CDR_0x1d2a42f5_default_b419133749&utm_medium=external&utm_source=blog).

- Make sure that billing is enabled for your Cloud project. Learn how to [check if billing is enabled on a project](https://cloud.google.com/billing/docs/how-to/verify-billing-enabled?utm_campaign=CDR_0x1d2a42f5_default_b419133749&utm_medium=external&utm_source=blog)**.**

**For trying this ****codelab**** out, you can use the GCP Trial Billing Credit Link: **[**https://bit.ly/ez-alloydb-1**](https://bit.ly/ez-alloydb-1)

**How to redeem credits using this link? **[**Refer**](https://codelabs.developers.google.com/codelabs/cloud-codelab-credits)**.**

- You'll use [Cloud Shell](https://cloud.google.com/cloud-shell/?utm_campaign=CDR_0x1d2a42f5_default_b419133749&utm_medium=external&utm_source=blog), a command-line environment running in Google Cloud. Click Activate Cloud Shell at the top of the Google Cloud console.

- Once connected to Cloud Shell, you check that you're already authenticated and that the project is set to your project ID using the following command:

gcloud auth list

- Run the following command in Cloud Shell to confirm that the gcloud command knows about your project.

gcloud config list project

- If your project is not set, use the following command to set it:

gcloud config set project <YOUR_PROJECT_ID>

- Enable the required APIs: Follow the [link](https://console.cloud.google.com/apis/enableflow?apiid=alloydb.googleapis.com,compute.googleapis.com,cloudresourcemanager.googleapis.com,servicenetworking.googleapis.com,run.googleapis.com,cloudbuild.googleapis.com,cloudfunctions.googleapis.com,aiplatform.googleapis.com&utm_campaign=CDR_0x1d2a42f5_default_b419133749&utm_medium=external&utm_source=blog) and enable the APIs.

Alternatively you can use the gcloud command for this. Refer [documentation](https://cloud.google.com/sdk/gcloud/reference/config/list?utm_campaign=CDR_0x1d2a42f5_default_b419133749&utm_medium=external&utm_source=blog) for gcloud commands and usage.

- AlloyDB API

- Compute Engine API

- Cloud Resource Manager API

- Service Networking API

- Cloud Run Admin API

- Cloud Build API

- Cloud Functions API

- Vertex AI API

[3. Why AlloyDB for your business data & AI?](https://codelabs.developers.google.com/quick-alloydb-setup?hl=en)

AlloyDB for PostgreSQL isn't just another managed Postgres service. It is a fundamental modernization of the engine designed for the AI era. Here is why it stands alone compared to standard databases:

- **Hybrid Transactional ****&**** Analytical Processing (HTAP)**

Most databases force you to move data to a data warehouse for analytics. AlloyDB has a built-in **Columnar Engine** that automatically keeps relevant data in a column store in-memory. This makes analytical queries up to **100x faster** than standard PostgreSQL, allowing you to run real-time business intelligence on your operational data without complex ETL pipelines.

- **Native AI Integration:**

AlloyDB bridges the gap between your data and Generative AI. With the google_ml_integration extension, you can call Vertex AI models (like Gemini) directly within your SQL queries. This means you can perform sentiment analysis, translation, or entity extraction as a standard database transaction, ensuring data security and minimizing latency.

- **Superior Vector Search:**

While standard PostgreSQL uses pgvector, AlloyDB supercharges it with the **ScaNN**** index** (Scalable Nearest Neighbors), developed by Google Research. This provides significantly faster vector similarity search and higher recall at scale compared to standard HNSW indexes found in other Postgres offerings. It enables you to build high-performance RAG (Retrieval Augmented Generation) applications natively.

- **Performance at Scale:**

AlloyDB offers up to **4x faster** transactional performance than standard PostgreSQL. It separates compute from storage, allowing them to scale independently. The storage layer is intelligent, handling write-ahead logging (WAL) processing to offload work from the primary instance.

- **Enterprise Availability:**

It offers a **99.99% uptime SLA**, inclusive of maintenance. This level of reliability for a PostgreSQL-compatible database is achieved through a cloud-native architecture that ensures rapid failure recovery and storage durability.

[4. AlloyDB setup](https://codelabs.developers.google.com/quick-alloydb-setup?hl=en)

In this lab we'll use AlloyDB as the database for the test data. It uses *clusters* to hold all of the resources, such as databases and logs. Each cluster has a *primary instance* that provides an access point to the data. Tables will hold the actual data.

Let's create an AlloyDB cluster, instance and table where the test dataset will be loaded.

- Click the button or Copy the link below to your browser where you have the Google Cloud Console user logged in.

[One Click & Run](https://ssh.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/AbiramiSukumaran/easy-alloydb-setup&cloudshell_open_in_editor=README.md&&cloudshell_tutorial=tutorial.md)

Alternative approach to clicking the above button (recommended):

# 1. Clone the repository
git clone https://github.com/GoogleCloudPlatform/devrel-demos.git

# 2. Navigate to the project directory
cd devrel-demos/infrastructure/easy-alloydb-setup

- Once this step is complete the repo will be cloned to your local cloud shell editor and you will be able to run the command below from within the project folder (important to make sure you are in the project directory):

sh run.sh

- Now use the UI (clicking the link in the terminal or clicking the "preview on web" link in the terminal.

- Enter your details for project id, cluster and instance names to get started.

- Go grab a coffee while the logs scroll & you can read about how it's doing this behind the scenes here.

**If you want to test it locally or from anywhere, go to the ****AlloyDB**** instance, click "EDIT" and click "Enable Public IP" or "Public IP Connectivity" (not the outbound one) and enter "0.0.0.0/0" in "Authorized External Networks" for development purposes but once done, remove ****&**** disable public ****ip**** connectivity.**

[5. Setup Illustrated](https://codelabs.developers.google.com/quick-alloydb-setup?hl=en)

[6. Cleanup](https://codelabs.developers.google.com/quick-alloydb-setup?hl=en)

Once this trial lab is done, do not forget to delete alloyDB cluster and instance.

**Go to **[**https://console.cloud.google.com/alloydb/clusters**](https://console.cloud.google.com/alloydb/clusters)**. Select the cluster you want to delete by clicking on the vertical ellipsis next to it and click DELETE.**

It should clean up the cluster along with its instance(s).

---

## Codelab 2: Building a Real-Time Surplus Engine with Gemini 3 Flash & AlloyDB

Building a Real-Time Surplus Engine with Gemini 3 Flash & AlloyDB

About this codelab

subjectLast updated Mar 28, 2026

account_circleWritten by Author: Abirami Sukumaran

[1. Overview](https://codelabs.developers.google.com/gemini-3-flash-on-alloydb-sustainability-app?hl=en)

In this codelab, you will build Neighbor Loop, a sustainable surplus-sharing app that treats intelligence as a first-class citizen of the data layer.

By integrating Gemini 3.0 Flash and AlloyDB AI, you will move past basic storage into the realm of In-Database Intelligence. You'll learn how to perform multimodal item analysis and semantic discovery directly within SQL, eliminating the "AI Tax" of latency and architectural bloat.

What you'll build

A high-performance "swipe-to-match" web application for community surplus sharing.

What you'll learn

- One-Click Provisioning: How to set up an AlloyDB cluster and instance designed for AI workloads.

- In-Database Embeddings: Generating text-embedding-005 vectors directly within INSERT statements.

- Multimodal Reasoning: Using Gemini 3.0 Flash to "see" items and generate witty, dating-style bios automatically.

- Semantic Discovery: Performing logic-based "vibe checks" inside SQL queries using the ai.if() function to filter results based on context, not just math.

The Architecture

Neighbor Loop bypasses traditional application-layer bottlenecks. Instead of pulling data out to process it, we use:

- **AlloyDB**** AI:** To generate and store vectors in real-time.

- **Google Cloud Storage:** To store images

- **Gemini 3.0 Flash:** To perform sub-second reasoning on image and text data directly via SQL.

- **Cloud Run:** To host a lightweight, single-file Flask backend.

Requirements

- A browser, such as [Chrome](https://www.google.com/chrome/) or [Firefox](https://www.mozilla.org/en-US/firefox/).

- A Google Cloud project with billing enabled.

- Basic familiarity with SQL and Python.

[2. Before you begin](https://codelabs.developers.google.com/gemini-3-flash-on-alloydb-sustainability-app?hl=en)

Create a project

- In the [Google Cloud Console](https://console.cloud.google.com/?utm_campaign=CDR_0x1d2a42f5_default_b419133749&utm_medium=external&utm_source=blog), on the project selector page, select or create a Google Cloud [project](https://cloud.google.com/resource-manager/docs/creating-managing-projects?utm_campaign=CDR_0x1d2a42f5_default_b419133749&utm_medium=external&utm_source=blog).

- Make sure that billing is enabled for your Cloud project. Learn how to [check if billing is enabled on a project](https://cloud.google.com/billing/docs/how-to/verify-billing-enabled?utm_campaign=CDR_0x1d2a42f5_default_b419133749&utm_medium=external&utm_source=blog)**.**

**For trying this ****codelab**** out, you can use the GCP Trial Billing Credit Link: **[**https://bit.ly/ez-alloydb3**](https://bit.ly/ez-alloydb3)

**How to redeem credits using this link? **[**Refer**](https://codelabs.developers.google.com/codelabs/cloud-codelab-credits)**.**

- You'll use [Cloud Shell](https://cloud.google.com/cloud-shell/?utm_campaign=CDR_0x1d2a42f5_default_b419133749&utm_medium=external&utm_source=blog), a command-line environment running in Google Cloud. Click Activate Cloud Shell at the top of the Google Cloud console.

- Once connected to Cloud Shell, you check that you're already authenticated and that the project is set to your project ID using the following command:

gcloud auth list

- Run the following command in Cloud Shell to confirm that the gcloud command knows about your project.

gcloud config list project

- If your project is not set, use the following command to set it:

gcloud config set project <YOUR_PROJECT_ID>

- Enable the required APIs: Follow the [link](https://console.cloud.google.com/apis/enableflow?apiid=alloydb.googleapis.com,compute.googleapis.com,cloudresourcemanager.googleapis.com,servicenetworking.googleapis.com,run.googleapis.com,cloudbuild.googleapis.com,cloudfunctions.googleapis.com,aiplatform.googleapis.com) and enable the APIs.

Alternatively you can use the gcloud command for this. Refer [documentation](https://cloud.google.com/sdk/gcloud/reference/config/list?utm_campaign=CDR_0x1d2a42f5_default_b419133749&utm_medium=external&utm_source=blog) for gcloud commands and usage.

Gotchas & Troubleshooting

| **The "Ghost Project" **Syndrome | You ran gcloud config set project, but you're actually looking at a different project in the Console UI. **Check the project ID in the top-left dropdown!** |
| --- | --- |
| **The Billing **Barricade | You enabled the project, but forgot the billing account. AlloyDB is a high-performance engine; it won't start if the "gas tank" (billing) is empty. |
| **API Propagation **Lag | You clicked "Enable APIs," but the command line still says Service Not Enabled. Give it 60 seconds. The cloud needs a moment to wake up its neurons. |
| **Quota **Quags | If you're using a brand-new trial account, you might hit a regional quota for AlloyDB instances. If us-central1 fails, try us-east1. |
| **"Hidden" Service Agent** | Sometimes the AlloyDB Service Agent **isn't** automatically granted the aiplatform.user role. If your SQL queries can't talk to Gemini later, this is usually the culprit. |

[3. Database setup](https://codelabs.developers.google.com/gemini-3-flash-on-alloydb-sustainability-app?hl=en)

In this lab we'll use AlloyDB as the database for the test data. It uses *clusters* to hold all of the resources, such as databases and logs. Each cluster has a *primary instance* that provides an access point to the data. Tables will hold the actual data.

Let's create an AlloyDB cluster, instance and table where the test dataset will be loaded.

- Click the button or Copy the link below to your browser where you have the Google Cloud Console user logged in.

[One Click & Run](https://ssh.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/AbiramiSukumaran/easy-alloydb-setup&cloudshell_open_in_editor=README.md&&cloudshell_tutorial=tutorial.md)

- Once this step is complete the repo will be cloned to your local cloud shell editor and you will be able to run the command below from with the project folder (important to make sure you are in the project directory):

sh run.sh

- Now use the UI (clicking the link in the terminal or clicking the "preview on web" link in the terminal.

- Enter your details for project id, cluster and instance names to get started.

- Go grab a coffee while the logs scroll & you can read about how it's doing this behind the scenes here.

**Important: For testing it locally or from anywhere, go to the ****AlloyDB**** instance, click "EDIT" and click "Enable Public IP" or "Public IP Connectivity" (not the outbound one) and enter "0.0.0.0/0" in "Authorized External Networks" for development purposes but once done, remove ****&**** disable public ****ip**** connectivity.**

Gotchas & Troubleshooting

| **The "Patience" Problem** | Database clusters are heavy infrastructure. If you refresh the page or kill the Cloud Shell session because it "looks stuck," you might end up with a "ghost" instance that is partially provisioned and impossible to delete without manual intervention. |
| --- | --- |
| **Region Mismatch** | If you enabled your APIs in us-central1 but try to provision the cluster in asia-south1, you might run into quota issues or Service Account permission delays. Stick to one region for the whole lab! |
| **Zombie Clusters** | If you previously used the same name for a cluster and didn't delete it, the script might say the cluster name already exists. **Cluster names must be unique within a project.** |
| **Cloud Shell Timeout** | If your coffee break takes 30 minutes, Cloud Shell might go to sleep and disconnect the sh run.sh process. Keep the tab active! |

[4. Schema Provisioning](https://codelabs.developers.google.com/gemini-3-flash-on-alloydb-sustainability-app?hl=en)

Once you have your AlloyDB cluster and instance running, head over to the AlloyDB Studio SQL editor to enable the AI extensions and provision the schema.

You may need to wait for your instance to finish being created. Once it is, sign into AlloyDB using the credentials you created when you created the cluster. Use the following data for authenticating to PostgreSQL:

- Username : "postgres"

- Database : "postgres"

- Password : "alloydb" (or whatever you set at the time of creation)

Once you have authenticated successfully into AlloyDB Studio, SQL commands are entered in the Editor. You can add multiple Editor windows using the plus to the right of the last window.

You'll enter commands for AlloyDB in editor windows, using the Run, Format, and Clear options as necessary.

Enable Extensions

For building this app, we will use the extensions pgvector and google_ml_integration. The pgvector extension allows you to store and search vector embeddings. The google_ml_integration extension provides functions you use to access Vertex AI prediction endpoints to get predictions in SQL. [Enable](https://cloud.google.com/alloydb/docs/reference/extensions) these extensions by running the following DDLs:

CREATE EXTENSION IF NOT EXISTS google_ml_integration CASCADE;
CREATE EXTENSION IF NOT EXISTS vector;

Create a table

You can create a table using the DDL statement below in the AlloyDB Studio:

-- Items Table (The "Profile" you swipe on)
CREATE TABLE items (
   item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
   owner_id UUID,
   provider_name TEXT,
   provider_phone TEXT,
   title TEXT,
   bio TEXT,
   category TEXT,
   image_url TEXT,
   item_vector VECTOR(768),
   status TEXT DEFAULT 'available',
   created_at TIMESTAMP DEFAULT NOW()
);

-- Swipes Table (The Interaction)
CREATE TABLE swipes (
   swipe_id SERIAL PRIMARY KEY,
   swiper_id UUID,
   item_id UUID REFERENCES items(item_id),
   direction TEXT CHECK (direction IN ('left', 'right')),
   is_match BOOLEAN DEFAULT FALSE,
   created_at TIMESTAMP DEFAULT NOW()
);

The item_vector column will allow storage for the vector values of the text.

Grant Permission

Run the below statement to grant execute on the "embedding" function:

GRANT EXECUTE ON FUNCTION embedding TO postgres;

Grant Vertex AI User ROLE to the AlloyDB service account

From **Google Cloud IAM console**, grant the AlloyDB service account (that looks like this: service-<<PROJECT_NUMBER>>@gcp-sa-alloydb.iam.gserviceaccount.com) access to the role "Vertex AI User". PROJECT_NUMBER will have your project number.

Alternatively you can run the below command from the Cloud Shell Terminal:

PROJECT_ID=$(gcloud config get-value project)

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")@gcp-sa-alloydb.iam.gserviceaccount.com" \
--role="roles/aiplatform.user"

Register Gemini 3 Flash model in AlloyDB

Run the below SQL statement from the AlloyDB Query Editor

CALL google_ml.create_model(
   model_id => 'gemini-3-flash-preview',
   model_request_url => 'https://aiplatform.googleapis.com/v1/projects/<<YOUR_PROJECT_ID>>/locations/global/publishers/google/models/gemini-3-flash-preview:generateContent',
   model_qualified_name => 'gemini-3-flash-preview',
   model_provider => 'google',
   model_type => 'llm',
   model_auth_type => 'alloydb_service_agent_iam'
);
--replace <<YOUR_PROJECT_ID>> with your project id.

Gotchas & Troubleshooting

| **The "Password Amnesia" Loop** | If you used the "One Click" setup and can't remember your password, go to the Instance basic information page in the console and click "Edit" to reset the postgres password. |
| --- | --- |
| **The "Extension Not Found" Error** | If CREATE EXTENSION fails, it's often because the instance is still in a "Maintenance" or "Updating" state from the initial provisioning. Go check if instance creation step is complete and wait a few seconds if needed. |
| **The IAM Propagation Gap** | You ran the gcloud IAM command, but the SQL CALL still fails with a permission error. **IAM changes can take a little time to propagate** through the Google backbone. Take a breath. |
| **Vector Dimension Mismatch** | The items table is set to VECTOR(768). If you try to use a different model (like a 1536-dim model) later, your inserts will explode. Stick to text-embedding-005. |
| **Project ID Typo** | In the create_model call, if you leave the brackets « » or mistype your project ID, the model registration will look successful but fail during the first actual query. Double-check your string! |

[5. Image Storage (Google Cloud Storage)](https://codelabs.developers.google.com/gemini-3-flash-on-alloydb-sustainability-app?hl=en)

To store the photos of our surplus items, we use a GCS bucket. For the purpose of this demo app, we want the images to be publicly accessible so they render instantly in our swipe cards.

- **Create a Bucket: **[**Create**](https://console.cloud.google.com/storage/create-bucket) a new bucket in your GCP project (e.g., neighborloop-images), preferably in the same region as your database and application.

- **Configure Public Access:** * Navigate to the bucket's **Permissions** tab.

- Add the **allUsers** principal.

- Assign the **Storage Object Viewer** role (so everyone can see the photos) and the **Storage Object Creator** role (for demo upload purposes).

**Alternative** (Service Account): If you prefer not to use public access, ensure your application's Service Account is granted full access to AlloyDB and the necessary Storage roles to manage objects securely.

Gotchas & Troubleshooting

| **The Region Drag** | If your database is in us-central1 and your bucket is in europe-west1, you are literally slowing down your AI. The "vibe check" happens fast, but fetching the image for the UI will feel sluggish. **Keep them in the same region!** |
| --- | --- |
| **Bucket Name Uniqueness** | Bucket names are a global namespace. If you try to name your bucket neighborloop-images, someone else likely already has it. If your creation fails, **add a random suffix.** |
| **The "Creator" vs. "Viewer" Mix-up** | **The "Creator" vs. "Viewer" Mix-up:** If you only add "Viewer," your app will crash when a user tries to list a new item because it doesn't have permission to *write* the file. You need both for this specific demo setup. |

[6. Let's create the application](https://codelabs.developers.google.com/gemini-3-flash-on-alloydb-sustainability-app?hl=en)

Clone this repo into your project and let's walk through it.

[Github Repo](https://github.com/AbiramiSukumaran/neighbor-loop)

- To clone this, from your Cloud Shell Terminal (in the root directory or from wherever you want to create this project), run the following command:

git clone https://github.com/AbiramiSukumaran/neighbor-loop

This should create the project and you can verify that in the Cloud Shell Editor.

- How to get your Gemini API Key

- Visit Google AI Studio: Go to [aistudio.google.com](http://aistudio.google.com/).

- Sign In: Use the **same** Google Account you are using for your Google Cloud project.

- Create API Key:

- On the left-hand sidebar, click on "Get API key".

- Click the button "Create API key in new project".

- Copy the Key: Once the key is generated, click the copy icon.

- Now set the environment variables in the .env file

GEMINI_API_KEY=<<YOUR_GEMINI_API_KEY>>
DATABASE_URL=postgresql+pg8000://postgres:<<YOUR_PASSWORD>>@<<HOST_IP>>:<<PORT>>/postgres
GCS_BUCKET_NAME=<<YOUR_GCS_BUCKET>>

Replace the values for placeholders <<YOUR_GEMINI_API_KEY>>, <<YOUR_PASSWORD>, <<HOST_IP>>, <<PORT>> and <<YOUR_GCS_BUCKET>>.

**Important: Your HOST_IP should be the public IP address of your ****AlloyDB**** instance in this case when you're testing locally. You can find this in ****AlloyDB**** instance's "Connectivity Configuration" section. Click that "View Connectivity Configuration" link and from the "Connectivity" page that opens up, copy the instance's host and port from the "Public IP Address" entry.**

Gotchas & Troubleshooting

| **Multiple Account Confusion** | If you are logged into multiple Google accounts (Personal vs. Work), AI Studio might default to the wrong one. **Check the avatar in the top right corner** to ensure it matches your GCP Project account. |
| --- | --- |
| **The "Free Tier" Quota Hit** | If you are using the Free of Charge tier, there are rate limits (RPM - Requests Per Minute). If you "swipe" too fast in Neighbor Loop, you might get a 429 Too Many Requests error. **Slow down!** |
| **Exposed Key Security** | If you accidentally git commit your .env file with the key inside. Always add .env to your .gitignore. |
| **The "Connection Timeout" Void** | You used the Private IP address in your .env file but you are trying to connect from outside the VPC (like your local machine). Private IPs are only reachable from within the same Google Cloud network. Switch to the Public IP! |
| **The Port 5432 Assumption** | While 5432 is the standard PostgreSQL port, AlloyDB sometimes requires specific port configurations if you are using an Auth Proxy. For this lab, ensure you are using :5432 at the end of your host string. |
| **The "Authorized Networks" Gatekeeper** | Even if you have the Public IP, AlloyDB will "Refuse Connection" unless you have whitelisted the IP address of the machine running the code.**Fix****: **In the AlloyDB instance settings, add 0.0.0.0/0 (for temporary **testing** only!) or your specific IP to the Authorized Networks. |
| **SSL/TLS Handshake Failure** | AlloyDB prefers secure connections. If your DATABASE_URL doesn't specify the driver correctly (like using **pg8000**), the handshake might fail silently, leaving you with a generic "Database not reachable" error. |
| **The "Primary vs. Read Pool" Swap** | If you accidentally copy the IP address of the Read Pool instead of the Primary Instance, your app will work for searching items but will crash with a "Read-only" error when you try to list a new item. Always use the Primary Instance IP for writes. |

[7. Let's check the code](https://codelabs.developers.google.com/gemini-3-flash-on-alloydb-sustainability-app?hl=en)

The "Dating Profile" for your Stuff

When a user uploads a photo of an item, they shouldn't have to write a long description. I use Gemini 3 Flash to "see" the item and write the listing for them.

In the backend, the user just provides a title and a photo. Gemini handles the rest:

prompt = """
You are a witty community manager for NeighborLoop.
Analyze this surplus item and return JSON:
{
   "bio": "First-person witty dating-style profile bio for the product, not longer than 2 lines",
   "category": "One-word category",
   "tags": ["tag1", "tag2"]
}
"""
response = genai_client.models.generate_content(
   model="gemini-3-flash-preview",
   contents=[types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"), prompt],
   config=types.GenerateContentConfig(response_mime_type="application/json")
)

Real-time In-Database Embeddings

One of the coolest features of AlloyDB is the ability to generate embeddings without leaving the SQL context. Instead of calling an embedding model in Python and sending the vector back to the DB, I do it all in one INSERT statement using the embedding() function:

INSERT INTO items (owner_id, provider_name, provider_phone, title, bio, category, image_url, status, item_vector)
VALUES (
   :owner, :name, :phone, :title, :bio, :cat, :url, 'available',
   embedding('text-embedding-005', :title || ' ' || :bio)::vector
)

This ensures that every item is "searchable" by its meaning the second it's posted. And note that this is the part that covers the "listing the product" feature of the Neighbor Loop app.

Advanced Vector Search and Smart Filtering with Gemini 3.0

Standard keyword search is limited. If you search for "something to fix my chair," a traditional database might return nothing if the word "chair" isn't in a title. Neighbor Loop solves this with AlloyDB AI's advanced vector search.

By using the pgvector extension and AlloyDB's optimized storage, we can perform extremely fast similarity searches. But the real "magic" happens when we combine vector proximity with LLM-based logic.

AlloyDB AI allows us to call models like Gemini directly within our SQL queries. This means we can perform a Semantic Discovery that includes a logic-based "sanity check" using the ai.if() function:

SELECT item_id, title, bio, category, image_url,
      1 - (item_vector <=> embedding('text-embedding-005', :query)::vector) as score
FROM items
WHERE status = 'available'
 AND item_vector IS NOT NULL
 AND ai.if(
       prompt => 'Does this text: "' || bio ||'" match the user request: "' ||  :query || '", at least 60%? "',
       model_id => 'gemini-3-flash-preview'
     ) 
ORDER BY score DESC
LIMIT 5

This query represents a major architectural shift: we are moving logic to the data. Instead of pulling thousands of results into application code to filter them, Gemini 3 Flash performs a "vibe check" inside the database engine. This reduces latency, lowers egress costs, and ensures that the results aren't just mathematically similar, but contextually relevant.

The "Swipe to Match" Loop

The UI is a classic deck of cards.

Swipe Left: Discard.

Swipe Right: It's a match!

When you swipe right, the backend records the interaction in our swipes table and marks the item as matched. The frontend instantly triggers a modal showing the provider's contact info so you can arrange the pickup.

[8. Let's deploy it to Cloud Run](https://codelabs.developers.google.com/gemini-3-flash-on-alloydb-sustainability-app?hl=en)

- Deploy it on Cloud Run by running the following command from the Cloud Shell Terminal where the project is cloned and **make sure you are inside the project's root folder**.

Run this in your Cloud Shell terminal:

gcloud beta run deploy neighbor-loop \
   --source . \
   --region=us-central1 \
   --network=<<YOUR_NETWORK_NAME>> \
   --subnet=<<YOUR_SUBNET_NAME>> \
   --allow-unauthenticated \
   --vpc-egress=all-traffic \
   --set-env-vars GEMINI_API_KEY=<<YOUR_GEMINI_API_KEY>>,DATABASE_URL=postgresql+pg8000://postgres:<<YOUR_PASSWORD>>@<<PRIVATE_IP_HOST>>:<<PORT>>/postgres,GCS_BUCKET_NAME=<<YOUR_GCS_BUCKET>>

Replace the values for placeholders <<YOUR_GEMINI_API_KEY>>, <<YOUR_PASSWORD>, <<PRIVATE_IP_HOST>>, <<PORT>> and <<YOUR_GCS_BUCKET>>

**Important:**

- **Your HOST_IP should be the private IP address of your ****AlloyDB**** instance in this case when you're deploying to Cloud Run. You can find this in ****AlloyDB**** instance's "Connectivity Configuration" section. Click that "View Connectivity Configuration" link and from the "Connectivity" page that opens up, copy the instance's host and port from the "Private IP Address" entry.**

- **Since we are using** ﻿**--vpc-egress=all-traffic**﻿**, Cloud Run will talk to the database securely over your internal Google network.**

- **At this point, you can safely remove 0.0.0.0/0 from your Authorized External Networks list of IP addresses.**

- **If you have followed the 2 steps from the ****codelab** **mentioned initially for easy ****set up**** of ****AlloyDB**** Cluster and Instance, you would have the details of network, subnet, in those steps.**

Once the command finishes, it will spit out a Service URL. Copy it.

- Grant the **AlloyDB**** Client** role to the Cloud Run service account.This allows your serverless application to securely tunnel into the database.

Run this in your Cloud Shell terminal:

# 1. Get your Project ID and Project Number
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# 2. Grant the AlloyDB Client role
gcloud projects add-iam-policy-binding $PROJECT_ID \
--member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
--role="roles/alloydb.client"

Now use the service URL (Cloud Run endpoint you copied earlier) and test the app. Upload a photo of that old power tool, and let Gemini do the rest!

Gotchas & Troubleshooting

| **The "Revision Failed" Loop** | If the deployment finishes but the URL gives a 500 Internal Server Error, check the logs! This is usually caused by a **missing Environment Variable** (like a typo in your DATABASE_URL) or the Cloud Run Service Account lacking permissions to read from your GCS bucket. |
| --- | --- |
| **The IAM "Shadow" Role** | Even if *you* have permission to deploy, the **Cloud Run Service Account** (usually [project-number]-compute@developer.gserviceaccount.com) needs the AlloyDB Client role to actually establish a connection to the database. |

[9. High Level Troubleshooting](https://codelabs.developers.google.com/gemini-3-flash-on-alloydb-sustainability-app?hl=en)

[10. Demo](https://codelabs.developers.google.com/gemini-3-flash-on-alloydb-sustainability-app?hl=en)

You should be able to use your end point for tests.

But for demo purposes for a few days, you can play with this:

[Demo App](https://bit.ly/neighbor-loop)

[11. Clean up](https://codelabs.developers.google.com/gemini-3-flash-on-alloydb-sustainability-app?hl=en)

Once this lab is done, do not forget to delete alloyDB cluster and instance.

**Go to **[**https://console.cloud.google.com/alloydb/clusters**](https://console.cloud.google.com/alloydb/clusters)**. Select the cluster you want to delete by clicking on the vertical ellipsis next to it and click DELETE.**

It should clean up the cluster along with its instance(s).

---

## Codelab 3: Configure Vector Search in AlloyDB

Configure Vector Search in AlloyDB

experimentLabschedule20 minutesuniversal_currency_alt1 Creditshow_chartIntroductory

infoThis lab may incorporate AI tools to support your learning.

**GSP1286**

**Overview**

Imagine your applications searching your AlloyDB database and quickly identifying related data, even if the provided search phrase is not actually included in the stored text! You can now leverage the power of [Vertex AI text embeddings](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings) to conduct Vector Search within AlloyDB.

[AlloyDB](https://cloud.google.com/alloydb/docs/overview) is a fully managed, PostgreSQL-compatible database service that's designed for your most demanding workloads, including hybrid transactional and analytical processing. In addition, you can leverage [AlloyDB AI](https://docs.cloud.google.com/alloydb/docs/ai/what-is-alloydb-ai) functionality to accomplish tasks such as building [Generative AI chat bots](https://cloud.google.com/alloydb/docs/ai/alloydb-ai-use-cases) and surfacing data in your AlloyDB database based on relevance to your specific search terms.

[Vector Search](https://docs.cloud.google.com/vertex-ai/docs/vector-search/overview) is a methodology that finds similar items based on their semantic meaning (rather than exact keyword matching) and can be applied to many types of data including audio, images, videos, and text. For text, Vector Search enables you to find similar text items without needing their contents to match the exact text or phrase used in the search.

This lab introduces the essential steps for configuring Vector Search in AlloyDB. You begin by generating and storing [text embeddings](https://cloud.google.com/vertex-ai/docs/vector-search/overview)—vectors that numerically represent the semantic meaning of text—and then utilize these embeddings to conduct rapid similarity searches.

The lab uses patent data to demonstrate how AlloyDB's Vector Search can efficiently search lengthy, technical abstracts. This capability is vital because traditional keyword matching on such complex text often makes it difficult to quickly grasp the core idea and can produce inaccurate results.

What you'll learn

In this lab, you learn how to:

- Configure an AlloyDB database to support Vector Search.

- Create a table and load data in AlloyDB.

- Generate and store text embeddings in AlloyDB.

- Perform Vector Search in AlloyDB using text embeddings.

**Setup and requirements**

Before you click the Start Lab button

Read these instructions. Labs are timed and you cannot pause them. The timer, which starts when you click **Start Lab**, shows how long Google Cloud resources are made available to you.

This hands-on lab lets you do the lab activities in a real cloud environment, not in a simulation or demo environment. It does so by giving you new, temporary credentials you use to sign in and access Google Cloud for the duration of the lab.

To complete this lab, you need:

- Access to a standard internet browser (Chrome browser recommended).

**Note:** Use an Incognito (recommended) or private browser window to run this lab. This prevents conflicts between your personal account and the student account, which may cause extra charges incurred to your personal account.

- Time to complete the lab—remember, once you start, you cannot pause a lab.

**Note:** Use only the student account for this lab. If you use a different Google Cloud account, you may incur charges to that account.

How to start your lab and sign in to the Google Cloud console

- Click the **Start Lab** button. If you need to pay for the lab, a dialog opens for you to select your payment method. On the left is the Lab Details pane with the following:

- The Open Google Cloud console button

- Time remaining

- The temporary credentials that you must use for this lab

- Other information, if needed, to step through this lab

- Click **Open Google Cloud console** (or right-click and select **Open Link in Incognito Window** if you are running the Chrome browser).

The lab spins up resources, and then opens another tab that shows the Sign in page.

***Tip:*** Arrange the tabs in separate windows, side-by-side.

**Note: **If you see the **Choose an account** dialog, click **Use Another Account**.

- If necessary, copy the **Username** below and paste it into the **Sign in** dialog.

"Username"

Copied!

You can also find the Username in the Lab Details pane.

- Click **Next**.

- Copy the **Password** below and paste it into the **Welcome** dialog.

"Password"

Copied!

You can also find the Password in the Lab Details pane.

- Click **Next**.

**Important: **You must use the credentials the lab provides you. Do not use your Google Cloud account credentials.**Note: **Using your own Google Cloud account for this lab may incur extra charges.

- Click through the subsequent pages:

- Accept the terms and conditions.

- Do not add recovery options or two-factor authentication (because this is a temporary account).

- Do not sign up for free trials.

After a few moments, the Google Cloud console opens in this tab.

**Note:** To access Google Cloud products and services, click the **Navigation menu** or type the service or product name in the **Search** field. 

**Task 1. Configure an AlloyDB database to support Vector Search**

To simplify the process of building AI applications, AlloyDB provides a number of extensions. This lab uses the following two vector extensions:

- google_ml_integration: Provides AI functions for generating embeddings, semantic ranking, and implementing AI-based filters, joins and text generation/summarization. This lab automatically enabled this extension.

- vector: Supports storing generated embeddings in a vector column. In this section, you enable this extension.

For more information about extensions, refer to [Build generative AI applications using AlloyDB AI](https://docs.cloud.google.com/alloydb/docs/ai)

This lab automatically created the AlloyDB cluster named **patent-cluster** and an instance named **patent-instance**.

In this task, you configure the default AlloyDB database, named **postgres**, to support Vector Search capabilities. This involves enabling key extensions and setting the necessary permissions for generating, storing, and querying text embeddings.

Enable extensions and permissions in AlloyDB for Vector Search

First, you connect to the AlloyDB database using [AlloyDB Studio](https://cloud.google.com/alloydb/docs/manage-data-using-studio) to enable the vector extension and access to Vertex AI endpoints.

- In the Google Cloud console title bar, type **AlloyDB for PostgreSQL** in the **Search** field, and then click **AlloyDB for PostgreSQL** from the search results.

- In the left pane, click **Clusters** to examine the cluster's details.

It may take a few minutes for both the cluster and instance to be fully provisioned.

Wait for a **Status** of **Ready** (green checkmark) for both **patent-cluster** and **patent-instance** before you proceed to the next step.

- Click the **patent-instance** instance.

- In the left pane, click **AlloyDB Studio**.

- Provide the following details to sign in, and click **Authenticate**.

| **Property** | **Value** |
| --- | --- |
| **Database** | **postgres** |
| **User** | **postgres** |
| **Password** | **changeme** |

- In the right pane, click **Untitled query** to open a query window.

- To enable the vector extension, copy and paste the following query in the query window, and click **Run**.

CREATE EXTENSION vector;

Copied!

When the query has executed successfully, you see the message: *Statement executed successfully*.

- In the query editor window, click **Clear** to remove the previous query.

- To grant the default database user named **postgres** the permission to execute the embedding function, copy and paste the following query:

GRANT EXECUTE ON FUNCTION embedding TO postgres;

Copied!

When the query has executed successfully, you see a message that says *Statement executed successfully*.

Click **Check my progress** to verify the objective.

Enable extensions and permissions in AlloyDB for Vector Search

Grant Vertex AI User role to the AlloyDB service account

Now that the database has the appropriate extensions and permissions, use [Identity and Access Management (IAM)](https://cloud.google.com/security/products/iam) to grant the appropriate Vertex AI role to the AlloyDB service account, which is necessary for accessing Vertex AI resources.

- In the Google Cloud console, on the **Navigation menu** (), select **IAM ****&**** Admin** > **IAM**.

- Click **Grant access**.

- For **New principals**, enter the AlloyDB service account ID:

service-Project_Number@gcp-sa-alloydb.iam.gserviceaccount.com

Copied!

- For **Select a role**, select **Vertex AI** > **Vertex AI User**.

- Click **Save**.

Click **Check my progress** to verify the objective.

Grant Vertex AI User role to AlloyDB service account

**Task 2. Create a new table and load patents data**

The [Google Patents Public Data](https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data) is a large dataset of patent publications that provides the full abstract of each patent. The often lengthy and complex text in these abstracts make this database a great candidate for Vector Search.

In this task, you create a new table containing the various columns in the patent source data plus an extra column for the vector embeddings for the abstract text (to be generated in the next task). You then load a sample of the full patent data into the table in AlloyDB.

- Return to AlloyDB Studio: In the Google Cloud console title bar, type **AlloyDB for PostgreSQL** in the **Search** field, and then click **AlloyDB for PostgreSQL** from the search results.

- Click the **patent-instance** instance.

- In the left pane, click **AlloyDB Studio**.

- In the query editor window, if needed, click **Clear**.

- To create a new table named **patents_data**, copy and paste the following query in the query window, and click **Run**.

CREATE TABLE patents_data (id VARCHAR(25), type VARCHAR(25), number VARCHAR(20), country VARCHAR(2), date VARCHAR(20), abstract VARCHAR(300000), title VARCHAR(100000), kind VARCHAR(5), num_claims BIGINT, filename VARCHAR(100), withdrawn BIGINT, abstract_embeddings vector(3072));

Copied!

The last column of the table named **abstract_embeddings** is of the type vector, which supports storage for the vector values that you create in the next task.

When the query has executed successfully, you see the message: *Statement executed successfully*.

- In the AlloyDB Studio query editor, click **Clear**.

- To load data into the table, copy and paste the following query in the query window, and click **Run**.

**Note:** Although this is only a sample of the full patents dataset, the sample includes all information for each of the 50 patents loaded into the table.

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10326103','utility','10326103','US','6/18/2019','A display device includes a first substrate having a display area and a non-display area around the display area, a seal pattern in the non-display area and offset from the display area, and one or more buffer patterns between the seal pattern and the display area and having a viscosity of 5000 cps to 50000 cps.','Display device having buffer patterns','B2',15,'ipg190618.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10326507','utility','10326507','US','6/18/2019','A network device receives, from a network management system (NMS), a first traffic distribution associated with the FD-MIMO antenna site, and receives a first service reliability requirement associated with the FD-MIMO antenna site. The network device determines, based on physical constraints, a maximum number of a plurality of antenna base blocks that can be placed at a full-dimension multiple input multiple output (FD-MIMO) antenna site, wherein each of the plurality of antenna base blocks includes a plurality of antennas. The network device further determines a first number of antennas to switch into the FD-MIMO antenna site based on the determined maximum number of the plurality of antenna base blocks, the first traffic distribution, and the first service reliability requirement; and causes the first number of antennas to be switched into the FD-MIMO antenna site.','System and method for a dynamically active FD-MIMO antenna array adjustment system','B2',20,'ipg190618.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10328303','utility','10328303','US','6/25/2019','An exercise treadmill is disclosed. The treadmill can be constructed with no obstructing front rails, with one or more side rails, and/or with a structural flat or ramped surface at the front allowing the user to exercise with unconstrained motion. The treadmill can further include one or more accommodations to help the user stay safe, remain longitudinally centered, and/or adjust speed with controls built into the treadmill, or automatically based on body position relative to sensors built into the side rails. The treadmill belt may be motor driven, or be user driven and dynamically moderated by resistance. The treadmill configuration can be utilized to provide a virtualized exercise experience for the user.','Exercise treadmill','B2',27,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10328431','utility','10328431','US','6/25/2019','A storage system for storing samples, such as frozen biological samples in RFID-tagged vials. The storage system has (i) a storage device having a device antenna and (ii) a plurality of storage components adapted to be stored within the storage device, each storage component having a component circuit. Each storage component is configured to store one or more samples. The storage device is configured to (i) transmit electrical power and downlink data signals wirelessly to each storage component via the device antenna and the corresponding component circuit and to (ii) receive uplink data signals from each storage component wirelessly via the corresponding component circuit and the device antenna such that a control system located outside of the dewar can identify any specified storage component stored within the storage device.','Storage devices for RFID-tracked biological and other samples','B2',19,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10328505','utility','10328505','US','6/25/2019','A circular saw includes a worktable, a sliding unit including a mounting base mounted on the worktable and providing an accommodation slot and two sliding shafts axially slidably inserted through the mounting base at two opposite sides of the accommodation slot in a parallel manner, and a cutting unit including a saw arm pivotally connected between the two sliding shafts and providing an accommodation portion and a saw blade pivotally mounted at the saw arm. Thus, when the saw arm is in an upper limit position, the accommodation of the saw arm is partially disposed outside the accommodation slot. When the saw arm is in a lower limit position, the accommodation portion is received in the accommodation slot. Subject to the design described above, the circular saw achieves the effects of reduced overall dimension, low vibration and high cutting accuracy.','Circular saw','B2',3,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10328822','utility','10328822','US','6/25/2019','An improved system to raise and lower a seat by a simplified substantially parallelogram or non-parallelogram motion. By replacing two of the links of a parallelogram seat lift system with an arc, or a straight link as a mechanically defined path for a pivot to follow, space and material can be saved to fit an adjustable seat on an ATV or any type of support system. The system can be useful on many varieties of vehicles and other adjustable supports.','Adjustable seat and support system','B2',9,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10329100','utility','10329100','US','6/25/2019','A tie plate straightener includes a plurality of rollers having varying cross-section and differing elevations. The tie plate straightener includes directional wheels between the rollers and disposed in alignment with the lower elevations of the rollers. The straightener receives tie plates at an input and rotates the tie plates when the tie plate engages the directional wheels. The tie plate is thereby oriented and/or positioned so that the tie plate is supported above the directional wheels.','Plate straightener','B1',19,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10329436','utility','10329436','US','6/25/2019','A self-healing polymer is described herein, including a first carbon nanotube filled with at least a first healing agent, wherein the first carbon nanotube has first and second ends, wherein a first end cap is closed on the first end of the first carbon nanotube and a second end cap is closed on the second end of the first carbon nanotube, and a second carbon nanotube filled with at least a second healing agent, wherein the second carbon nanotube has first and second ends, wherein a first end cap is closed on the first end of the second carbon nanotube and a second end cap is closed on the second end of the second carbon nanotube.','Self-healing polymer compositions','B2',18,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10330945','utility','10330945','US','6/25/2019','There is provided a medical image display apparatus including: a display control section that performs control such that a left-eye image and a right-eye image that form a medical image are displayed in a time division manner on a predetermined display section; and a communication section that transmits a synchronization signal in accordance with display timings of the left-eye image and the right-eye image on the display section to shutter glasses that include a left-eye shutter and a right-eye shutter, and receives a response to the synchronization signal from the shutter glasses. The display control section performs the control such that only any one of the left-eye image and the right-eye image is displayed on the display section in accordance with a reception status of the response.','Medical image display apparatus, medical information processing system, and medical image display control method','B2',10,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10331073','utility','10331073','US','6/25/2019','In an example implementation, a method of cleaning a silicon photoconductor includes contacting the silicon photoconductor with a base-peroxide solution, rinsing the silicon photoconductor with a liquid, and heating the silicon photoconductor to evaporate the liquid.','Cleaning a silicon photoconductor','B2',18,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10331564','utility','10331564','US','6/25/2019','Technologies for secure I/O with MIPI camera devices include a computing device having a camera controller coupled to a camera and a channel identifier filter. The channel identifier filter detects DMA transactions issued by the camera controller and related to the camera. The channel identifier filter determines whether a DMA transaction includes a secure channel identifier or a non-secure channel identifier. If the DMA transaction includes the non-secure channel identifier, the channel identifier filter allows the DMA transaction. If the DMA transaction includes the secure channel identifier, the channel identifier filter determines whether the DMA transaction is targeted to a memory address in a protected memory range associated with the secure channel identifier. If so, the channel identifier filter allows the DMA transaction. If not, the channel identifier filter blocks the DMA transaction. Other embodiments are described and claimed.','Technologies for secure I/O with MIPI camera device','B2',25,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10331881','utility','10331881','US','6/25/2019','Techniques are described herein for loading a user-mode component of a security agent based on an asynchronous procedure call (APC) built by a kernel-mode component of the security agent. The APC is executed while a process loads, causing the process to load the user-mode component. The user-mode component then identifies slack space of the process, stores instructions in the slack space, and hooks function(s) of the process, including modifying instruction(s) of the function(s) to call the instructions stored in the slack space. When those modified instruction(s) call the stored instructions, the stored instructions invoke the user-mode component, which receives data from the hooked function(s). Also, the security agent may bypass a control-flow protection mechanism of the operating system by setting a pointer of the control-flow protection mechanism to point to an alternate verification function.','User-mode component injection techniques','B2',20,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10332201','utility','10332201','US','6/25/2019','A computer-assisted method of presenting a plurality of financial accounts as a unitary financial account. The method includes displaying, on a graphical display, a graphical representation of a first financial account and displaying, on the graphical display, a graphical representation of a second financial account, wherein the graphical representation of the first financial account and the graphical representation of the second financial account are displayed as a unitary graphical representation that conveys to a user that the first financial account and the second financial account are a partitioned unitary financial account. The method also includes enabling the user to transfer monetary funds between the first financial account and the second financial account by manipulation of the unitary graphical representation.','Bundled financial accounts','B1',12,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10333086','utility','10333086','US','6/25/2019','A flexible display panel fabrication method and a flexible display panel where the method first subjects a photoresist layer to patterning to form a plurality of mutually spaced photoresist zones, a through hole being formed between every two adjacent ones of the photoresist zones; and then, subjecting the flexible backing plate to cavity formation with the photoresist zones as a mask so as to form a plurality of mutually parallel backing cavities respectively at locations corresponding to the through holes; and then, depositing a metal film and subsequently removing the photoresist zones and portions of the metal layer located thereon to form a plurality of metal patterns embedded in the plurality of mutually parallel backing cavities, each of the metal patterns including a scan line and a plurality of gate electrodes; and then, forming a plurality of TFTs arranged in an array and OLED light emissive elements.','Flexible display panel fabrication method and flexible display panel','B2',13,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10333126','utility','10333126','US','6/25/2019','The present invention relates to a composite separation membrane for a lithium secondary battery having excellent lifetime and safety improvement effects, and a preparation method therefor and, more specifically, to a composite separation membrane for a lithium secondary battery, including: a porous base layer; a heat resistant layer formed on one surface or both surfaces of the porous base layer; and a fusion layer formed on the outermost layer. Inorganic particles in the heat resistant layer are connected and fixed by a binder polymer, and the fusion layer is prepared by comprising amorphous polymer particles having a glass transition temperature of 30 to 90Â° C. and a difference between a fusion temperature and the glass transition temperature of 60Â° C. or lower.','Fusion type composite separation membrane for lithium secondary battery, and preparation method therefor','B2',11,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10333949','utility','10333949','US','6/25/2019','The present disclosure relates to systems and methods for blocking an infection vector. In some embodiments, a method may include detecting, at a first device, a synchronization event with a second device, the first device and the second device operating with a proprietary mobile operating system. In some examples, the method may include recognizing, by the first device, that the first device is attempting to send a data package to the second device, and identifying the data package as malware. The method may further include blocking the data package from being received at the second device based at least in part on the identifying.','Proactive protection of mobile operating system malware via blocking of infection vector','B1',16,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10334023','utility','10334023','US','6/25/2019','The present invention discloses a content distribution method, system and a server. In one embodiment, the method includes: receiving a content distribution request form a client; obtaining all receiving ends designated by the content distribution request, and marking at least a portion of the receiving ends with a first status code; judging whether all the at least a portion of the receiving ends complete the distribution task, if not, controlling an internal distribution process until all the at least a portion of the receiving ends complete the distribution task.','Content distribution method, system and server','B2',18,'ipg190625.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10334962','utility','10334962','US','7/2/2019','A portable, stable and rigid baby changing station which can be easily collapsed for storage or expanded for use and which can be safely and securely worn by a user, to form a firm bed for changing a baby when no other clean or useable surfaces are available.','Wearable portable baby changing table','B2',15,'ipg190702.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10335619','utility','10335619','US','7/2/2019','A multifunction NFPA escape and ladder belt having multiple functions for firefighter and rescue worker work. The belt includes a front buckle and right and left side buckles, straps coupling the left and right side buckles to the front buckle and to one another. At least one of said straps includes a stitched loop portion formed with a stitching pattern configured to fail, and for the loop portion to unfold, when the side straps are under a sufficient tension load exceeding the breaking strength of the stitching pattern; that failure will occur before a structural failure in any other element or component of the belt.','Firefighter multifunction ladder and escape belt','B2',14,'ipg190702.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10336444','utility','10336444','US','7/2/2019','A rotor includes a blade retention cuff configured to receive a rotor blade; a yoke coupled to the blade retention cuff; and a rigid propeller shaped hub configured to enclose at least a portion of the blade retention cuff and at least a portion of the yoke.','Composite stiffened rigid propeller shaped main rotor hub','B2',18,'ipg190702.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10337814','utility','10337814','US','7/2/2019','A dearmer positioning system has two assemblies, each of which circumscribes a dearmers barrel. Each of the two assemblies includes two half rings and a one-piece outer ring. The two half rings are joined to one another to define a full ring having a first central opening defining a first diameter. The full ring has a periphery defining a second diameter. The one-piece outer ring has a second central opening defining a third diameter, and a periphery defining a fourth diameter. The third diameter is greater than the second diameter such that the full ring slidingly fits in the central opening of the outer ring. Threaded fasteners engage the outer ring and extend radially through the outer ring and into its central opening to engage the periphery of the full ring.','Dearmer positioning system','B1',18,'ipg190702.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10338067','utility','10338067','US','7/2/2019','Method and compositions using transition metal salts and/or ammonium chloride to liberate toxins and other molecules from cyanobacteria, useful for assaying for total cyanobacterial toxins in lakes, reservoirs and other waters.','Rapid analysis for cyanobacterial toxins','B1',11,'ipg190702.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10338681','utility','10338681','US','7/2/2019','One illustrative system disclosed herein includes a processor configured to determine a haptic effect, wherein the haptic effect includes a static ESF effect or a confirmation ESF effect; and transmit a haptic signal associated with the haptic effect. The illustrative system also includes an ESF controller in communication with the processor, the ESF controller configured to receive the haptic signal, determine an ESF signal based at least in part on the haptic signal, and transmit the ESF signal. The illustrative system further includes an ESF device in communication with the ESF controller, the ESF device including an ESF cell and configured to receive the ESF signal and output the haptic effect.','Systems and methods for multi-output electrostatic haptic effects','B2',20,'ipg190702.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10338956','utility','10338956','US','7/2/2019','An application profiling system, initiating profiling a software application; including: apparatus to receive user input information of a software application profiling target and execution requirements, to store profiler specifications; to determine which profiler satisfies the execution requirements, based on the specifications, and to generate needed profiling tasks, each task specifying an application profiler; to select hardware resources the tasks; and to initiate execution of the tasks.','Application profiling job management system, program, and method','B2',15,'ipg190702.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10339572','utility','10339572','US','7/2/2019','A seemingly infinite and continuous stream of online content can be tracked by a movement tracker that can track an amount of movement of a stream of content. For example, such a movement tracker can track the amount of movement per session of a client-side application, such as per session of a web browser. In an example, the tracking of the movement can occur by tracking a measurable parameter of the stream that indicates the amount of movement, such as scroll distance. The movement tracker may also be configured to determine user interaction data according to the tracked amount of movement.','Tracking user interaction with a stream of content','B2',20,'ipg190702.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10339617','utility','10339617','US','7/2/2019','An order management system that employs profile locking is provided for managing clinical orders in patient profiles. The system allows users to initiate lockable order actions (e.g., order actions requiring a profile lock for conflict checking) in a profile locked by another user. When a user attempts to initiate a lockable order action, the system provides a notification to the user indicating that the patient profile is locked by another user. The user may elect to continue initiating the lockable order action. When the profile becomes available, the system provides a notification to the user, who may then obtain the profile lock and process the lockable order action, including having the system perform conflict checking. The system may also provide for the initiation of an instant messaging session between the user attempting to enter a lockable order action in a locked profile and another user who has the profile lock.','Order profile safeguarding mechanism','B2',20,'ipg190702.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10340545','utility','10340545','US','7/2/2019','A method and apparatus is provided for harvesting electricity from a biofilm retained in a zero chamber, no interphase container, the biofilm having a portion supporting aerobic microbial activity and a second portion supporting anaerobic microbial activity, wherein the first and the second portion are in direct physical contact. A power harvester is electrically connected, directly or indirectly, to the second portion of the biofilm.','Method and apparatus for converting chemical energy stored in wastewater into electrical energy','B2',29,'ipg190702.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10341086','utility','10341086','US','7/2/2019','A method is performed by a server for searching for information contained in encrypted data without revealing the information to the server. The server receives from a client: an encrypted matrix containing the information to be searched for in files and linking the information to the files; for each of the files, a merged secret key; and an encrypted vector having a length corresponding to a number of the information. The encrypted data is evaluated by performing a multiplication of the matrix with entries in the vector using a multikey homomorphic encryption scheme. For each of the files, a value of the multiplication of the matrix is decrypted using the corresponding merged secret key so as to determine which of the files contains the information. The files containing the information are sent to the client.','Method and system for providing encrypted data for searching of information therein and a method and system for searching of information on encrypted data','B2',12,'ipg190702.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10341990','utility','10341990','US','7/2/2019','An electronic apparatus and a controlling method thereof are provided. The electronic apparatus includes: a first communication module configured to communicate in a first communication method, and a second communication module configured to communicate in a second communication method. The first communication module is further configured to change a transmission output level of the first communication module from a first transmission output level to a second transmission output level in response to the second communication module receiving data, and change the transmission output level from the second transmission output level to the first transmission output level in response to the second communication module completing the reception of the data.','Electronic apparatus and controlling method thereof','B2',17,'ipg190702.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10342895','utility','10342895','US','7/9/2019','A pulverulent semisynthetic material, derived from a natural marine biomaterial, namely the aragonitic inner layer of the shell of bivalve molluscs selected from the group including Pinctadines, notably Pinctada maxima, margaritifera, and Tridacnes, notably Tridacnagigas, maxima, derasa, tevaroa, squamosa, crocea, Hippopushippopus, Hippopusporcelanus, in pulverulent form, with addition of insoluble and soluble biopolymers and calcium carbonate transformed by carbonation; it also relates to the method of preparation thereof and to the uses thereof.','Pulverulent semisynthetic material obtained by modifying the composition of a natural marine biomaterial, method of manufacture thereof, and applications thereof','B2',7,'ipg190709.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10343251','utility','10343251','US','7/9/2019','In a cam grinding method, a common surface of a first cam and a second cam is acquired in a common surface setting step. In a first common surface grinding step performed after a first cam grinding step, traverse movement of a grinding wheel is performed such that the grinding wheel is aligned with an area from the first cam to the second cam while the first cam and the second cam are rotated, and the common surface is ground. In a second common surface grinding step performed after a second cam grinding step, traverse movement of the grinding wheel is performed such that the grinding wheel is aligned with an area from the second cam to the first cam while the first cam and the second cam are rotated, and the common surface is ground.','Cam grinding machine and cam grinding method','B2',6,'ipg190709.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10343997','utility','10343997','US','7/9/2019','An ursolic acid derivative can have the following structural formula: The ursolic acid derivative exhibits potent selective calcium channel blocker activities and may be used to treat a disease or condition for which calcium channel regulation is useful.','Ursolic acid derivatives','B1',11,'ipg190709.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10344433','utility','10344433','US','7/9/2019','A ground stabilisation system is used for stabilising a subgrade region which includes a peat layer under a railway having rails supported across rail ties on a ballast layer over the subgrade region. The system uses a plurality of drain members submerged in an upright orientation within the peat layer of the subgrade region in which each drain member has a hollow interior and a plurality of openings therein which allow communication of fluid from the peat layer surrounding the drain member into the hollow interior of the drain member so as to be arranged to reduce fluid pressure in the peat layer when the peat layer undergoes dynamic loading from a passing train. Each drain member is a semi-rigid pipe having an axial stiffness greater than a dynamic stiffness of the peat layer to reduce loading on the peat layer under dynamic loading from a passing train.','Subgrade peat stabilisation system for railway','B2',16,'ipg190709.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10344992','utility','10344992','US','7/9/2019','Embodiments of the invention provide a lighting and ventilating system including a main housing. The main housing can include an inlet through which air can be received within the main housing and an outlet through which the air can exit the main housing. A fan wheel can be supported in the main housing and it can be operable to generate a flow of air. A grille can be coupled to the main housing and the grille can comprise at least one aperture. The system can include a plate coupled to the grille and the plate can include a recess. Also, a set of illumination devices can be at least partially disposed within the recess.','Lighting and ventilating system and method','B2',34,'ipg190709.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10345589','utility','10345589','US','7/9/2019','An apparatus includes a holographic film having one or more reflective holograms recorded therein. One or more light sources positioned to direct light toward a corresponding one of the one or more holograms, and a dynamic mask positioned between the one or more light sources and the holographic film to spatially modulate light traveling between the one or more light sources and the one or more reflective holograms but not spatially modulate ambient light traveling through the hologram.','Compact near-eye hologram display','B1',20,'ipg190709.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10346746','utility','10346746','US','7/9/2019','A method and apparatus for generating a training model based on feedback are provided. The method for generating a training model based on feedback, includes calculating an eigenvector of a sample among a plurality of samples; obtaining scores granted by a user for one or more of the plurality of samples in a round, obtaining scores granted by the user for a first number of samples; obtaining scores granted by the user for a second number of samples in response to detecting, based on the eigenvector, an inconsistency between the scores granted by the user for the first number of samples; and generating a training model based on the scores granted by the user for the first and second numbers of samples. A corresponding apparatus is also provided.','Generating a training model based on feedback','B2',8,'ipg190709.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10347147','utility','10347147','US','7/9/2019','A system, a method, and a computer program product for managing answer feasibility in a Question and Answering (QA) system. A set of candidate situations is established. The set of candidate situations corresponds to a first set of answers. A QA system establishes the set of candidate situations by analyzing a corpus. The first set of answers will answer a question. The QA system identifies a subset of the set of candidate situations. The subset of candidate situations corresponds to a portion of contextual data. The portion of contextual data is from a set of contextual data. The set of contextual data relates to the question. The question-answering system determines a set of answer feasibility factors. The set of answer feasibility factors is determined using the subset of candidate situations. The set of answer feasibility factors indicates the feasibility of the answers in the first set of answers.','Managing answer feasibility','B2',14,'ipg190709.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10347243','utility','10347243','US','7/9/2019','Disclosed herein is a method for analyzing an utterance meaning. The method includes collecting a voice signal of an utterer; converting the collected voice signal into information in a text form, extracting a keyword of the text information from the text information, and deriving at least one utterance topic on the basis of the extracted keywords of the text information.','Apparatus and method for analyzing utterance meaning','B2',26,'ipg190709.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10347623','utility','10347623','US','7/9/2019','A switch includes an input terminal and an output terminal. The switch also includes a first stack having transistors coupled in series, and a second stack having transistors coupled in series. The first stack and the second stack are connected in parallel with one another.','Switch having first and second switching elements connected in parallel with one another','B2',16,'ipg190709.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10347660','utility','10347660','US','7/9/2019','The present disclosure discloses an array substrate, the array substrate comprises a substrate as well as a thin film transistor and a pixel electrode formed on the substrate, wherein the top of the thin film transistor is formed a floating gate electrode, at least portion of the floating gate electrode and the pixel electrode are made of the same material. The present disclosure also discloses a manufacturing method of an array substrate. Through this way, the present disclosure simultaneously forms a floating gate electrode in the manufacturing process of the pixel electrode, the pixel electrode and the floating gate electrode is formed by a mask, there is no need to add a mask, thus achieving the manufacture of the dual gate thin film transistor and the array substrate, briefing the process, reducing the production costs.','Array substrate and manufacturing method thereof','B2',11,'ipg190709.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10348905','utility','10348905','US','7/9/2019','A computer-based system and method for responding to customer calls. The method includes automatically determining whether at least one incoming call meets existing customer criteria and further automatically determining a market segment of the at least one incoming call. The market segment may indicate whether a specific customer prefers: (i) no voice or face-to-face interaction with a representative; (ii) a face-to-face interaction with a representative; and/or (iii) a voice only interaction with a representative. The method further includes automatically routing the at least one incoming call based upon the determined market segment to one of: (1) an automated voice prompt; (2) a gaming system having two-way video capability; or (3) a person-to-person voice call system to facilitate answering incoming calls in a customer-friendly or customer preferred manner.','System and method for responding to customer calls','B1',16,'ipg190709.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10349594','utility','10349594','US','7/16/2019','The present invention relates to a Lactuca sativa seed designated 45-227 RZ. The present invention also relates to a Lactuca sativa plant produced by growing the 45-227 RZ seed. The invention further relates to methods for producing the lettuce cultivar, represented by lettuce variety 45-227 RZ.','Lettuce variety 45-227 RZ','B2',29,'ipg190716.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10350762','utility','10350762','US','7/16/2019','A cleaning robot which performs a predetermined task while autonomously moving includes: a driver which makes the cleaning robot move; an image capturer which detects a movement state indicating whether a different cleaning robot existing in front of the cleaning robot is moving along an obstacle, a direction in which the different cleaning robot exists relative to the cleaning robot, and a distance between the cleaning robot and the different cleaning robot; and a following run controller which controls the driver in order for the cleaning robot to move following the different cleaning robot while keeping a position diagonally behind the different cleaning robot at an opposite side of the different cleaning robot from the obstacle, if the movement state indicates that the different cleaning robot is moving along the obstacle.','Autonomously moving body, movement controlling method, and recording medium storing movement controlling program','B2',14,'ipg190716.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10351196','utility','10351196','US','7/16/2019','A foldable-chair carrier for a bicycle includes a frame that defines a plurality of generally planar, inclined chair-supporting surfaces over the rear wheel of the bicycle. The frame includes a pair of enlarged hooks at the forward, upper portion of the frame, with the hooks being arranged to receive opposite ends of one of the structural tubes of the chair in its folded configuration. The hooks may be sufficiently large to receive two or more of the folded chairs, in a stacked array. The hooks are configured so that even if the bicycle is running on uneven ground, the chairs will be unlikely to be thrown from the frame even in the absence of supplementary tie-downs.','Bicycle attachment for carrying a folding chair','B2',9,'ipg190716.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10351891','utility','10351891','US','7/16/2019','The present invention provides a hydroxyacyl-coenzyme A dehydrogenase gene, an acyl-coenzyme A thiolase gene, genetically engineered strains and a use thereof. The hydroxyacyl-coenzyme A dehydrogenase gene encodes a protein (i) or (ii) as follows: (i) having an amino acid sequence according to SEQ ID NO 2; (ii) derived by substituting, deleting or inserting one or more amino acids in the amino acid sequence defined by (i) and having the same function as that of the protein of (i). The present invention constructs genetically engineered Mycobacterium strains lacking of a hydroxyacyl-coenzyme A dehydrogenase gene or an acyl-coenzyme A thiolase gene, which are used in the preparation of steroidal compounds, such as 1,4-BNA, 4-BNA, 9-OH-BNA, etc. Further, the invention improves the production efficiency and product quality of steroidal drug, improves the utilization of drug precursors, reduces the production costs, and provides the advantages of mild reaction conditions, environmentally friendly, and high economic and social benefits.','Hydroxyacyl-coenzyme A dehydrogenase gene, an acyl-coenzyme A thiolase gene, genetically engineered strains and a use thereof','B2',1,'ipg190716.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10353986','utility','10353986','US','7/16/2019','Some embodiments provide a method for displaying text content on a device. The method receives a set of text content arranged in a single column. The method identifies a separable segment of the text content for display on a device. Based on properties of the text content and the device, the method determines whether the separable segment of the text content meets a set of characteristics for dividing the segment of text content into more than one column for display. When the separable segment of text content meets the set of characteristics, the method displays the segment of text content using more than one column.','Automatically dividing text into multiple columns','B2',25,'ipg190716.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10353994','utility','10353994','US','7/16/2019','Systems, methods, and computer-readable media are disclosed for enhancing an email application to automatically analyze an email thread and generate a compact content summary. The content summary is based on relative content contributions provided by the constituent email messages in the email thread. The content summary may be presented in a special window without disturbing or modifying the email thread or its constituent email messages. The distinctive content summary disclosed herein comprises certain sentences that are automatically gleaned from the email thread, analyzed relative to other sentences, and presented in a chronological sequence so that the user can quickly determine what the email thread is about and/or the current status of the conversation. The content summary is based on email weights, word weights, and intersecting sentence pairs.','Summarization of email on a client computing device based on content contribution to an email thread using classification and word frequency considerations','B2',20,'ipg190716.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10354362','utility','10354362','US','7/16/2019','Methods of detecting an object in an image using a convolutional neural network based architecture that processes multiple feature maps of differing scales from differing convolution layers within a convolutional network to create a regional-proposal bounding box. The bounding box is projected back to the feature maps of the individual convolution layers to obtain a set of regions of interest. These regions of interest are then processed to ultimately create a confidence score representing the confidence that the object detected in the bounding box is the desired object. These processes allow the method to utilize deep features encoded in both the global and the local representation for object regions, allowing the method to robustly deal with challenges in the problem of robust object detection. Software for executing the disclosed methods within an object-detection system is also disclosed.','Methods and software for detecting objects in images using a multiscale fast region-based convolutional neural network','B2',20,'ipg190716.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10355310','utility','10355310','US','7/16/2019','Multi-functional additives containing at least one solid electrolyte interface (SEI) forming group and at least one SEI modifying group are advantageously employed in electrolyte compositions for electrochemical devices. The SEI forming group may comprise an organic carbonate moiety and the SEI modifying group may comprise a heteroatom functional group such as a sulfur containing organic moiety. The electrochemical devices include lithium ion batteries.','Electrolyte compositions for electrochemical devices','B2',20,'ipg190716.xml',0);

insert into patents_data(id, type, number, country, date, abstract, title, kind, num_claims, filename, withdrawn) values('10355956','utility','10355956','US','7/16/2019','Methods, systems, and devices are described for wireless communications. A wireless station includes a transmitter to generate a wideband contiguous waveform in a band. The transmitter transmits the waveform that conforms to spectral masking attributes and spectral flatness attributes. The wireless station, or another device supporting spectrum analysis functions, detects a wideband contiguous waveform and performs spectrum analysis of the waveform. The wireless station includes a resolution bandwidth of 25 KHz and a video bandwidth of 7.5 KHz.','Spectral masking for wideband wireless local area network transmissions','B2',20,'ipg190716.xml',0);

Copied!

When the query has executed successfully, you see the message: *Statement executed successfully*.

Click **Check my progress** to verify the objective.

Create the table and load patents data

**Task 3. Generate and store text embeddings for the patents data**

You configured your database to support Vector Search and loaded some data to search. In this task, you generate the text embeddings for the patent abstracts and add them to the **patents_data** table.

To do this, you run a test query to generate embeddings using the [Vertex AI text embeddings model](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings) named Gemini Embedding model ID.

After a successful test, you run the full query to update the **patents_data** table with the generated embeddings for the abstract text.

Test the query to generate text embeddings

- In the AlloyDB Studio query editor, click **Clear** to remove the previous query.

- To test the query to generate embeddings, copy and paste the following query in the query window, and click **Run**.

SELECT embedding('Gemini Embedding model ID | disablehighlight', 'AlloyDB is a managed, cloud-hosted SQL database service.');

Copied!

**Note:** If you receive an error message postgresql error: Permission denied on the resource, wait a few minutes for the permissions that you assigned in Task 1 to fully propagate, and then run the query again.

The successful output resembles the following:

{0.0021198154,0.0079625305,-0.0069023115,-0.07734479,-0.02922551,0.011961212,0.012080298,0.013767373,0.002040522,0.010687652,-0.0071210554,-0.010858355,0.013857126,-0.01196426,...

Update the **abstract_embeddings** column to store the generated text embeddings

- In the AlloyDB Studio query editor, click **Clear** to remove the previous query.

- To add the text embeddings to the column named **abstract_embeddings**, copy and paste the following query in the query window, and click **Run**.

UPDATE patents_data set abstract_embeddings = embedding('Gemini Embedding model ID | disablehighlight', abstract);

Copied!

When the query has executed successfully, you see the message: *Statement executed successfully*.

Click **Check my progress** to verify the objective.

Generate and store text embeddings for the patents data

**Task 4. Perform a Vector Search using text embeddings in AlloyDB**

After generating and storing the text embeddings for the patent abstracts, your data is ready for your first real time Vector Search!

In this task, you run a query to perform [similarity search](https://cloud.google.com/alloydb/docs/ai/work-with-embeddings) based on the phrase new natural language processing related machine learning model and quickly return the top 10 most relevant patents, despite there not being an exact match for this text in the patent data.

- In the AlloyDB Studio query editor, click **Clear** to remove the previous query.

- To perform Vector Search using the text embeddings, copy and paste the following query in the query window, and click **Run**.

SELECT id, title, abstract FROM patents_data ORDER BY abstract_embeddings <=> embedding('Gemini Embedding model ID | disablehighlight', 'new natural language processing related machine learning model')::vector LIMIT 10;

Copied!

This query uses the values in the **abstract_embeddings** column to find the top 10 database rows that are the most semantically similar to the search phrase new natural language processing related machine learning model.

**Note: **The embedding for the search phrase is generated dynamically in the query. Feel free to explore this query by replacing new natural language processing related machine learning model in the code above with a new search term of your choice.

The output information resembles the following:

| **id** | **title** | **abstract** |
| --- | --- | --- |
| 10347243 | Apparatus and method for analyzing utterance meaning | Disclosed herein is a method for analyzing an utterance meaning. The ... |
| 10346746 | Generating a training model based on feedback | A method and apparatus for generating a training model based on feedback ... |
| 10347147 | Managing answer feasibility | A system, a method, and a computer program product for managing answer feasibility ... |
| 10353994 | Summarization of email on a client computing device based on content ... | Systems, methods, and computer-readable media are disclosed for ... |
| 10354362 | Methods and software for detecting objects in images ... | Methods of detecting an object in an image using a convolutional neural network ... |
| 10353986 | Automatically dividing text into multiple columns | Some embodiments provide a method for displaying text content on a device ... |
| 10348905 | System and method for responding to customer calls | A computer-based system and method for responding to customer calls ... |
| 10350762 | Autonomously moving body, movement controlling method, and recording | A cleaning robot which performs a predetermined task while autonomously moving ... |
| 10338681 | Systems and methods for multi-output electrostatic haptic effects | One illustrative system disclosed herein ... |
| 10338956 | Application profiling job management system, program, and method | An application profiling system, initiating profiling a software application ... |

**Congratulations!**

In this lab, you learned the fundamentals of how to configure an AlloyDB database to support Vector Search, generate and store text embeddings in an AlloyDB table, and perform Vector Search in AlloyDB using the stored text embeddings.

Next steps / Learn more

- Learn more about the key concepts for Vector Search and embeddings in the course titled [Vector Search and Embeddings](https://www.skills.google/course_templates/939).

- Check out the AlloyDB documentation on Vector Search titled [Perform a Vector Search](https://cloud.google.com/alloydb/docs/ai/perform-vector-search) and vector indexes titled [Choose a vector index in AlloyDB AI](https://cloud.google.com/alloydb/docs/ai/choose-index-strategy).

- Review other AI use cases for AlloyDB in the documentation titled [AlloyDB AI use cases](https://cloud.google.com/alloydb/docs/ai/alloydb-ai-use-cases).

- Walk through the full codelab titled [Build a Patent Search App with AlloyDB, Vector Search & Vertex AI](https://codelabs.developers.google.com/patent-search-alloydb-gemini) by Abirami Sukumaran, which was adapted for this lab.

- Complete other hands-on labs on AlloyDB in the course titled [Create and Manage AlloyDB Instances](https://www.skills.google/course_templates/642).