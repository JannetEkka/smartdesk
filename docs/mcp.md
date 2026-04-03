# MCP (Model Context Protocol) — Reference Guide

> Consolidated from Track 2 codelabs: Location Intelligence with BigQuery & Maps MCP, MCP Toolbox for Databases, MCP Tools with ADK Agents

---

## Track 2 Overview

**Track 2 - Connect AI agents to real-world data and tools using Model Context Protocol (MCP)**

**Track focus **

This track focuses on enabling AI agents to securely connect with real-world data, tools, and systems using Model Context Protocol (MCP). Participants learn how to separate AI reasoning from tool execution and build data-aware, production-ready agents. The emphasis is on standardized, scalable AI-to-system integrations.

**Hands-on ****Codelabs**

Build and deploy an ADK agent that uses an MCP server on Cloud Run

Codelabs 1:[ ](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)[Build a Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps | Google Codelabs](https://codelabs.developers.google.com/adk-mcp-bigquery-maps?hl=en)
Codelabs 2:  [MCP Toolbox for Databases: Making BigQuery datasets available to MCP clients | Google Codelabs](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en)

Overview

This lab teaches you how to build an AI agent using ADK that connects to external tools through an MCP server. You’ll create a tour guide agent that fetches animal data from a zoo MCP server and enriches responses using Wikipedia. The lab demonstrates how to separate AI reasoning from data and tool access using secure APIs.

**What you'll learn**

How to structure a Python project for ADK deployment.

- How to implement a tool-using agent with Google-ADK.

- How to connect an agent to a remote MCP server for its toolset.

- How to deploy a Python application as a serverless container to Cloud Run.

- How to configure secure, service-to-service authentication using IAM roles.

- How to delete Cloud resources to avoid incurring future costs.

**Google Skills Lab (Optional)**
Model Context Protocol (MCP) Tools with ADK Agents
Google Skills Lab: 
[**Model Context Protocol (MCP) Tools with ADK Agents**](https://www.skills.google/focuses/132178?catalog_rank=%7B%22rank%22:1,%22num_filters%22:0,%22has_search%22:true%7D&parent=catalog&search_id=59957381)

In this lab, you learn how to:

- Use an ADK agent as an MCP client to interact with tools from existing MCP servers.

- Configure and deploy your own MCP server to expose ADK tools to other clients.

- Connect ADK agents with external tools through standardized MCP communication.

- Enable seamless interaction between LLMs and tools using Model Context Protocol.

**Project Submission**

**Problem Statement**

Build an **AI agent** that uses the **Model Context Protocol (MCP)** to connect to **one external tool or data source**, retrieve information, and use that information in its response.

This is a **mini project** focused on **data-to-agent integration**, not complex workflows.

**What You Must Build**

You must build **one AI agent** that:

- Is implemented using **ADK**

- Uses **MCP** to connect to **one tool or data source**

- Retrieves structured data or performs one external action

- Uses the retrieved data to generate its final response

We will take the cloud run link as submission along with the repository if applicable.

---

## Codelab 1: Build a Location Intelligence ADK Agent with MCP Servers for BigQuery and Google Maps

Build a Location Intelligence ADK Agent with MCP servers for BigQuery and Google Maps

About this codelab

subjectLast updated Mar 16, 2026

account_circleWritten by Rachael Deacon-Smith, Jeff Nelson

[1. Introduction](https://codelabs.developers.google.com/adk-mcp-bigquery-maps?hl=en)

In this Codelab, you will build an agent with ADK that is powered by Gemini 3.1 Pro. The agent will be equipped with tools from two remote (Google-hosted) MCP servers to securely access BigQuery for demographic, pricing, and sales data, and Google Maps for real-world location analysis and validation.

The agent orchestrates requests between the user and Google Cloud services to solve business problems related to the fictitious bakery dataset.

**What you'll do**

- **Set up the Data:** Create the foundational bakery dataset in BigQuery.

- **Develop the Agent:** Build an intelligent agent using the Agent Development Kit (ADK).

- **Integrate Tools:** Equip the agent with BigQuery and Maps functionalities via the MCP server.

- **Analyze**** the Market:** Interact with the agent to assess market trends and saturation.

**What you'll need**

- A web browser such as [Chrome](https://www.google.com/chrome/)

- A Google Cloud project with billing enabled or a Gmail account.

This Codelab is for developers of all levels, including beginners. You will use the command-line interface in Google Cloud Shell and Python code for ADK development. You don't need to be a Python expert, but a basic understanding of how to read code will help you understand the concepts.

[2. Before you begin](https://codelabs.developers.google.com/adk-mcp-bigquery-maps?hl=en)

Create a Google Cloud Project

- In the [Google Cloud Console](https://console.cloud.google.com/?utm_campaign=CDR_0x77c43128_default_b433981364&utm_medium=external&utm_source=blog), on the project selector page, [**select or create a Google Cloud project**](https://cloud.google.com/resource-manager/docs/creating-managing-projects?utm_campaign=CDR_0x77c43128_default_b433981364&utm_medium=external&utm_source=blog).

- Make sure that billing is enabled for your Cloud project. Learn how to [check if billing is enabled on a project](https://cloud.google.com/billing/docs/how-to/verify-billing-enabled?utm_campaign=CDR_0x77c43128_default_b429113443&utm_medium=external&utm_source=event).

**Start Cloud Shell**

**Cloud Shell** is a command-line environment running in Google Cloud that comes preloaded with necessary tools.

- Click **Activate Cloud Shell** at the top of the Google Cloud console:

- Once connected to Cloud Shell, run this command to **verify your authentication** in Cloud Shell:

gcloud auth list

- Run the following command to confirm that your project is configured for use with gcloud:

gcloud config get project

- Confirm the project is as expected, and then run the command below to **set your project id**:

export PROJECT_ID=$(gcloud config get project)

[3. Get the Code](https://codelabs.developers.google.com/adk-mcp-bigquery-maps?hl=en)

**Clone the Repository**

- Clone the repository to your Cloud Shell environment:

git clone https://github.com/google/mcp.git

- Navigate to the demo directory:

cd mcp/examples/launchmybakery

**Authenticate**

Run the following command to authenticate with your Google Cloud account. This is required for the ADK to access BigQuery.

gcloud auth application-default login

Follow the prompts to complete the authentication process.

**Note:** ADK does not automatically refresh your OAuth 2.0 token. If your chat session lasts more than 60 minutes, you may need to re-authenticate using the command above.

[4. Configure environment and BigQuery](https://codelabs.developers.google.com/adk-mcp-bigquery-maps?hl=en)

**Run Setup Scripts**

- Run the environment setup script. This script enables the BigQuery and Google Maps APIs, and creates a .env file with your Project ID and Maps API Key.

chmod +x setup/setup_env.sh
./setup/setup_env.sh

- Run the BigQuery setup script. This script automates creating the Cloud Storage bucket, uploading data, and provisioning the BigQuery dataset and tables.

chmod +x ./setup/setup_bigquery.sh
./setup/setup_bigquery.sh

Once the script completes, the mcp_bakery dataset should be created and be populated with the following tables:

- **demographics** - census data and population characteristics by zip code.

- **bakery_prices** - competitor pricing and product details for various baked goods.

- **sales_history_weekly** - weekly sales performance (quantity and revenue) by store and product.

- **foot_traffic** - estimated foot traffic scores by zip code and time of day.

- Verify the dataset and tables are created by visiting the **BigQuery**** console** in your Google Cloud Project:

[5. Install ADK](https://codelabs.developers.google.com/adk-mcp-bigquery-maps?hl=en)

Now that the infrastructure is ready, let's create a virtual Python environment and install the required packages for ADK.

- Create a virtual environment:

python3 -m venv .venv

- Activate the virtual environment:

source .venv/bin/activate

- Install the ADK:

pip install google-adk

- Navigate to the agent directory:

cd adk_agent/

[6. Inspect the ADK application](https://codelabs.developers.google.com/adk-mcp-bigquery-maps?hl=en)

Click the **Open Editor** button in Cloud Shell to open Cloud Shell Editor and view the cloned repository under the mcp/examples/launchmybakery directory.

The agent code is already provided in the adk_agent/ directory. Let's explore the solution structure:

launchmybakery/
├── data/                        # Pre-generated CSV files for BigQuery
├── adk_agent/                   # AI Agent Application (ADK)
│   └── mcp_bakery_app/          # App directory
│       ├── agent.py             # Agent definition
│       ├── tools.py             # Custom tools for the agent
│       └── .env                 # Project configuration (created by setup script)
├── setup/                       # Infrastructure setup scripts
└── cleanup/                     # Infrastructure cleanup scripts

Key files in mcp_bakery_app:

- agent.py: The core logic defining the agent, its tools, and the model (Gemini 3.1 Pro Preview).

- tools.py: Contains any custom tool definitions.

- .env: Contains your project configuration and secrets (like API keys) created by the setup script.

1. MCP Toolset Initialization:

Now, open adk_agent/mcp_bakery_app/tools.py in the Editor to understand how the MCP toolsets are initialized.

To enable our agent to communicate with BigQuery and Google Maps, we need to configure the Model Context Protocol (MCP) clients.

The code establishes secure connections to Google's remote MCP servers using StreamableHTTPConnectionParams.

def get_maps_mcp_toolset():
    dotenv.load_dotenv()
    maps_api_key = os.getenv('MAPS_API_KEY', 'no_api_found')
    
    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=MAPS_MCP_URL,
            headers={    
                "X-Goog-Api-Key": maps_api_key
            }
        )
    )
    print("MCP Toolset configured for Streamable HTTP connection.")
    return tools

def get_bigquery_mcp_toolset():   
        
    credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/bigquery"]
    )

    credentials.refresh(google.auth.transport.requests.Request())
    oauth_token = credentials.token
        
    HEADERS_WITH_OAUTH = {
        "Authorization": f"Bearer {oauth_token}",
        "x-goog-user-project": project_id
    }

    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=BIGQUERY_MCP_URL,
            headers=HEADERS_WITH_OAUTH
        )
    )
    print("MCP Toolset configured for Streamable HTTP connection.")
    return tools

- **Maps Toolset:** Configures the connection to the [Maps MCP server](https://developers.google.com/maps/ai/grounding-lite?utm_campaign=CDR_0xaea1deef_default_b460491199&utm_medium=external&utm_source=blog) using your API Key.

- **BigQuery**** Toolset:** This function configures the connection to the BigQuery MCP server. It uses google.auth to automatically retrieve your Cloud credentials, generates an OAuth Bearer token, and injects it into the Authorization header.

2. Agent Definition:

Now, open adk_agent/mcp_bakery_app/agent.py in the Editor to see how the agent is defined.

The LlmAgent is initialized with the gemini-3.1-pro-preview model.

maps_toolset = tools.get_maps_mcp_toolset()
bigquery_toolset = tools.get_bigquery_mcp_toolset()

root_agent = LlmAgent(
    model='gemini-3.1-pro-preview',
    name='root_agent',
    instruction=f"""
                Help the user answer questions by strategically combining insights from two sources:
                
                1.  **BigQuery toolset:** Access demographic (inc. foot traffic index), product pricing, and historical sales data in the  mcp_bakery dataset. Do not use any other dataset.
                Run all query jobs from project id: {project_id}. 

                2.  **Maps Toolset:** Use this for real-world location analysis, finding competition/places and calculating necessary travel routes.
                    Include a hyperlink to an interactive map in your response where appropriate.
            """,
    tools=[maps_toolset, bigquery_toolset]
)

- **System Instructions:** The agent is given specific instructions to combine insights from both BigQuery (for data) and Maps (for location analysis).

- **Tools:** Both the maps_toolset and bigquery_toolset are assigned to the agent, giving it access to the capabilities of both services.

The agent complies with the instructions and tools defined in the repo. Feel free to make changes to the instructions to see how it affects the agent's behavior.

[7. Chat with your agent!](https://codelabs.developers.google.com/adk-mcp-bigquery-maps?hl=en)

Return to the terminal in Cloud Shell and run this command to navigate to the adk_agent directory:

cd adk_agent

Run the following command to start the ADK web interface. This command spins up a lightweight web server to host the chat application:

adk web

Once the server starts, you will see the following in Cloud Shell:

+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://127.0.0.1:8000.                         |
+-----------------------------------------------------------------------------+

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

You have two options to access the ADK UI:

**Option 1: Click the local link** Click the http://127.0.0.1:8000 link that appears in your Cloud Shell terminal.

**Option 2: Use Web Preview**

- Click the **Web Preview** button in the top right corner of the Cloud Shell.

- Select **Change port**.

- Enter **8000** as the port number and click **Change and Preview**.

**Interact with the Agent** by asking the following questions in the Web UI. You should see the relevant tools being called.

- **Find the ****Neighborhood**** (Macro):** "I want to open a bakery in Los Angeles. Find the zip code with the highest morning foot traffic score."

The agent should use tools such get_table_info and execute_sql to query the foot_traffic table in BigQuery.

- **Validate the Location (Micro):** "Can you search for ‘Bakeries' in that zip code to see if it's saturated?"

The agent should use the search places tools in the Maps toolset to answer this question.

**Give it a go! Check out these sample questions to see your ADK agent in action:**

- "I'm looking to open my fourth bakery location in Los Angeles. I need a neighborhood with early activity. Find the zip code with the highest ‘morning' foot traffic score."

- "Can you search for ‘Bakeries' in that zip code to see if it's saturated? If there are too many, check for ‘Specialty Coffee' shops, so I can position myself near them to capture foot traffic."

- "Okay and I want to position this as a premium brand. What is the maximum price being charged for a ‘Sourdough Loaf' in the LA Metro area?"

- "Now I want a revenue projection for December 2025. Look at my sales history and take data from my best performing store for the ‘Sourdough Loaf'. Run a forecast for December 2025 to estimate the quantity I'll sell. Then, calculate the projected total revenue using just under the premium price we found (let's use $18)"

- "That'll cover my rent. Lastly, let's verify logistics. Find the closest "Restaurant Depot" to the proposed area and make sure that drive time is under 30 minutes for daily restocking."

## [**8. Clean Up**](https://codelabs.developers.google.com/adk-mcp-bigquery-maps?hl=en)

To avoid ongoing charges to your Google Cloud account, delete the resources created during this Codelab.

Run the cleanup script. This script will delete the BigQuery dataset, the Cloud Storage bucket, and the API keys created during setup.

chmod +x ../cleanup/cleanup_env.sh
./../cleanup/cleanup_env.sh

[9. Congratulations](https://codelabs.developers.google.com/adk-mcp-bigquery-maps?hl=en)

**Mission Complete!** You have successfully built a Location Intelligence Agent using the Agent Development Kit (ADK).

By bridging the gap between your "enterprise" data in **BigQuery** and real-world location context from **Google Maps**, you've created a powerful tool capable of complex business reasoning - all powered by the Model Context Protocol (MCP) and Gemini.

**What you accomplished:**

- **Infrastructure as Code:** You provisioned a data stack using Google Cloud CLI tools.

- **MCP Integration:** You connected an AI agent to two distinct remote MCP servers (BigQuery & Maps) without writing complex API wrappers.

- **Unified Reasoning:** You built a single agent capable of strategically combining insights from two different domains to solve a business problem.

**Reference docs**

- [Use the BigQuery MCP server](https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp?utm_campaign=CDR_0xaea1deef_default_b460491199&utm_medium=external&utm_source=blog)

- [Use the Maps Groundling Lite MCP Server](https://developers.google.com/maps/ai/grounding-lite?utm_campaign=CDR_0xaea1deef_default_b460491199&utm_medium=external&utm_source=blog)

- [Authenticate MCP](https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp?utm_campaign=CDR_0xaea1deef_default_b460491199&utm_medium=external&utm_source=blog)

---

## Codelab 2: MCP Toolbox for Databases — Making BigQuery Datasets Available to MCP Clients

MCP Toolbox for Databases:

Making BigQuery datasets available to MCP clients

About this codelab

subjectLast updated Mar 27, 2026

account_circleWritten by Romin Irani

[1. Introduction](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en)

In this codelab, you will be utilizing the [MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) to make available your BigQuery datasets.

Through the codelab, you will employ a step by step approach as follows:

- Identify a specific BigQuery dataset ("Google Cloud Release Notes") from the public BigQuery datasets program.

- Setup MCP Toolbox for Databases, that connects to the BigQuery dataset.

- Develop an Agent using Agent Development Kit (ADK) that will utilize the MCP Toolbox to answer queries from the user about Google Cloud Release notes

**What you'll do**

- Setup MCP Toolbox for Databases to expose Google Cloud Release notes, a public BigQuery dataset, as a MCP Interface to other MCP Clients (IDEs, Tools, etc).

**What you'll learn**

- Explore BigQuery public datasets and choose a specific dataset.

- Setup MCP Toolbox for Databases for the BigQuery public dataset that we want to make available to MCP clients.

- Design and develop an Agent using Agent Development Kit (ADK) to answer user queries.

- Test out the Agent and MCP Toolbox for Databases in the local environment.

**What you'll need**

- Chrome web browser.

- A local Python development environment.

[2. Before you begin](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en)

**For Google Cloud Credits:** To help you get started, redeem your free Google Cloud credits using this [link](https://goo.gle/mcp-toolbox-bigquery-lab). You can follow the instructions [here](https://codelabs.developers.google.com/codelabs/cloud-codelab-credits) to activate the credit and create a new project.

Create a project

- In the [Google Cloud Console](https://console.cloud.google.com/), on the project selector page, select or create a Google Cloud [project](https://cloud.google.com/resource-manager/docs/creating-managing-projects).

- Make sure that billing is enabled for your Cloud project. Learn how to [check if billing is enabled on a projec](https://cloud.google.com/billing/docs/how-to/verify-billing-enabled) .

- You'll use [Cloud Shell](https://cloud.google.com/cloud-shell/), a command-line environment running in Google Cloud that comes preloaded with bq. Click Activate Cloud Shell at the top of the Google Cloud console.

- Once connected to Cloud Shell, you check that you're already authenticated and that the project is set to your project ID using the following command:

gcloud auth list

- Run the following command in Cloud Shell to confirm that the gcloud command knows about your project.

gcloud config list project

- If your project is not set, use the following command to set it:

gcloud config set project <YOUR_PROJECT_ID>

- Enable the required APIs via the command shown below. This could take a few minutes, so please be patient.

gcloud services enable cloudresourcemanager.googleapis.com \
                       servicenetworking.googleapis.com \
                       run.googleapis.com \
                       cloudbuild.googleapis.com \
                       cloudfunctions.googleapis.com \
                       aiplatform.googleapis.com \
                       sqladmin.googleapis.com \
                       compute.googleapis.com 

On successful execution of the command, you should see a message similar to the one shown below:

Operation "operations/..." finished successfully.

The alternative to the gcloud command is through the console by searching for each product or using this [link](https://console.cloud.google.com/apis/enableflow?apiid=firestore.googleapis.com,compute.googleapis.com,cloudresourcemanager.googleapis.com,servicenetworking.googleapis.com,run.googleapis.com,cloudbuild.googleapis.com,cloudfunctions.googleapis.com,aiplatform.googleapis.com).

If any API is missed, you can always enable it during the course of the implementation.

Refer [documentation](https://cloud.google.com/sdk/gcloud/reference/config/list) for gcloud commands and usage.

[3. Google Release Notes Dataset and MCP clients](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en)

First up, let us take a look at Google Cloud Release notes that are regularly updated at the [official Google Cloud Release Notes webpage](https://cloud.google.com/release-notes), a screenshot of which is shown below:

You might subscribe to the feed URL but what if we could simply ask in our Agent Chat about these Release notes. Maybe a simple query like "Update me on Google Cloud Release Notes".

[4. MCP Toolbox for Databases](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en)

[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) is an open source MCP server for databases It was designed with enterprise-grade and production-quality in mind. It enables you to develop tools easier, faster, and more securely by handling the complexities such as connection pooling, authentication, and more.

Toolbox helps you build Gen AI tools that let your agents access data in your database. Toolbox provides:

- Simplified development: Integrate tools to your agent in less than 10 lines of code, reuse tools between multiple agents or frameworks, and deploy new versions of tools more easily.

- Better performance: Best practices such as connection pooling, authentication, and more.

- Enhanced security: Integrated auth for more secure access to your data

- End-to-end observability: Out of the box metrics and tracing with built-in support for OpenTelemetry.

- Toolbox makes it easy to connect databases to any MCP-capable AI assistants, even those that are in your IDE.

Toolbox sits between your application's orchestration framework and your database, providing a control plane that is used to modify, distribute, or invoke tools. It simplifies the management of your tools by providing you with a centralized location to store and update tools, allowing you to share tools between agents and applications and update those tools without necessarily redeploying your application.

To summarize in simple words:

- MCP Toolbox is available as a binary, container image or you can build it from source.

- It exposes a set of tools that you configure via a tools.yaml file. The tools can be thought of connecting to your data sources. You can see the various data sources that it supports : AlloyDB, BigQuery, etc.

- Since this toolbox now supports MCP, you automatically have a MCP Server endpoint that can then be consumed by the Agents (IDEs) or you can use them while developing your Agent Applications using various frameworks like Agent Development Kit (ADK).

Our focus in this blog post is going to be on the areas highlighted below:

In summary, we are going to create a configuration in the MCP Toolbox for Databases that knows how to connect to our BigQuery dataset. We will then develop an Agent using Agent Development Kit (ADK) that will integrate with the MCP Toolbox endpoint and allow us to send natural queries to ask about our dataset. Think of it as an agentic application that you are developing that knows how to talk to your BigQuery dataset and it runs some queries.

[5. BigQuery Dataset for Google Cloud Release Notes](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en)

The [Google Cloud Public Dataset Program](https://cloud.google.com/datasets) is a program that makes available a range of [datasets](https://cloud.google.com/datasets?e=48754805) for your applications. One such dataset is the Google Cloud Release Notes database. This dataset provides you the same information as the [official Google Cloud Release Notes webpage](https://cloud.google.com/release-notes) and it is available as a publicly queryable dataset.

As a test, I simply validate the dataset by running a simple query shown below:

SELECT
       product_name,description,published_at
     FROM
       `bigquery-public-data`.`google_cloud_release_notes`.`release_notes`
     WHERE
       DATE(published_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
     GROUP BY product_name,description,published_at
     ORDER BY published_at DESC

This gets me a list of records from the Release Notes dataset that have been published in the last 7 days.

Substitute this with any other dataset of your choice and your respective queries and parameters that you'd like. All we need to do now is set this up as a Data Source and Tool in MCP Toolbox for Databases. Let's see how to do that.

[6. Installing MCP Toolbox for Databases](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en)

Open a terminal on your local machine and create a folder named mcp-toolbox.

mkdir mcp-toolbox

Go to the mcp-toolbox folder via the command shown below:

cd mcp-toolbox

Install the binary version of the MCP Toolbox for Databases via the script given below. The command given below is for Linux but if you are on Mac or Windows, ensure that you are downloading the correct binary. Check out the [releases page for your Operation System and Architecture](https://github.com/googleapis/genai-toolbox/releases) and download the correct binary.

export VERSION=0.23.0
curl -O https://storage.googleapis.com/genai-toolbox/v$VERSION/linux/amd64/toolbox
chmod +x toolbox

We now have the binary version of the toolbox ready for our use. The next step is to configure the toolbox with our data sources and other configurations.

[7. Configuring the MCP Toolbox for Databases](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en)

Now, we need to define our BigQuery dataset and tools in the tools.yaml file that is needed by the MCP Toolbox for Database. The file tools.yaml is the primary way to configure Toolbox.

Create a file named tools.yaml in the same folder i.e. mcp-toolbox, the contents of which is shown below.

You can use the nano editor that is available in Cloud Shell. The nano command is as follows: "nano tools.yaml".

Remember to replace the YOUR_PROJECT_ID value with your Google Cloud Project Id.

sources:
 my-bq-source:
   kind: bigquery
   project: YOUR_PROJECT_ID

tools:
 search_release_notes_bq:
   kind: bigquery-sql
   source: my-bq-source
   statement: |
    SELECT
     product_name,description,published_at
    FROM
      `bigquery-public-data`.`google_cloud_release_notes`.`release_notes`
    WHERE
     DATE(published_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    GROUP BY product_name,description,published_at
    ORDER BY published_at DESC
   description: |
    Use this tool to get information on Google Cloud Release Notes.

toolsets:
 my_bq_toolset:
   - search_release_notes_bq

Let us understand the file in brief:

- Sources represent your different data sources that a tool can interact with. A Source represents a data source that a tool can interact with. You can define Sources as a map in the sources section of your tools.yaml file. Typically, a source configuration will contain any information needed to connect with and interact with the database. In our case, we have defined a BigQuery source my-bq-source and you need to provide your Google Cloud Project Id. For more information, refer to the [Sources](https://googleapis.github.io/genai-toolbox/resources/sources/) reference.

- Tools define actions an agent can take – such as reading and writing to a source. A tool represents an action your agent can take, such as running a SQL statement. You can define Tools as a map in the tools section of your tools.yaml file. Typically, a tool will require a source to act on. In our case, we define a single tool search_release_notes_bq. This references the BigQuery source my-bq-source that we defined in the first step. It also has the statement and the instruction that will be used by the AI Agent clients. For more information, refer to the [Tools](https://googleapis.github.io/genai-toolbox/resources/tools/) reference.

- Finally, we have the Toolset, that allows you to define groups of tools that you want to be able to load together. This can be useful for defining different groups based on agent or application. In our case, we have a toolset definition where we have currently defined only one existing tool search_release_notes_bq that we defined. You can have more than one toolset, which has a combination of different tools.

So currently, we have defined only one tool that gets the release notes for the last 7 days as per the query. But you can have various combinations with parameters too.

Check out some more configuration details ( [Source](https://googleapis.github.io/genai-toolbox/resources/sources/bigquery/), [Tools](https://googleapis.github.io/genai-toolbox/resources/tools/bigquery-sql/)) in the BigQuery datasource configuration in MCP Toolbox for Databases.

[8. Testing the MCP Toolbox for Databases](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en)

We have downloaded and configured the Toolbox with the tools.yaml file in the mcp-toolbox folder. Let's run it locally first.

Execute the following command:

./toolbox --tools-file="tools.yaml"

On successful execution, you should see a server startup with sample output similar to the one below:

2025-12-09T08:27:02.777619+05:30 INFO "Initialized 1 sources: my-bq-source" 
2025-12-09T08:27:02.777695+05:30 INFO "Initialized 0 authServices: " 
2025-12-09T08:27:02.777707+05:30 INFO "Initialized 1 tools: search_release_notes_bq" 
2025-12-09T08:27:02.777716+05:30 INFO "Initialized 2 toolsets: my_bq_toolset, default" 
2025-12-09T08:27:02.777719+05:30 INFO "Initialized 0 prompts: " 
2025-12-09T08:27:02.777723+05:30 INFO "Initialized 1 promptsets: default" 
2025-12-09T08:27:02.77773+05:30 WARN "wildcard (`*`) allows all origin to access the resource and is not secure. Use it with cautious for public, non-sensitive data, or during local development. Recommended to use `--allowed-origins` flag to prevent DNS rebinding attacks" 
2025-12-09T08:27:02.777839+05:30 INFO "Server ready to serve!"

The MCP Toolbox Server runs by default on port 5000. If you find that port 5000 is already in use, feel free to use another port (say 7000) as per the command shown below. Please use 7000 then instead of the 5000 port in the subsequent commands.

./toolbox --tools-file "tools.yaml" --port 7000

Let us use Cloud Shell to test this out.

Click on Web Preview in Cloud Shell as shown below:

Click on **Change port** and set the port to 5000 as shown below and click on Change and Preview.

This should bring the following output:

In the browser URL, add the following to the end of the URL:

/api/toolset

This should bring up the tools that are currently configured. A sample output is shown below:

{
  "serverVersion": "0.22.0+binary.linux.amd64.1a6dfe8d37d0f42fb3fd3f75c50988534dbc1b85",
  "tools": {
    "search_release_notes_bq": {
      "description": "Use this tool to get information on Google Cloud Release Notes.\n",
      "parameters": [],
      "authRequired": []
    }
  }
}

**Test the Tools via MCP Toolbox for Databases UI**

The Toolbox provides a visual interface (**Toolbox UI**) to directly interact with tools by modifying parameters, managing headers, and executing calls, all within a simple web UI.

If you would like to test that out, you can run the previous command that we used to launch the Toolbox Server with a --ui option.

To do that, shutdown the previous instance of the MCP Toolbox for Databases Server that you may have running and give the following command:

./toolbox --tools-file "tools.yaml" --ui

Ideally you should see an output that the Server has been able to connect to our data sources and has loaded the toolset and tools. A sample output is given below and you will notice that it will mention that the Toolbox UI is up and running.

2025-12-09T08:28:07.479989+05:30 INFO "Initialized 1 sources: my-bq-source" 
2025-12-09T08:28:07.480065+05:30 INFO "Initialized 0 authServices: " 
2025-12-09T08:28:07.480079+05:30 INFO "Initialized 1 tools: search_release_notes_bq" 
2025-12-09T08:28:07.480087+05:30 INFO "Initialized 2 toolsets: my_bq_toolset, default" 
2025-12-09T08:28:07.48009+05:30 INFO "Initialized 0 prompts: " 
2025-12-09T08:28:07.480094+05:30 INFO "Initialized 1 promptsets: default" 
2025-12-09T08:28:07.4801+05:30 WARN "wildcard (`*`) allows all origin to access the resource and is not secure. Use it with cautious for public, non-sensitive data, or during local development. Recommended to use `--allowed-origins` flag to prevent DNS rebinding attacks" 
2025-12-09T08:28:07.480214+05:30 INFO "Server ready to serve!" 
2025-12-09T08:28:07.480218+05:30 INFO "Toolbox UI is up and running at: http://127.0.0.1:5000/ui" 

Click on the UI url and ensure that you have the /ui at the end of the URL. This will display a UI as shown below:

Click on the Tools option on the left to view the tools that have been configured and in our case, it should just one i.e. search_release_notes_bq, as shown below:

Simply click the tools (search_release_notes_bq) and it should bring up a page for you to test out the tool. Since there are no parameters to provide, you can simply click on the **Run Tool** to see the result. A sample run is shown below:

The MCP Toolkit for Databases also describes a Pythonic way for you to validate and test out the tools, which is documented over [here](https://github.com/googleapis/genai-toolbox?tab=readme-ov-file). We will skip that and jump directly into the Agent Development Kit (ADK) in the next section that will utilize these tools.

[9. Writing our Agent with Agent Development Kit (ADK)](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en)

**Install the Agent Development Kit (ADK)**

Open a new terminal tab in Cloud Shell and create a folder named my-agents as follows. Navigate to the my-agents folder too.

mkdir my-agents
cd my-agents

Now, let's create a virtual Python environment using venv as follows:

python -m venv .venv

Activate the virtual environment as follows:

source .venv/bin/activate

Install the ADK and the MCP Toolbox for Databases packages along with langchain dependency as follows:

pip install google-adk toolbox-core

You will now be able to invoke the adk utility as follows.

adk

It will show you a list of commands.

$ adk
Usage: adk [OPTIONS] COMMAND [ARGS]...

  Agent Development Kit CLI tools.

Options:
  --help  Show this message and exit.

Commands:
  api_server  Starts a FastAPI server for agents.
  create      Creates a new app in the current folder with prepopulated agent template.
  deploy      Deploys agent to hosted environments.
  eval        Evaluates an agent given the eval sets.
  run         Runs an interactive CLI for a certain agent.
  web         Starts a FastAPI server with Web UI for agents.

**Creating our first Agent Application**

We are now going to use adk to create a scaffolding for Google Cloud Release Notes Agent Application via the adk create command with an app name **(gcp_releasenotes_agent_app)**as given below.

adk create gcp_releasenotes_agent_app

Follow the steps and select the following:

- Gemini model for choosing a model for the root agent.

- Choose Vertex AI for the backend.

- Your default Google Project Id and region will be displayed. Select the default itself.

Choose a model for the root agent:
1. gemini-2.5-flash
2. Other models (fill later)

Choose model (1, 2): 1
1. Google AI
2. Vertex AI
Choose a backend (1, 2): 2

You need an existing Google Cloud account and project, check out this link for details:
https://google.github.io/adk-docs/get-started/quickstart/#gemini---google-cloud-vertex-ai

Enter Google Cloud project ID [YOUR_GOOGLE_PROJECT_ID]: 
Enter Google Cloud region [us-central1]: 

Agent created in ../my-agents/gcp_releasenotes_agent_app:
- .env
- __init__.py
- agent.py

Observe the folder in which a default template and required files for the Agent have been created.

First up is the .env file. The contents of which are shown below:

GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=YOUR_GOOGLE_PROJECT_ID
GOOGLE_CLOUD_LOCATION=YOUR_GOOGLE_PROJECT_REGION

The values indicate that we will be using Gemini via Vertex AI along with the respective values for the Google Cloud Project Id and location.

Then we have the __init__.py file that marks the folder as a module and has a single statement that imports the agent from the agent.py file.

from . import agent

Finally, let's take a look at the agent.py file. The contents are shown below:

from google.adk.agents import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)

This is the simplest Agent that you can write with ADK. From the ADK documentation [page](https://google.github.io/adk-docs/agents/), an Agent is a self-contained execution unit designed to act autonomously to achieve specific goals. Agents can perform tasks, interact with users, utilize external tools, and coordinate with other agents.

Specifically, an LLMAgent, commonly aliased as Agent, utilizes Large Language Models (LLMs) as their core engine to understand natural language, reason, plan, generate responses, and dynamically decide how to proceed or which tools to use, making them ideal for flexible, language-centric tasks. Learn more about LLM Agents [here](https://google.github.io/adk-docs/agents/llm-agents/).

This completes our scaffolding to generate a basic Agent using the Agent Development Kit (ADK). We are now going to connect our Agent to the MCP Toolbox, so that it can use that tool to answer queries from the user (in this case, it will be the Google Cloud Release notes).

[10. Connecting our Agent to Tools](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en)

We are going to connect this Agent to Tools now. In the context of ADK, a Tool represents a specific capability provided to an AI agent, enabling it to perform actions and interact with the world beyond its core text generation and reasoning abilities.

In our case, we are going to equip our Agent now with the Tools that we have configured in the MCP Toolbox for Databases.

Modify the agent.py file with the following code. Notice that we are using the default port 5000 in the code, but if you are using an alternate port number, please use that.

from google.adk.agents import Agent
from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("http://127.0.0.1:5000")

# Load all the tools
tools = toolbox.load_toolset('my_bq_toolset')

root_agent = Agent(
    name="gcp_releasenotes_agent",
    model="gemini-2.5-flash",
    description=(
        "Agent to answer questions about Google Cloud Release notes."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the Google Cloud Release notes. Use the tools to answer the question"
    ),
    tools=tools,
)

We can now test the Agent that will fetch real data from our BigQuery dataset that has been configured with the MCP Toolbox for Databases.

To do this, follow this sequence:

In one terminal of Cloud Shell, launch the MCP Toolbox for Databases. You might already have it running locally on port 5000 as we tested earlier. If not, run the following command (from the mcp-toolbox folder) to start the server:

./toolbox --tools_file "tools.yaml"

Ideally you should see an output that the Server has been able to connect to our data sources and has loaded the toolset and tools.

Once the MCP server has started successfully, in another terminal, launch the Agent via the adk run (from the my-agents folder) command shown below. You could also use the adk web command if you like.

$ adk run gcp_releasenotes_agent_app/

Log setup complete: /tmp/agents_log/agent.20250423_170001.log
To access latest log: tail -F /tmp/agents_log/agent.latest.log
Running agent gcp_releasenotes_agent, type exit to exit.

[user]: get me the google cloud release notes

[gcp_releasenotes_agent]: Here are the Google Cloud Release Notes.

Google SecOps SOAR: Release 6.3.49 is being rolled out to the first phase of regions. This release contains internal and customer bug fixes. Published: 2025-06-14

Compute Engine: Dynamic NICs let you add or remove network interfaces to or from an instance without having to restart or recreate the instance. You can also use Dynamic NICs when you need more network interfaces. The maximum number of vNICs for most machine types in Google Cloud is 10; however, you can configure up to 16 total interfaces by using Dynamic NICs. Published: 2025-06-13

Compute Engine: General purpose C4D machine types, powered by the fifth generation AMD EPYC processors (Turin) and Google Titanium, are generally available. Published: 2025-06-13

Google Agentspace: Google Agentspace Enterprise: App-level feature management. As an Agentspace administrator, you can choose to turn the following features on or off for your end users in the web app: Agents gallery, Prompt gallery, No-code agent, NotebookLM Enterprise. Published: 2025-06-13

Cloud Load Balancing: Cloud Load Balancing supports load balancing to multi-NIC instances that use Dynamic NICs. This capability is in Preview. Published: 2025-06-13

Virtual Private Cloud: Dynamic Network Interfaces (NICs) are available in Preview. Dynamic NICs let you update an instance to add or remove network interfaces without having to restart or recreate the instance. Published: 2025-06-13

Security Command Center: The following Event Threat Detection detectors for Vertex AI have been released to Preview:
- `Persistence: New Geography for AI Service`
- `Privilege Escalation: Anomalous Multistep Service Account Delegation for AI Admin Activity`
- `Privilege Escalation: Anomalous Multistep Service Account Delegation for AI Data Access`
- `Privilege Escalation: Anomalous Service Account Impersonator for AI Admin Activity`
- `Privilege Escalation: Anomalous Service Account Impersonator for AI Data Access`
- `Privilege Escalation: Anomalous Impersonation of Service Account for AI Admin Activity`
- `Persistence: New AI API Method`
......
......

Notice that the Agent is utilizing the tool that we have configured in the MCP Toolbox for Databases (search_release_notes_bq) and retrieves the data from the BigQuery dataset and format the response accordingly.

[11. Congratulations](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en)

Congratulations, you've successfully configured the MCP Toolbox for Databases and configured a BigQuery dataset for access within MCP clients.

**Reference docs**

- [MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox)

- [BigQuery public datasets](https://cloud.google.com/bigquery/public-data?utm_campaign=CDR_0xd466e25b_awareness&utm_source=external&utm_medium=web)

---

## Codelab 3: Use MCP Tools with ADK Agents

Use Model Context Protocol (MCP) Tools with ADK Agents

experimentLabschedule1 houruniversal_currency_alt7 Creditsshow_chartAdvanced

infoThis lab may incorporate AI tools to support your learning.

**GENAI124**

**Overview**

In this lab, you explore [Model Context Protocol](https://modelcontextprotocol.io/) (MCP), an open standard that enables seamless integration between external services, data sources, tools, and applications. You learn how to integrate MCP into your Agent Development Kit (ADK) agents, using tools provided by existing MCP servers to enhance your ADK workflows. Additionally, you discover how to expose ADK tools like load_web_page through a custom-built MCP server, enabling broader integration with MCP clients.

**What is Model Context Protocol (MCP)?**

Model Context Protocol (MCP) is an open standard designed to standardize how Large Language Models (LLMs) like Gemini and Claude communicate with external applications, data sources, and tools. Think of it as a universal connection mechanism that simplifies how LLMs obtain context, execute actions, and interact with various systems.

MCP follows a client-server architecture, defining how data (resources), interactive templates (prompts), and actionable functions (tools) are exposed by an MCP server and consumed by an MCP client (which could be an LLM host application or an AI agent).

This lab covers two primary integration patterns:

- **Using existing MCP Servers within ADK:** An ADK agent acts as an MCP client, leveraging tools provided by external MCP servers.

- **Exposing ADK Tools via an MCP Server:** Building an MCP server that wraps ADK tools, making them accessible to any MCP client.

Objectives

In this lab, you learn how to perform the following tasks:

- Use an ADK agent as an MCP client to interact with tools from existing MCP servers.

- Configure and deploy your own MCP server to expose ADK tools to other clients.

- Connect ADK agents with external tools through standardized MCP communication.

- Enable seamless interaction between LLMs and tools using MCP.

**Setup and requirements**

**Before you click the Start Lab button**

Read these instructions. Labs are timed and you cannot pause them. The timer, which starts when you click **Start Lab**, shows how long Google Cloud resources will be made available to you.

This Qwiklabs hands-on lab lets you do the lab activities yourself in a real cloud environment, not in a simulation or demo environment. It does so by giving you new, temporary credentials that you use to sign in and access Google Cloud for the duration of the lab.

**What you need**

To complete this lab, you need:

- Access to a standard internet browser (Chrome browser recommended).

- Time to complete the lab.

**Note:** If you already have your own personal Google Cloud account or project, do not use it for this lab.

**Note:** If you are using a Pixelbook, open an Incognito window to run this lab.

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

**Task 1. Install the ADK and set up your environment**

In this lab environment, the **Vertex AI API**, **Routes API**, and **Directions API** have been enabled for you.

Prepare a Cloud Shell Editor tab

- From the Google Cloud console, press G,S to open Cloud Shell. Alternatively, you can click the **Activate Cloud Shell** button () in the upper right of the Cloud console.

- Click **Continue**.

- When prompted to authorize Cloud Shell, click **Authorize**.

- In the upper-right corner of the Cloud Shell terminal panel, click the **Open in new window** button ().

- Click the **Open Editor** icon () at the top of the pane to view files.

- At the top of the left-hand navigation menu, click the **Explorer** icon () to open your file explorer.

- Click the **Open Folder** button.

- In the Open Folder dialog that opens, click **OK** to select your student account's home folder.

- Close any additional tutorial or Gemini panels that appear on the right side of the screen to save more of your window for your code editor.

- Throughout the rest of this lab, you work in this window as your IDE with the Cloud Shell Editor and Cloud Shell terminal.

Download and install the ADK and code samples for this lab

In this section, you run the commands that follow in the Cloud Shell terminal.

- Run the following command in the Cloud Shell terminal to copy a project directory with code for this lab from Cloud Storage:

gcloud storage cp -r gs://YOUR_GCP_PROJECT_ID-bucket/* .

Copied!

- Install ADK and additional lab requirements with the following commands:

- export PATH=$PATH:"/home/${USER}/.local/bin"

python3 -m pip install google-adk -r adk_mcp_tools/requirements.txt

Copied!

Click **Check my progress** to verify the objective.

Install the ADK and set up your environment

**Task 2. Use the Google Maps MCP server with ADK agents (ADK as an MCP client) in the ADK Dev UI**

This section demonstrates how to integrate tools from an external Google Maps MCP server into your ADK agents. This is the most common integration pattern when your ADK agent needs to use capabilities provided by an existing service that exposes an MCP interface. You will see how the MCPToolset class can be directly added to your agent's tools list, enabling seamless connection to an MCP server, discovery of its tools, and making them available for your agent to use. These examples primarily focus on interactions within the adk web development environment.

MCPToolset

The MCPToolset class is ADK's primary mechanism for integrating tools from an MCP server. When you include an MCPToolset instance in your agent's tools list, it automatically handles the interaction with the specified MCP server. Here's how it works:

- **Connection Management**: On initialization, MCPToolset establishes and manages the connection to the MCP server. This can be a local server process (using StdioServerParameters for communication over standard input/output) or a remote server (using SseServerParams for Server-Sent Events). The toolset also handles the graceful shutdown of this connection when the agent or application terminates.

- **Tool Discovery ****&**** Adaptation**: Once connected, MCPToolset queries the MCP server for its available tools (via the list_tools MCP method). It then converts the schemas of these discovered MCP tools into ADK-compatible BaseTool instances.

- **Exposure to Agent**: These adapted tools are then made available to your LlmAgent as if they were native ADK tools.

- **Proxying Tool Calls**: When your LlmAgent decides to use one of these tools, MCPToolset transparently proxies the call (using the call_tool MCP method) to the MCP server, sends the necessary arguments, and returns the server's response back to the agent.

- **Filtering (Optional)**: You can use the tool_filter parameter when creating an MCPToolset to select a specific subset of tools from the MCP server, rather than exposing all of them to your agent.

Get an API key and enable the APIs

In this sub-section, you generate a new API key named **GOOGLE_MAPS_API_KEY**.

- Go to the **Google Cloud console** browser tab (not your Cloud Shell Editor).

- You can **close** the Cloud Shell terminal pane in this browser tab for more console area.

- Search for **Credentials** in the search bar at the top of the page. Select it from the results.

- On the **Credentials** page, click **Create credentials** at the top of the page, then select **API key**.

The **API key created** dialog displays your newly created API key. Be sure to copy and save this key locally for use later in the lab.

- Click **Close** on the dialog box.

Your newly created key is named **API Key 1** by default. Select the key, rename it to **GOOGLE_MAPS_API_KEY**, and click **Save**.

Define your Agent with an MCPToolset for Google Maps

In this sub-section, you configure your agent to use the MCPToolset for Google Maps, enabling it to seamlessly provide directions and location-based information.

- Paste the following command into a plain text document on your computer, then update the YOUR_ACTUAL_API_KEY value with the Google Maps API key you generated and saved in a previous step:

- cd ~/adk_mcp_tools

- cat << EOF > google_maps_mcp_agent/.env

- GOOGLE_GENAI_USE_VERTEXAI=TRUE

- GOOGLE_CLOUD_PROJECT=Project

- GOOGLE_CLOUD_LOCATION=global

- GOOGLE_MAPS_API_KEY="YOUR_ACTUAL_API_KEY"

- MODEL=gemini_flash_model_id

EOF

Copied!

- Copy and paste the updated command into the Cloud Shell terminal and run it to write a **.env** file, which provides authentication details for this agent directory.

- Copy the **.env** file to the other agent directory for later use in this lab by running the following command:

cp google_maps_mcp_agent/.env adk_mcp_server/.env

Copied!

- In the Cloud Shell Editor's file explorer pane, find the **adk_mcp_tools** folder. Click it to toggle it open.

- Navigate to the directory **adk_mcp_tools/google_maps_mcp_agent**.

- In the agent.py file in this directory, add the following code after the comment ## Add the MCPToolset below: (insert it on a new line after **line 39**) to add the Google maps tool to your agent. This allows your agent to use the **MCPToolset** for Google Maps to provide directions or location-based information.

- tools=[

-     MCPToolset(

-     connection_params=StdioConnectionParams(

-         server_params=StdioServerParameters(

-             command='npx',

-             args=[

-                 "-y",

-                 "@modelcontextprotocol/server-google-maps",

-             ],

-             env={

-                 "GOOGLE_MAPS_API_KEY": google_maps_api_key

-             }

-         ),

-         timeout=15,

-         ),

-     )

],

Copied!

- **Save** the file.

- From the **adk_mcp_tools** project directory, launch the **Agent Development Kit Dev UI** with the following command:

adk web --allow_origins "regex:https://.*\.cloudshell\.dev"

Copied!

**Output:**

INFO:     Started server process [2434]

INFO:     Waiting for application startup.

+----------------------------------------------------+

| ADK Web Server started                             |

|                                                    |

| For local testing, access at http://localhost:8000.|

+----------------------------------------------------+

INFO:     Application startup complete.

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

- To view the web interface in a new tab, click the **http://127.0.0.1:8000** link in the terminal output.

- A new browser tab opens with the ADK Dev UI. From the **Select an agent** drop-down on the left, select the **google_maps_mcp_agent**.

- Start a conversation with the agent and run the following prompts:

Get directions from GooglePlex to SFO.

Copied!

**Note: **If your API call times out the first time you use it, click **+ New Session** in the upper right of the ADK Dev UI and try again.

What's the route from Paris, France to Berlin, Germany?

Copied!

**Output:**

- Click the **agent icon** next to the agent's chat bubble with a lightning bolt, which indicates a function call. This opens up the Event inspector for this event.

Notice that the agent graph indicates several different tools, identified by the wrench emoji (🔧). Even though you only imported one MCPToolset, that toolset came with the different tools you see listed here, such as maps_place_details and maps_directions.

On the **Request** tab, you can see the structure of the request. You can use the arrows at the top of the Event inspector to browse the agent's thoughts, function calls, and responses.

- When you are finished asking questions of this agent, close the Dev UI browser tab.

- Go back to the Cloud Shell terminal panel and press CTRL+C to stop the server.

Click **Check my progress** to verify the objective.

Create the API key and deploy the ADK agent

**Task 3. Build an MCP server with ADK tools (MCP server exposing ADK)**

In this section, you learn how to expose the ADK load_web_page tool through a custom-built MCP server. This pattern allows you to wrap existing ADK tools and make them accessible to any standard MCP client application.

Create the MCP Server script and implement server logic

- Return to your Cloud Shell Editor and select the **adk_mcp_tools/adk_mcp_server** directory.

- Select the Python file named **adk_server.py** that has been prepared and commented for you.

Take some time to review that file, reading the comments to understand how the code wraps a tool and serves it as an MCP server. Notice how it allows MCP clients to list available tools as well as invoke the ADK tool asynchronously, handling requests and responses in an MCP-compliant format.

Test the custom MCP Server with an ADK Agent

- Using your Cloud Shell Editor, in the **adk_mcp_server** directory, click on the **agent.py** file

- In **line 22** of the **agent.py** file, update the path to your **adk_server.py** file that is assigned to the variable PATH_TO_YOUR_MCP_SERVER_SCRIPT with the following value:

/home/Username/adk_mcp_tools/adk_mcp_server/adk_server.py

Copied!

- Next, add the following code in **line 38**, i.e. after where it says ## Add the MCPToolset below: in the agent.py file, to add the **MCPToolset** to your agent. An ADK agent acts as a client to the MCP server. This ADK agent uses MCPToolset to connect to your adk_server.py script.

- tools=[

-     MCPToolset(

-     connection_params=StdioConnectionParams(

-         server_params=StdioServerParameters(

-             command="python3", # Command to run your MCP server script

-             args=[PATH_TO_YOUR_MCP_SERVER_SCRIPT], # Argument is the path to the script

-         ),

-         timeout=15,

-         ),

-         tool_filter=['load_web_page'] # Optional: ensure only specific tools are loaded

-     )

],

Copied!

- **Save** the file.

- To run the MCP server, start the adk_server.py script by running the following command in the Cloud Shell terminal:

python3 ~/adk_mcp_tools/adk_mcp_server/adk_server.py

Copied!

**Output:**

- Open a new Cloud Shell terminal tab by clicking the  button at the top of the Cloud Shell terminal window.

- In the Cloud Shell terminal, from the **adk_mcp_tools** project directory, launch the **Agent Development Kit Dev UI** with the following command:

- cd ~/adk_mcp_tools

adk web --allow_origins "regex:https://.*\.cloudshell\.dev"

Copied!

- To view the web interface in a new tab, click the **http://127.0.0.1:8000** link in the terminal output.

- From the **Select an agent drop-down** on the left, select the **adk_mcp_server**.

- Prompt the agent with the following:

Load the content from http://example.com.

Copied!

**Output:**

What happens here:

- The ADK agent (web_reader_mcp_client_agent) uses the MCPToolset to connect to your adk_server.py.

- The MCP server receives the call_tool request, executes the ADK load_web_page tool, and returns the result.

- The ADK agent then relays this information. You should see logs from both the ADK Web UI (and its terminal) and from your adk_server.py terminal in the Cloud Shell terminal tab where it is running.

This demonstrates that ADK tools can be encapsulated within an MCP server, making them accessible to a broad range of MCP-compliant clients, including ADK agents.

**Congratulations!**

In this lab, you learned how to integrate external Model Context Protocol (MCP) tools into your Agent Development Kit (ADK) agents using the MCPToolset class. You discovered how to connect to an MCP server, use its tools within your agent, and expose ADK tools like load_web_page through a custom MCP server. These skills enable you to extend your ADK agents with powerful, external services, enhancing your web development workflows.

**Manual Last Updated March 16, 2026**

**Lab Last Tested March 16, 2026**

Copyright 2026 Google LLC. All rights reserved. Google and the Google logo are trademarks of Google LLC. All other company and product names may be trademarks of the respective companies with which they are associated.