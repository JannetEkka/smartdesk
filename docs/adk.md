# ADK (Agent Development Kit) — Reference Guide

> Consolidated from Track 1 codelabs: Building AI Agents with ADK, Build & Deploy ADK Agent on Cloud Run, Connect to Remote Agents with A2A SDK

---

## Track 1 Overview

**Track 1- Build and deploy AI agents using Gemini, ADK, and Cloud Run**

**Track focus**

This track focuses on designing, building, and deploying production-ready AI agents using Gemini and the Agent Development Kit (ADK). Participants learn how to move from prototypes to scalable, serverless AI agents running on Cloud Run.

**Hands-on Codelabs**

Build and deploy an ADK agent on Cloud Run

Codelabs 1: [Build and deploy an ADK agent on Cloud Run | Google Codelabs](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)
Codelabs 2: [Building AI Agents with ADK: The Foundation | Google Codelabs](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation?hl=en)

Overview

This lab focuses on the implementation and deployment of a client agent service. You will use the Agent Development Kit (ADK) to build an AI agent that uses tools.

**What you'll learn**

- How to structure a Python project for ADK deployment.

- How to implement a tool-using agent with Google-ADK.

- How to deploy a Python application as a serverless container to Cloud Run.

- How to configure secure, service-to-service authentication using IAM roles. 

How to delete Cloud resources to avoid incurring future costs.

**Google Skills Lab (Optional)**
Connect to Remote Agents with ADK and the Agent2Agent (A2A) SDK

Google Skills Lab: [Connect to Remote Agents with ADK and the Agent2Agent (A2A) SDK](https://www.skills.google/focuses/132170?catalog_rank=%7B%22rank%22:3,%22num_filters%22:0,%22has_search%22:true%7D&parent=catalog&search_id=59958757)

In this lab, you learn how to:

- Deploy an ADK agent as an A2A Server.

- Prepare a JSON Agent Card to describe an A2A agent's capabilities.

- Enable another ADK agent to read the Agent Card of your deployed A2A agent and use it as a sub-agent.

**Project Submission**

**Problem Statement**

Build and deploy a **single AI agent** using **ADK and Gemini** that is hosted on **Cloud Run** and performs **one clearly defined task**.
The agent must be callable via an HTTP endpoint and return a valid response for a given input.

This is a **mini project** focused on **agent structure and deployment**, not complex logic.

**What You Must Build**

You must build **one AI agent** that:

- Is implemented using **ADK**

- Uses a **Gemini model** for inference

- Performs **one simple capability**, such as:

- Text summarization

- Question answering over a prompt

- Classification of input text

- Routing a request to a fixed response logic

- Accepts an input request and returns a response

We will take the cloud run link as submission, along with the repository if applicable.

---

## Codelab 1: Building AI Agents with ADK — The Foundation

Building AI Agents with ADK:

The Foundation

About this codelab

subjectLast updated Oct 31, 2025

account_circleWritten by Thu Ya Kyaw

[1. Before you begin](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation?hl=en)

**PLEASE READ:**

This tutorial requires a Google Cloud Project with **an active billing account**.

**For In-Person Workshop Attendees**

- Follow the specific setup and billing instructions provided by your instructor.

**For Self-Study Users**

- Follow these steps to redeem a trial:

- Open an Incognito Window in your browser.

- Navigate to [this redemption portal](https://trygcp.dev/claim/adk-foundation-31aug).

- Log in using your **personal ****gmail**** account.**

- Follow the step by step instructions from the portal.

Welcome to the first part of the "Building AI Agents with ADK" series! In this hands-on codelab series, you'll embark on an exciting journey to create your very own intelligent AI agent using Google's Agent Development Kit (ADK).

We'll start with the absolute essentials, guiding you through setting up your development environment and crafting a foundational conversational agent. By the end of this codelab, you'll have built your first interactive AI, ready to be expanded upon in subsequent parts of this series as we transform it into a sophisticated Multi-Agent System (MAS).

You can complete this codelab in either your local environment or on Google Cloud. For the most consistent experience, we recommend using the [Cloud Shell](https://cloud.google.com/shell/docs) from Google Cloud environment. Cloud Shell also provides 5 GB of persistent storage in the $HOME directory. This is useful to store scripts, configuration files, or cloned repositories.

You can also access this codelab via this shortened URL: goo.gle/adk-foundation.

**Note:** If you choose to work locally, you may require additional setup, installation, and authentication steps, which are not covered by the environment setup section of this lab.

**Prerequisites**

- An understanding of the [Generative AI concepts](https://www.cloudskillsboost.google/course_templates/536)

- A basic proficiency in [Python programming](https://docs.python.org/3/tutorial/index.html)

- Familiarity with [command line / terminal](https://www.youtube.com/watch?v=uwAqEzhyjtw)

**What you'll learn**

- How to set up a Python environment

- How to create a simple Personal Assistant Agent using ADK

- How to run, test, and debug the agent

**What you'll need**

- A working computer and reliable wifi

- A browser, such as [Chrome](https://www.google.com/chrome/), to access [Google Cloud Console](http://console.cloud.google.com/)

- A curious mind and eagerness to learn

## [**2. Introduction**](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation?hl=en)

The world of Generative AI (GenAI) is evolving rapidly, and AI Agents are currently a hot topic. An AI agent is a smart computer program designed to act on your behalf, much like a personal assistant. It can perceive its digital environment, make decisions, and take actions to achieve specific goals without direct human control. Think of it as a proactive, autonomous entity that can learn and adapt to get things done.

At its core, an AI agent uses a large language model (LLM) as its "brain" to understand and reason. This allows it to process information from various sources, such as text, images, and sounds. The agent then uses this understanding to create a plan and execute a series of tasks to reach a predefined objective.

You can now easily build your own AI agents, even without deep expertise, due to ready-to-use frameworks like the [Agent Development Kit](https://google.github.io/adk-docs/) (ADK). We will start this journey by constructing a personal assistant agent to help you with your tasks. Let's begin!

[3. Configure Google Cloud Services](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation?hl=en)

**Create a Google Cloud project**

Begin by creating a new Google Cloud project so that the activities from this codelab are isolated within this new project only.

- Navigate to [console.cloud.google.com/projectcreate](https://console.cloud.google.com/projectcreate)

- Enter the required information:

- **Project name** - you can input any name you desired (e.g. genai-workshop)

- **Location -** leave it as **No Organization**

- **Billing account** - If you see this option, select **Google Cloud Platform Trial Billing Account**. Don't worry if you don't see this option. Just proceed to the next step.

- Copy down the generated **Project ID**, you will need it later.

- If everything is fine, click on **Create** button

**Configure Cloud Shell**

Once your project is created successfully, do the following steps to set up **Cloud Shell**.

**1. Launch Cloud Shell**

Navigate to [shell.cloud.google.com](https://shell.cloud.google.com/) and if you see a popup asking you to authorize, click on **Authorize**.

**2. Set Project ID**

Execute the following command in the Cloud Shell terminal to set the correct **Project ID**. Replace <your-project-id> with your actual Project ID copied from the project creation step above.

gcloud config set project <your-project-id>

You should now see that the correct project is selected within the Cloud Shell terminal. The selected Project ID is highlighted in yellow.

3. Enable required APIs

To use Google Cloud services, you must first activate their respective APIs for your project. Run the commands below in the **Cloud Shell terminal** to enable the services for this Codelab:

gcloud services enable aiplatform.googleapis.com

If the operation was successful, you'll see Operation/... finished successfully printed in your terminal.

[4. Create a Python virtual environment](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation?hl=en)

Before starting any Python project, it's good practice to create a virtual environment. This isolates the project's dependencies, preventing conflicts with other projects or the system's global Python packages.

**Note:** We'll be using uv to create our virtual environment instead of the standard venv package. It's an incredibly fast Python package and project manager written in Rust.

If you're interested, you can learn more about it in the official uv documentation.

**1. Create project directory and navigate into it:**

mkdir ai-agents-adk
cd ai-agents-adk

**2. Create and activate a virtual environment:**

uv venv --python 3.12
source .venv/bin/activate

You'll see (ai-agents-adk) prefixing your terminal prompt, indicating the virtual environment is active.

**3. Install ****adk**** page**

uv pip install google-adk

**Note:** If you accidentally close the terminal, you will need to go into ai-agents-adk folder and execute source .venv/bin/activate again.

[5. Create an agent](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation?hl=en)

With your environment ready, it's time to create your AI agent's foundation. ADK requires a few files to define your agent's logic and configuration:

- agent.py: Contains your agent's primary Python code, defining its name, the LLM it uses, and core instructions.

- __init__.py: Marks the directory as a Python package, helping ADK discover and load your agent definition.

- .env: Stores sensitive information and configuration variables like API key, Project ID, and location.

This command will create a new directory named personal_assistant containing the three essential files.

adk create personal_assistant

Once the command is executed, you will be asked to choose a few options to configure your agent.

For the first step, choose **option 1** to use the gemini-2.5-flash model, a fast and efficient model perfect for conversational tasks.

Choose a model for the root agent:

1. gemini-2.5-flash

2. Other models (fill later)

Choose model (1, 2): 1

For the second step, choose **Vertex AI (option 2)**, Google Cloud's powerful, managed AI platform, as the backend service provider.

1. Google AI

2. Vertex AI

Choose a backend (1, 2): 2

After that, you need to verify that the Project ID shown in the brackets [...] is set correctly. If it is, **press Enter**. If not, key in the correct Project ID in the following prompt:

Enter Google Cloud project ID [your-project-id]:

Finally, **press Enter** at the next question, to use us-central1 as the region for this codelab.

Enter Google Cloud region [us-central1]:

You should see a similar output in your terminal.

Agent created in /home/<your-username>/ai-agent-adk/personal_assistant:

- .env

- __init__.py

- agent.py

[6. Explore agent codes](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation?hl=en)

To view the created files, open the ai-agents-adk folder in the Cloud Shell Editor.

- Click **File ****>**** Open Folder...** in the top menu.

- Find and select the ai-agents-adk folder

- Click **OK**.

If the top menu bar doesn't appear for you, you can also click on the folders icon and choose **Open Folder.**

**Note:** You're welcome to use a command-line editor like **Vim**, but you'll need to know the commands to **exit Vim** on your own.

Once the Editor window is fully loaded, navigate to the **personal-assistant** folder. You will see the necessary files as mentioned above (agent.py, __init__.py, and .env).

The .env file is often hidden by default. To make it visible in the **Cloud Shell Editor**:

- go to the menu bar at the top,

- click on **View**, and

- select **Toggle Hidden Files**.

Explore the content of each file.

**agent.py**

This file instantiates your agent using the Agent class from the google.adk.agents library.

from google.adk.agents import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)

- from google.adk.agents import Agent: This line imports the necessary Agent class from the ADK library.

- root_agent = Agent(...): Here, you're creating an instance of your AI agent.

- name="root_agent": A unique identifier for your agent. This is how ADK will recognize and refer to your agent.

- model="gemini-2.5-flash": This crucial parameter specifies which Large Language Model (LLM) your agent will use as its underlying "brain" for understanding, reasoning, and generating responses. gemini-2.5-flash is a fast and efficient model suitable for conversational tasks.

- description="...": This provides a concise summary of the agent's purpose or capabilities. The description is more for human understanding or for other agents in a multi-agent system to understand what this particular agent does. It's often used for logging, debugging, or when displaying information about the agent.

- instruction="...": This is the system prompt that guides your agent's behavior and defines its persona. It tells the LLM how it should act and what its primary purpose is. In this case, it establishes the agent as a "helpful assistant." This instruction is key to shaping the agent's conversational style and capabilities.

**init.py**

This file is necessary for Python to recognize personal-assistant as a package, allowing ADK to correctly import your agent.py file.

from . import agent

- from . import agent: This line performs a relative import, telling Python to look for a module named agent (which corresponds to agent.py) within the current package (personal-assistant). This simple line ensures that when ADK tries to load your personal-assistant agent, it can find and initialize the root_agent defined in agent.py. Even if empty, the presence of __init__.py is what makes the directory a Python package.

**.env**

This file holds environment-specific configurations and sensitive credentials.

GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=YOUR_PROJECT_LOCATION

- GOOGLE_GENAI_USE_VERTEXAI: This tells the ADK that you intend to use Google's Vertex AI service for your Generative AI operations. This is important for leveraging Google Cloud's managed services and advanced models.

- GOOGLE_CLOUD_PROJECT: This variable will hold the unique identifier of your Google Cloud Project. ADK needs this to correctly associate your agent with your cloud resources and to enable billing.

- GOOGLE_CLOUD_LOCATION: This specifies the Google Cloud region where your Vertex AI resources are located (e.g., us-central1). Using the correct location ensures your agent can communicate effectively with the Vertex AI services in that region.

[7. Run the agent on the Terminal](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation?hl=en)

With all three files in place, you're ready to run the agent directly from the terminal. To do this, run the following adk run command in the terminal:

adk run personal_assistant

If everything's set up correctly, you'll see similar output in your terminal. Don't worry about the warnings for now, as long as you see [user]: you are good to proceed.

...

Running agent personal_assistant, type exit to exit.

[user]: 

...

Go ahead and chat with the agent! Type something like **"hello. What can you do for me?"** and you should get back a reply.

...

Running agent personal_assistant, type exit to exit.

[user]: hello. What can you do for me?

[personal_assistant]: Hello! I am a large language model, trained by Google. I can do many things to help you, such as:

...

You'll notice the output is sometimes formatted with Markdown, which can be difficult to read in the terminal. In the next step, we'll use the Development UI for a much richer, chat-application-like experience.

**Troubleshooting**

**This API method requires billing to be enabled**

If you receive a message saying {‘message': ‘This API method requires billing to be enabled'}, do the following:

- Check if you are using the correct Project ID in .env file

- Go to [linked billing account](https://console.cloud.google.com/billing/linkedaccount) page and see if the billing account is already linked

- If not, choose **Google Cloud Platform Trial Biling Account** from the option

**Vertex AI API has not been used in project**

If you receive an error message containing {'message': 'Vertex AI API has not been used in project...'}, enable the Vertex AI API by typing this in the terminal:

gcloud services enable aiplatform.googleapis.com

If the operation was successful, you'll see Operation/... finished successfully printed in your terminal.

**Other Errors**

If you receive any other errors that are not mentioned above, try reloading the **Cloud Shell** tab in the browser (and reauthorize if prompted).

[8. Run the agent on the Development Web UI](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation?hl=en)

The Agent Development Kit also offers a convenient way to launch your agent as a chat application using its development UI. Simply use the command adk web instead of adk run.

If your terminal is still running **adk**** run**, type exit to close it before typing this command:

adk web

You should see a similar output in the terminal:

...

INFO:     Started server process [4978]

INFO:     Waiting for application startup.

+------------------------------------------------------+

| ADK Web Server started                               |

|                                                      |

| For local testing, access at http://localhost:8000.  |

+------------------------------------------------------+

INFO:     Application startup complete.

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

You have **two options** to access the development UI:

- Open via **Terminal**

- **Ctrl + Click** or **Cmd**** + Click** on the link (e.g., http://localhost:8000) as shown in the terminal.

- Open via **Web Preview**

- Click the **Web Preview** button,

- Select **Change Port**.

- Enter the port number (e.g., **8000**)

- Click **Change and Preview**

You'll then see the chat application-like UI appear in your browser. Go ahead and chat with your personal assistant through this interface!

You'll notice that Markdown formatting now displays correctly, and this UI also lets you debug and investigate each messaging event, the agent's state, user requests, and much more. Happy chatting!

[9. Clean Up (Optional)](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation?hl=en)

Note: You **don't need to do this step** if you are planning to continue with the series. If you are attending this codelab in person with an instructor, your instructor will provide further instruction on what to do.

Since this codelab doesn't involve any long-running products, simply stopping your active agent sessions (e.g., the adk web instance in your terminal) by pressing **Ctrl + C or ****Cmd**** + C** in the terminal is sufficient.

**Delete Agent Project Folders and Files**

If you only want to remove the code from your Cloud Shell environment, use the following commands:

cd ~
rm -rf ai-agents-adk

**Disable Vertex AI API**

To disable the Vertex AI API that was enabled earlier, run this command:

gcloud services disable aiplatform.googleapis.com

Shut Down the Entire Google Cloud Project

If you wish to fully shut down your Google Cloud project, refer to the [official guide](https://cloud.google.com/resource-manager/docs/creating-managing-projects) for detailed instructions.

[10. Conclusion](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-foundation?hl=en)

Congratulations! You've successfully built a simple personal assistant agent using the Agent Development Kit (ADK). You now have a solid foundation and understanding of the core components of an ADK agent.

As a next step, you can expand your agent's capabilities significantly by giving it tools to access real-time information and interact with external services. If you'd like to continue your journey, the next codelab in this series, [Building AI Agents with ADK: Empowering with Tools](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-empowering-with-tools), will guide you through this process.

---

## Codelab 2: Build and Deploy an ADK Agent on Cloud Run

Build and deploy an ADK agent on Cloud Run

About this codelab

subjectLast updated Feb 18, 2026

account_circleWritten by Smitha Kolan

[1. Introduction](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

This lab focuses on the implementation and deployment of a client agent service. You will use [Agent Development Kit (ADK)](https://google.github.io/adk-docs/) to build an [AI agent](https://cloud.google.com/discover/what-are-ai-agents?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab) that uses tools.

In this lab, we are building a zoo agent that uses wikipedia to answer questions about animals.

Finally, we'll deploy the tour guide agent to Google [Cloud Run](https://cloud.google.com/run?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab), rather than just running locally.

Prerequisites

- A Google Cloud project with billing enabled.

What you'll learn

- How to structure a Python project for [ADK](https://google.github.io/adk-docs/) deployment.

- How to implement a tool-using agent with google-adk.

- How to deploy a Python application as a serverless container to [Cloud Run](https://cloud.google.com/run?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab).

- How to configure secure, service-to-service authentication using [IAM roles](https://cloud.google.com/sdk/gcloud/reference/iam/roles?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab).

- How to delete Cloud resources to avoid incurring future costs.

What you'll need

- A Google Cloud Account and Google Cloud Project

- A web browser such as [Chrome](https://www.google.com/chrome/)

[2. Why deploy to Cloud Run?](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

[Cloud Run](https://cloud.google.com/run?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab) is a great choice for hosting [ADK](https://google.github.io/adk-docs/) agents because it's a serverless platform, which means you can focus on your code and not on managing the underlying infrastructure. We handle the operational work for you.

Think of it like a pop-up shop: it only opens and uses resources when customers (requests) arrive. When there are no customers, it closes down completely, and you don't pay for an empty store.

Key Features

Runs Containers Anywhere:

- You bring a container (Docker image) that has your app inside.

- Cloud Run runs it on Google's infrastructure.

- No OS patching, VM setup, or scaling headaches.

Automatic Scaling:

- If 0 people are using your app → 0 instances run (scales down to zero instance which is cost effective).

- If 1000 requests hit it → it spins up as many copies as needed.

Stateless by Default:

- Each request could go to a different instance.

- If you need to store state, use an external service like Cloud SQL, Firestore, or Memorystore.

Supports Any Language or Framework:

- As long as it runs in a Linux container, Cloud Run doesn't care if it's Python, Go, Node.js, Java, or .Net.

Pay for What You Use:

- [Request-based billing](https://cloud.google.com/run/docs/overview/what-is-cloud-run): Billed per request + compute time (down to 100 ms).

- [Instance-based billing](https://cloud.google.com/run/docs/overview/what-is-cloud-run): Billed for full instance lifetime (no per-request fee).

[3. Project setup](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

Google Account

If you don't already have a personal Google Account, you must [create a Google Account](https://accounts.google.com/SignUp).

**Use a personal account** instead of a work or school account.

Work and school accounts may have restrictions that prevent you from enabling the APIs needed for this lab.

Sign-in to the Google Cloud Console

Sign-in to the [Google Cloud Console](https://console.cloud.google.com/) using a personal Google account.

Enable Billing

Set up a personal billing account

*If you set up billing using Google Cloud credits, you can skip this step.*

To set up a personal billing account, [go here to enable billing](https://console.cloud.google.com/billing) in the Cloud Console.

Some Notes:

- Completing this lab should cost less than $1 USD in Cloud resources.

- You can follow the steps at the end of this lab to delete resources to avoid further charges.

- New users are eligible for the [$300 USD Free Trial](http://cloud.google.com/free).

Create a project (optional)

If you do not have a current project you'd like to use for this lab, [create a new project here](https://console.cloud.google.com/projectcreate).

[4. Open Cloud Shell Editor](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

- Click this link to navigate directly to [Cloud Shell Editor](https://ide.cloud.google.com/)

- If prompted to authorize at any point today, click **Authorize** to continue.

- If the terminal doesn't appear at the bottom of the screen, open it:

- Click **View**

- Click **Terminal**

[5. Set your project](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

- In the terminal, set your project with this command:

gcloud config set project [PROJECT_ID]

Example: gcloud config set project lab-project-id-example

If you can't remember your project ID, you can list all your project IDs with: gcloud projects list

- You should see this message:

	- Updated property [core/project].

If you see a WARNING and are asked Do you want to continue (Y/n)?, then you have likely entered the project ID incorrectly. Press n, press Enter, and try to run the gcloud config set project command again.

[6. Enable APIs](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

To use [Cloud Run](https://cloud.google.com/run?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab), [Artifact Registry](https://docs.cloud.google.com/artifact-registry?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab), [Cloud Build](https://cloud.google.com/build?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab), [Vertex AI](https://cloud.google.com/vertex-ai?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab), and [Compute Engine](https://cloud.google.com/products/compute?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab), you need to enable their respective APIs in your Google Cloud project.

- In the **terminal**, enable the APIs:

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com

When this finishes running, you should see an output like the following:

Operation "operations/acat.p2-[GUID]" finished successfully.

Introducing the APIs

- **Cloud Run Admin API** (run.googleapis.com) allows you to run frontend and backend services, batch jobs, or websites in a fully managed environment. It handles the infrastructure for deploying and scaling your containerized applications.

- **Artifact Registry API** (artifactregistry.googleapis.com) provides a secure, private repository to store your container images. It is the evolution of Container Registry and integrates seamlessly with Cloud Run and Cloud Build.

- **Cloud Build API** (cloudbuild.googleapis.com) is a serverless CI/CD platform that executes your builds on Google Cloud infrastructure. It is used to build your container image in the cloud from your Dockerfile.

- **Vertex AI API** (aiplatform.googleapis.com) enables your deployed application to communicate with [Gemini models](https://ai.google.dev/gemini-api/docs/models?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab) to perform core AI tasks. It provides the unified API for all of Google Cloud's AI services.

- **Compute Engine API** (compute.googleapis.com) provides secure and customizable virtual machines that run on Google's infrastructure. While Cloud Run is managed, the Compute Engine API is often required as a foundational dependency for various networking and compute resources.

[7. Prepare your development environment](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

Create the directory

- In the **terminal**, create the project directory and the necessary subdirectories:

cd && mkdir zoo_guide_agent && cd zoo_guide_agent

- In the terminal, run the following command to open the zoo_guide_agent directory in the Cloud Shell Editor explorer:

cloudshell open-workspace ~/zoo_guide_agent

- The explorer panel on the left will refresh. You should now see the directory you created.

**If the terminal disappears** when you do this, you can reopen it by clicking **View** and then **Terminal** in the top menu.

Install requirements

- Run the following command in the **terminal** to create the requirements.txt file.

cloudshell edit requirements.txt

- Add the following into the newly created requirements.txt file

google-adk==1.14.0
langchain-community==0.3.27
wikipedia==1.4.0

- In the **terminal**, create and activate a virtual environment using uv. This ensures your project dependencies don't conflict with the system Python.

uv venv
source .venv/bin/activate

**Note**: If your Cloud Shell session refreshes or you open a new terminal tab, you may need to reactivate the virtual environment by running source .venv/bin/activate.

- Install the required packages into your virtual environment in the **terminal**.

uv pip install -r requirements.txt

Set up environment variables

- Use the following command in the **terminal** to create the .env file.

# 1. Set the variables in your terminal first
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SA_NAME=lab2-cr-service

# 2. Create the .env file using those variables
cat <<EOF > .env
PROJECT_ID=$PROJECT_ID
PROJECT_NUMBER=$PROJECT_NUMBER
SA_NAME=$SA_NAME
SERVICE_ACCOUNT=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
MODEL="gemini-2.5-flash"
EOF

**Check the **.env** file** and make sure both PROJECT_ID, PROJECT_NUMBER, and SERVICE_ACCOUNT have been assigned values. If project details are missing, find them by running gcloud projects list. If the service account is missing, you can list the accounts in your project to find the email address (it should end in .iam.gserviceaccount.com) by running: gcloud iam service-accounts list.

[8. Create Agent Workflow](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

Create __init__.py file

- Create the **init**.py file by running the following in the **terminal**:

cloudshell edit __init__.py

This file tells Python that the zoo_guide_agent directory is a package.

- Add the following code to the new __init__.py file:

from . import agent

Create the agent.py file

- Create the main agent.py file by pasting the following command into the **terminal**.

cloudshell edit agent.py

- **Imports and Initial Setup**: Add the following code to your currently empty agent.py file:

import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

import google.auth
import google.auth.transport.requests
import google.oauth2.id_token

# --- Setup Logging and Environment ---

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")

This first block of the agent.py file brings in all the necessary libraries from the [ADK](https://google.github.io/adk-docs/) and Google Cloud. It also sets up logging and loads the environment variables from your .env file, which is crucial for accessing your model and server URL.

- **Define the tools**: An agent is only as good as the tools it can use. Add the following code to the bottom of agent.py to define the tools:

# Greet user and save their prompt

def add_prompt_to_state(
    tool_context: ToolContext, prompt: str
) -> dict[str, str]:
    """Saves the user's initial prompt to the state."""
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] Added to PROMPT: {prompt}")
    return {"status": "success"}

# Configuring the Wikipedia Tool
wikipedia_tool = LangchainTool(
    tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
)

**The Tools Explained**

- add_prompt_to_state 📝: This tool remembers what a zoo visitor asks. When a visitor asks, "Where are the lions?", this tool saves that specific question into the agent's memory so the other agents in the workflow know what to research.
**How:** It's a Python function that writes the visitor's prompt into the shared tool_context.state dictionary. This tool context represents the agent's short-term memory for a single conversation. Data saved to the state by one agent can be read by the next agent in the workflow.

- LangchainTool 🌍: This gives the tour guide agent general world knowledge. When a visitor asks a question that isn't in the zoo's database, like "What do lions eat in the wild?", this tool lets the agent look up the answer on Wikipedia.
**How:** It acts as an adapter, allowing our agent to use the pre-built WikipediaQueryRun tool from the LangChain library.

- **Define the Specialist agents**: Add the following code to the bottom of agent.py to define the comprehensive_researcher and response_formatter agents:

# 1. Researcher Agent
comprehensive_researcher = Agent(
    name="comprehensive_researcher",
    model=model_name,
    description="The primary researcher that can access both internal zoo data and external knowledge from Wikipedia.",
    instruction="""
    You are a helpful research assistant. Your goal is to fully answer the user's PROMPT.
    You have access to two tools:
    1. A tool for getting specific data about animals AT OUR ZOO (names, ages, locations).
    2. A tool for searching Wikipedia for general knowledge (facts, lifespan, diet, habitat).

    First, analyze the user's PROMPT.
    - If the prompt can be answered by only one tool, use that tool.
    - If the prompt is complex and requires information from both the zoo's database AND Wikipedia,
      you MUST use both tools to gather all necessary information.
    - Synthesize the results from the tool(s) you use into preliminary data outputs.

    PROMPT:
    { PROMPT }
    """,
    tools=[
        wikipedia_tool
    ],
    output_key="research_data" # A key to store the combined findings
)

# 2. Response Formatter Agent
response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Synthesizes all information into a friendly, readable response.",
    instruction="""
    You are the friendly voice of the Zoo Tour Guide. Your task is to take the
    RESEARCH_DATA and present it to the user in a complete and helpful answer.

    - First, present the specific information from the zoo (like names, ages, and where to find them).
    - Then, add the interesting general facts from the research.
    - If some information is missing, just present the information you have.
    - Be conversational and engaging.

    RESEARCH_DATA:
    { research_data }
    """
)

- The comprehensive_researcher agent is the "brain" of our operation. It takes the user's prompt from the shared State, examines it's the Wikipedia Tool, and decides which ones to use to find the answer.

- The response_formatter agent's role is presentation. It takes the raw data gathered by the Researcher agent (passed via the State) and uses the LLM's language skills to transform it into a friendly, conversational response.

- **Define the Workflow agent**: Add this block of code to the bottom of agent.py to define the sequential agent tour_guide_workflow:

tour_guide_workflow = SequentialAgent(
    name="tour_guide_workflow",
    description="The main workflow for handling a user's request about an animal.",
    sub_agents=[
        comprehensive_researcher, # Step 1: Gather all data
        response_formatter,       # Step 2: Format the final response
    ]
)

The workflow agent acts as the ‘back-office' manager for the zoo tour. It takes the research request and ensures the two agents we defined above perform their jobs in the correct order: first research, then formatting. This creates a predictable and reliable process for answering a visitor's question.
**How:** It's a SequentialAgent, a special type of agent that doesn't think for itself. Its only job is to run a list of sub_agents (the researcher and formatter) in a fixed sequence, automatically passing the shared memory from one to the next.

- **Assemble the main workflow**: Add this final block of code to the bottom of agent.py to define the root_agent:

root_agent = Agent(
    name="greeter",
    model=model_name,
    description="The main entry point for the Zoo Tour Guide.",
    instruction="""
    - Let the user know you will help them learn about the animals we have in the zoo.
    - When the user responds, use the 'add_prompt_to_state' tool to save their response.
    After using the tool, transfer control to the 'tour_guide_workflow' agent.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[tour_guide_workflow]
)

The [ADK](https://google.github.io/adk-docs/) framework uses the root_agent as the starting point for all new conversations. Its primary role is to orchestrate the overall process. It acts as the initial controller, managing the first turn of the conversation.

The full agent.py file

Your agent.py file is now complete! By building it this way, you can see how each component—tools, worker agents, and manager agents—has a specific role in creating the final, intelligent system.

The complete file should look like this:

import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

import google.auth
import google.auth.transport.requests
import google.oauth2.id_token

# --- Setup Logging and Environment ---

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")

# Greet user and save their prompt

def add_prompt_to_state(
    tool_context: ToolContext, prompt: str
) -> dict[str, str]:
    """Saves the user's initial prompt to the state."""
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] Added to PROMPT: {prompt}")
    return {"status": "success"}

# Configuring the Wikipedia Tool
wikipedia_tool = LangchainTool(
    tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
)

# 1. Researcher Agent
comprehensive_researcher = Agent(
    name="comprehensive_researcher",
    model=model_name,
    description="The primary researcher that can access both internal zoo data and external knowledge from Wikipedia.",
    instruction="""
    You are a helpful research assistant. Your goal is to fully answer the user's PROMPT.
    You have access to two tools:
    1. A tool for getting specific data about animals AT OUR ZOO (names, ages, locations).
    2. A tool for searching Wikipedia for general knowledge (facts, lifespan, diet, habitat).

    First, analyze the user's PROMPT.
    - If the prompt can be answered by only one tool, use that tool.
    - If the prompt is complex and requires information from both the zoo's database AND Wikipedia,
        you MUST use both tools to gather all necessary information.
    - Synthesize the results from the tool(s) you use into preliminary data outputs.

    PROMPT:
    { PROMPT }
    """,
    tools=[
        wikipedia_tool
    ],
    output_key="research_data" # A key to store the combined findings
)

# 2. Response Formatter Agent
response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Synthesizes all information into a friendly, readable response.",
    instruction="""
    You are the friendly voice of the Zoo Tour Guide. Your task is to take the
    RESEARCH_DATA and present it to the user in a complete and helpful answer.

    - First, present the specific information from the zoo (like names, ages, and where to find them).
    - Then, add the interesting general facts from the research.
    - If some information is missing, just present the information you have.
    - Be conversational and engaging.

    RESEARCH_DATA:
    { research_data }
    """
)

tour_guide_workflow = SequentialAgent(
    name="tour_guide_workflow",
    description="The main workflow for handling a user's request about an animal.",
    sub_agents=[
        comprehensive_researcher, # Step 1: Gather all data
        response_formatter,       # Step 2: Format the final response
    ]
)

root_agent = Agent(
    name="greeter",
    model=model_name,
    description="The main entry point for the Zoo Tour Guide.",
    instruction="""
    - Let the user know you will help them learn about the animals we have in the zoo.
    - When the user responds, use the 'add_prompt_to_state' tool to save their response.
    After using the tool, transfer control to the 'tour_guide_workflow' agent.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[tour_guide_workflow]
)

Next up, deployment!

[9. Prepare the application for deployment](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

Check the final structure

Before deploying, verify that your project directory contains the correct files.

- Ensure your zoo_guide_agent folder looks like this:

	- zoo_guide_agent/

	- ├── .env

	- ├── __init__.py

	- ├── agent.py

	- └── requirements.txt

Set up IAM permissions

With your local code ready, the next step is to set up the identity your agent will use in the cloud.

- In the **terminal**, load the variables into your shell session.

source .env

**Note:** If your Cloud Shell session refreshes or you open a new terminal tab, you may need to run source .env again to reload these variables.

- Create a dedicated [service account](https://docs.cloud.google.com/iam/docs/service-account-overview?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab) for your Cloud Run service so that it has its own specific permission. Paste the following into the **terminal**:

gcloud iam service-accounts create ${SA_NAME} \
    --display-name="Service Account for lab 2 "

By creating a dedicated identity for this specific application, you ensure the agent only has the exact permissions it needs, rather than using a default account with overly broad access.

- Grant the service account the Vertex AI User role, which gives it permission to call Google's models.

# Grant the "Vertex AI User" role to your service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"

[10. Deploy the agent using the ADK CLI](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

With your local code ready and your Google Cloud project prepared, it's time to deploy the agent. You will use the adk deploy cloud_run command, a convenient tool that automates the entire deployment workflow. This single command packages your code, builds a container image, pushes it to [Artifact Registry](https://docs.cloud.google.com/artifact-registry?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab), and launches the service on [Cloud Run](https://cloud.google.com/run?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab), making it accessible on the web.

- Run the following command in the **terminal** to deploy your agent.

# Run the deployment command
uvx --from google-adk==1.14.0 \
adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=europe-west1 \
  --service_name=zoo-tour-guide \
  --with_ui \
  . \
  -- \
  --labels=dev-tutorial=codelab-adk \
  --service-account=$SERVICE_ACCOUNT

The uvx command allows you to run command line tools published as Python packages without requiring a global installation of those tools.

**Note:** This deploy command below will take a few minutes to finish running.

- If you are prompted with the following:

	- Deploying from source requires an Artifact Registry Docker repository to store built containers. A repository named [cloud-run-source-deploy] in region 

	- [europe-west1] will be created.

	

	- Do you want to continue (Y/n)?

If so, Type Y and hit ENTER.

- If you are prompted with the following:

	- Allow unauthenticated invocations to [your-service-name] (y/N)?.

Type y and hit ENTER. This allows unauthenticated invocations for this lab for easy testing.

**Note:** Anyone with the URL will have access to this agent, so this is best for testing.

Upon successful execution, the command will provide the URL of the deployed Cloud Run service. (It will look something like https://zoo-tour-guide-123456789.europe-west1.run.app).

- Copy the URL of the deployed Cloud Run service for the next task.

[11. Test the deployed agent](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

With your agent now live on [Cloud Run](https://cloud.google.com/run?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab), you'll perform a test to confirm that the deployment was successful and the agent is working as expected. You'll use the public Service URL (something like https://zoo-tour-guide-123456789.europe-west1.run.app/) to access the ADK's web interface and interact with the agent.

- Open the public Cloud Run Service URL in your web browser. Because you used the --with_ui flag, you should see the ADK developer UI.

- Toggle on Token Streaming in the upper right.
You can now interact with the Zoo agent.

- Type hello and hit enter to begin a new conversation.

- Observe the result. The agent should respond quickly with its greeting, which will be something like this:

	- "Hello! I'm your Zoo Tour Guide. I can help you learn about the amazing animals we have here. What would you like to know or explore today?"

- Ask the agent questions like:

Where can I find the polar bears in the zoo and what is their diet?

 

Agent Flow Explained

Your system operates as an intelligent, [multi-agent team](https://cloud.google.com/discover/what-is-a-multi-agent-system?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab). The process is managed by a clear sequence to ensure a smooth and efficient flow from a user's question to the final, detailed answer.

1. The Zoo Greeter (The Welcome Desk)

The entire process begins with the greeter agent.

- **Its Job:** To start the conversation. Its instruction is to greet the user and ask what animal they would like to learn about.

- **Its Tool:** When the user replies, the Greeter uses its add_prompt_to_state tool to capture their exact words (e.g., "tell me about the lions") and save them in the system's memory.

- **The Handoff:** After saving the prompt, it immediately passes control to its sub-agent, the tour_guide_workflow.

2. The Comprehensive Researcher (The Super-Researcher)

This is the first step in the main workflow and the "brain" of the operation. Instead of a large team, you now have a single, highly-skilled agent that can access all the available information.

- **Its Job:** To analyze the user's question and form an intelligent plan. It uses the language model's tool use capability to decide if it needs:

- General knowledge from the web (via the Wikipedia API).

- Or, for complex questions, both.

3. The Response Formatter (The Presenter)

Once the Comprehensive Researcher has gathered all the facts, this is the final agent to run.

- **Its Job:** To act as the friendly voice of the Zoo Tour Guide. It takes the raw data (which could be from one or both sources) and polishes it.

- **Its Action:** It synthesizes all the information into a single, cohesive, and engaging answer. Following its instructions, it first presents the specific zoo information and then adds the interesting general facts.

- **The Final Result:** The text generated by this agent is the complete, detailed answer that the user sees in the chat window.

**If you interested in learning more about building Agents**, check out the following resources:

- [ADK docs](https://google.github.io/adk-docs/)

- [Building Custom Tools For ADK Agents](https://youtu.be/NiLb5DK4_rU?si=pTLljMihor0VJlNXv)

[12. Clean up environment](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

To avoid incurring charges to your Google Cloud account for the resources used in this tutorial, either delete the project that contains the resources, or keep the project and delete the individual resources.

Delete the Cloud Run services and images

If you wish to keep the Google Cloud project but remove the specific resources created in this lab, you must delete both the running service and the container image stored in the registry.

- Run the following commands in the **terminal**:

gcloud run services delete zoo-tour-guide --region=europe-west1 --quiet
gcloud artifacts repositories delete cloud-run-source-deploy --location=europe-west1 --quiet

Delete the project (Optional)

If you created a new project specifically for this lab and don't plan to use it again, the easiest way to clean up is to delete the entire project. This ensures all resources (including the Service Account and any hidden build artifacts) are completely removed.

- In the **terminal**, run the following command (replace [YOUR_PROJECT_ID] with your actual project ID)

gcloud projects delete $PROJECT_ID

**Deleting a project is irreversible.** Please ensure that this project is not being used for any other work before proceeding.

[13. Congratulations](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/5-deploying-agents/deploy-an-adk-agent-to-cloud-run)

You have successfully built and deployed a multi-agent AI application to Google Cloud!

Recap

In this lab, you went from an empty directory to a live, publicly accessible AI service. Here is a look at what you built:

- **You created a specialized team**: Instead of one generic AI, you built a "Researcher" to find facts and a "Formatter" to polish the answer.

- **You gave them tools**: You connected your agents to the outside world using the Wikipedia API.

- **You shipped it**: You took your local Python code and deployed it as a serverless container on [Cloud Run](https://cloud.google.com/run?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab), securing it with a dedicated Service Account.

What we've covered

- How to structure a Python project for deployment with the [ADK](https://google.github.io/adk-docs/).

- How to implement a [multi-agent workflow](https://cloud.google.com/discover/what-is-a-multi-agent-system?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab) using [SequentialAgent](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/).

- How to integrate external tools like the Wikipedia API.

- How to deploy an agent to [Cloud Run](https://cloud.google.com/run?utm_campaign=CDR_0x6e136736_default_b460751542&utm_medium=external&utm_source=lab) using the adk deploy command.

---

## Codelab 3 (Optional): Connect to Remote Agents with ADK and A2A SDK

Connect to Remote Agents with ADK and the Agent2Agent (A2A) SDK

experimentLabschedule1 houruniversal_currency_alt7 Creditsshow_chartAdvanced

infoThis lab may incorporate AI tools to support your learning.

**GENAI120**

**Overview**

The [Agent2Agent (A2A) protocol](https://a2a-protocol.org/) addresses a critical challenge in the AI landscape: enabling generative AI agents, built on diverse frameworks by different companies running on separate servers, to communicate and collaborate effectively – as agents, not just as tools. A2A aims to provide a common language for agents, fostering a more interconnected, powerful, and innovative AI ecosystem.

A2A is built around a few core concepts that make it powerful and flexible:

- **Standardized Communication:** JSON-RPC 2.0 over HTTP(S).

- **Agent Discovery:** Agent Cards detail an agent's capabilities and connection info, so agents can discover each other and learn about each other's capabilities

- **Rich Data Exchange:** Handles text, files, and structured JSON data.

- **Flexible Interaction:** Supports synchronous request/response, streaming (SSE), and asynchronous push notifications.

- **Enterprise-Readiness:** Designed with security, authentication, and observability in mind.

Objectives

In this lab, you learn how to perform the following tasks:

- Set up your environment and install the Agent Development Kit (ADK).

- Deploy an ADK agent as an A2A Server.

- Prepare a JSON Agent Card to describe an A2A agent's capabilities.

- Enable another ADK agent to read the Agent Card of your deployed A2A agent and use it as a sub-agent.

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

**Task 1. Install ADK and set up your environment**

In this lab environment, the **Vertex AI API** and **Cloud Run API** have been enabled for you. If you were to follow these steps in your own project, you would enable them by navigating to Vertex AI and following the prompt to enable it.

Prepare a Cloud Shell Editor tab

- With your Google Cloud console window selected, press G,S to open Cloud Shell. Alternatively, you can click the **Activate Cloud Shell** button () in the upper right of the Cloud console.

- Click **Continue**.

- When prompted to authorize Cloud Shell, click **Authorize**.

- In the upper-right corner of the Cloud Shell terminal panel, click the **Open in new window** button ().

- Click the **Open Editor** pencil icon () at the top of the pane to view files.

- At the top of the left-hand navigation menu, click the **Explorer** icon () to open your file explorer.

- Click the **Open Folder** button.

- In the Open Folder dialog that opens, click **OK** to select your student account's home folder.

- Close any additional tutorial or Gemini panels that appear on the right side of the screen to save more of your window for your code editor.

- Throughout the rest of this lab, you work in this window as your IDE with the Cloud Shell Editor and Cloud Shell terminal.

Download and install the ADK and code samples for this lab

- Download code for this lab and install the Agent Development Kit (ADK) and other requirements by running the following code in the Cloud Shell terminal:

- gcloud storage cp -r gs://YOUR_GCP_PROJECT_ID-bucket/* .

- export PATH=$PATH:"/home/${USER}/.local/bin"

python3 -m pip install --upgrade google-adk a2a-sdk google-genai

Copied!

Click **Check my progress** to verify the objective.

Install ADK and set up your environment.

**Task 2. Explore the ADK agent you plan to make available remotely**

For the purposes of this lab, imagine you work for a stadium maintenance company, **Cymbal Stadiums**. As part of a recent project, you developed an image generation agent that can create illustrations according to your brand guidelines. Now, several different teams in your organization want to use it too.

If you were to copy the code for use as a sub-agent by many agents, it would be very difficult to maintain and improve all of these copies.

Instead, you can deploy the agent once as an agent wrapped with an A2A server, and the other teams' agents can incorporate it by querying it remotely.

- In the Cloud Shell Editor's file explorer pane, navigate to the **adk_and_a2a/illustration_agent** directory. This directory contains the ADK agent you plan to make available remotely. Click the directory to toggle it open.

- Open the **agent.py** file on this directory and scroll to the section labeled # Tools.

- Notice the generate_image() function, which is used as a tool by this agent. It receives a prompt and performs a two-step process. First, it uses the **Google Gen AI SDK** to call generate_content(), which returns the raw image data directly in the response. Second, the function uses the **Cloud Storage library** to upload these image bytes to a Google Cloud Storage bucket. Finally, the tool returns a URL for the newly created image file.

- Notice that the instruction provided to the root_agent provides specific instructions to the agent to use image-generation prompts that respect the company's brand guidelines. For example, it specifies:

- a specific illustration style: ([Corporate Memphis](https://en.wikipedia.org/wiki/Corporate_Memphis))

- a color palette (purples and greens on sunset gradients)

- examples of stadium/sports and maintenance imagery because it is a stadium maintenance company

- To see it in action, you first need to write a **.env** file to set environment variables needed by ADK agents. Run the following in the Cloud Shell terminal to write this file in this directory.

- cd ~/adk_and_a2a

- cat << EOF > illustration_agent/.env

- GOOGLE_GENAI_USE_VERTEXAI=TRUE

- GOOGLE_CLOUD_PROJECT=YOUR_GCP_PROJECT_ID

- GOOGLE_CLOUD_LOCATION=global

- MODEL=gemini_flash_model_id

- IMAGE_MODEL=gemini_flash_image_model_id

EOF

Copied!

- Run the following to copy the .env to another agent directory you are using in this lab:

cp illustration_agent/.env slide_content_agent/.env

Copied!

- Now from the Cloud Shell terminal, launch the Agent Development Kit Dev UI with the following command:

adk web

Copied!

**Output**

INFO:     Started server process [2434]

INFO:     Waiting for application startup.

+-------------------------------------------------------+

| ADK Web Server started                                |

|                                                       |

| For local testing, access at http://localhost:8000.   |

+-------------------------------------------------------+

INFO:     Application startup complete.

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit) 

- To view the web interface in a new tab, click the **http://127.0.0.1:8000** link at the bottom of the terminal output.

- A new browser tab opens with the ADK Dev UI.

- In the ADK Dev UI tab, from the **Select an agent** drop-down on the left, select the **illustration_agent**.

- Prompt the agent with some text that could be used in a recruitment slide deck:

By supporting each other, we get big things done!

Copied!

- After about 10 seconds, the agent should respond with the prompt it generated and a URL to preview the image. **Click the image URL** to preview the image, then click **Back** in your browser to return to the Dev UI.

**Note:** If you get a **Forbidden Error 403**, you may have multiple accounts signed into your Incognito session. Try incrementing the value of the authuser value at the end of the URL, for example changing it from authuser=0 to authuser=1. authuser=2, etc. In production you could handle this with a service account creating a Signed URL.

**Example Output**

**Example Image**

- Notice that the prompt you provided to the agent didn't mention sports, stadiums, or maintenance work, but the agent took your text and the brand guidelines and combined them into a single prompt for the image generation model.

When you are finished exploring the base agent, close the browser tab.

- Return to the Cloud Shell terminal and press CTRL+C to stop the server.

Click **Check my progress** to verify the objective.

Explore the ADK agent.

**Task 3. Deploy the agent as an A2A Server**

In this task, you take the steps to deploy this agent as a remote A2A agent. An A2A Agent identifies itself and its capabilities by serving an [Agent Card](https://a2a-protocol.org/latest/topics/agent-discovery/).

- Run the following to create an **agent.json** file:

touch illustration_agent/agent.json

Copied!

- Open the **agent.json** file within the **adk_and_a2a/illustration_agent** directory and paste in the following contents:

- {

-     "name": "illustration_agent",

-     "description": "An agent designed to generate branded illustrations for Cymbal Stadiums.",

-     "defaultInputModes": ["text/plain"],

-     "defaultOutputModes": ["application/json"],

-     "skills": [

-     {

-         "id": "illustrate_text",

-         "name": "Illustrate Text",

-         "description": "Generate an illustration to illustrate the meaning of provided text.",

-         "tags": ["illustration", "image generation"]

-     }

-     ],

-     "url": "https://illustration-agent-Project Number.GCP_LOCATION.run.app/a2a/illustration_agent",

-     "capabilities": {},

-     "version": "1.0.0"

}

Copied!

- **Save** the file.

- Review the JSON in the **agent.json** file. Notice that it gives the agent a name and description and identifies some skills . It also indicates a url where the agent itself can be called.

The agent's url is constructed to be its Cloud Run service URL once you have deployed it following the instructions in this lab.

While similar in name to skills, the parameter capabilities here is reserved to indicate abilities like streaming.

- Run the following to create a **requirements.txt** file in the **illustration_agent** directory:

touch illustration_agent/requirements.txt

Copied!

- Open the **requirements.txt** file, and paste the following into the file:

- google-adk

a2a-sdk

Copied!

- **Save** the file.

- In the following command, you use adk deploy cloud_run with the --a2a flag to deploy your agent to Cloud Run as an A2A server:

- adk deploy cloud_run \

-     --project YOUR_GCP_PROJECT_ID \

-     --region GCP_LOCATION \

-     --service_name illustration-agent \

-     --a2a \

    illustration_agent

Copied!

You can learn more about deploying agents to Cloud Run by searching for the lab "Deploy ADK agents to Cloud Run". In this command:

- The --project and --region define the project and region in which your Cloud Run service will be deployed.

- The --service_name defines the name for the Cloud Run service.

- The --a2a flag indicates it should be hosted as an A2A agent. This means two things:

- Your agent will be wrapped by a class that bridges ADK and A2A agents, the [A2aAgentExecutor](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/executor/a2a_agent_executor.py). This class translates A2A Protocol's language of [tasks and messages](https://a2a-protocol.org/latest/topics/key-concepts/) to an ADK Runner in its language of [events](https://google.github.io/adk-docs/events/).

- The Agent Card will be hosted as well at CLOUD_RUN_URL/a2a/AGENT_NAME/.well-known/agent.json.

**Note:** While this version of the card will be usable soon, the dynamic rewriting of the agent's url currently does not work with Cloud Run, so we don't use it in this version of this lab.

- You are prompted to allow unauthenticated responses for this container. For the sake of lab testing, enter Y into the Cloud Shell terminal (for "yes") and press ENTER or RETURN.

**Note:** Deployment should take about 5-10 minutes. If you encounter a PERMISSION_DENIED error, try running the above command again.

**Expected output:**

You should see steps relating to building a Dockerfile and deploying the container, then deploying the service, followed by:

Service [illustration-agent] revision [illustration-agent-00001-xpp] has been deployed and is serving 100 percent of traffic.

Service URL: https://illustration-agent-Project Number.GCP_LOCATION.run.app

Click **Check my progress** to verify the objective.

Deploy the Agent as an A2A Server.

**Task 4. Enable another ADK agent to call this agent remotely**

In this task, you provide a second ADK agent the ability to identify your illustration agent's capabilities and call it remotely. This second agent is tasked with creating contents for slides. It must write a headline and a couple of sentences of body text, then transfer to the illustration agent to generate an image to illustrate that text.

- In the Cloud Shell terminal, run the following command to copy the Agent Card JSON file to your **adk_and_a2a** directory and change its name to indicate that it represents the **illustration_agent**:

cp illustration_agent/agent.json illustration-agent-card.json

Copied!

- In the Cloud Shell Editor's file explorer pane, navigate to the **adk_and_a2a/slide_content_agent** directory, and open the **agent.py** file.

Review this agent's instruction to see that it takes a user's suggestion for a slide, uses that to write a headline & body text, and then requests that your A2A agent provides an illustration for the slide.

- Paste the following code under the # Agents header in **line 24** to add the remote agent using the [RemoteA2aAgent](https://github.com/google/adk-python/blob/main/src/google/adk/agents/remote_a2a_agent.py) class from ADK:

- illustration_agent = RemoteA2aAgent(

-     name="illustration_agent",

-     description="Agent that generates illustrations.",

-     agent_card=(

-         "illustration-agent-card.json"

-     ),

)

Copied!

- Add the **illustration_agent** as a sub-agent of the **root_agent** by adding the following parameter to **line 43** in the same file:

sub_agents=[illustration_agent]

Copied!

- **Save** the file.

- Launch the UI from the Cloud Shell terminal with the following command:

- cd ~/adk_and_a2a

adk web

Copied!

- Once again, click the **http://127.0.0.1:8000** link in the terminal output to launch the ADK Dev UI.

- In the ADK Dev UI browser tab, from the **Select an agent** drop-down on the left, select the **slide_content_agent**.

- Prompt the agent with an idea for a slide as follows:

Create content for a slide about our excellent on-the-job training.

Copied!

You should see the following output:

- A headline and body text written by the **slide_content_agent** itself.

- A call to **transfer_to_agent**, indicating a transfer to the **illustration_agent**.

- The response from the **illustration_agent** with a link you can click on to see the new image.

**Note:** As before, if you get a **Forbidden Error 403**, you may have multiple accounts signed into your Incognito session. Try incrementing the value of the authuser value at the end of the URL, for example changing it from authuser=0 to authuser=1. authuser=2, etc. In production you could handle this with a service account creating a Signed URL.

**Expected output:**

Click **Check my progress** to verify the objective.

Enable another ADK agent to call the agent remotely.

**Congratulations!**

In this lab, you deployed an ADK agent as an A2A Server, prepared a JSON Agent Card to describe an A2A agent's capabilities, and enabled another ADK agent to read the Agent Card of your deployed A2A agent and use it as a sub-agent.