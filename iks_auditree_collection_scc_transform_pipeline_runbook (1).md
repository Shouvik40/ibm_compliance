Compliance Automation: How to setup IBM cloud toolchain pipelines for evidence collection and SCC facts generation

1. <a name="_overview"></a>[Overview](#_overview_1)
2. [Architecture Diagram](#_architecture_diagram)
3. [Prerequisites](#_prerequisites)
4. [Setup Data Collection Pipeline using Auditree Central](#_setup_data_collection)
    - [Create a Toolchain](#_create_a_toolchain_1)
    - [Add tool integrations](#_add_tool_integrations)
    - [GitHub Enterprise Whitewater](#_github_enterprise_whitewater)
    - [Delivery Pipeline Private Workers](#_delivery_pipeline_private)
    - [Configure Environment](#_configure_environment)
    - [Configure Slack](#_configure_slack)
    - [Delivery Pipeline](#_delivery_pipeline)
      - [Pipeline Definitions](#_pipeline_definitions)
      - [Worker](#_worker)
      - [Environment properties](#_environment_properties)
5. [Setup SCC Fact Generation Pipeline](#_pushing_data_to)
    - [Add tool integrations](#_add_integration_tool)
    - [Delivery Pipeline](#_delivery_pipeline_scc)
6. [Controls and Fetchers mapping](#_controls_and_fetchers_mapping)
7. [Help and References](#_help_and_references)
 
# <a name="_overview_1"></a><a name="_setup_auditree_pipeline"></a>1. Overview

This document is a complete guide to setting up an **Automation Pipeline** for **Compliance**. The pipeline helps collect evidence data using **Auditree fetchers**, which are tools that gather the necessary information for compliance checks. This collected data is then transformed into **SCC facts**, which are used by the **Security and Compliance Center (SCC)** to generate reports and provide information on how well certain standards and audit requirements are being met. 
### <a name="_access_ca_repo"></a>Key Details:
- The guide will use the term **"Tekton pipeline"** to refer to the **IBM Cloud Toolchain Delivery Pipeline** for simplicity.
- The **Auditree configuration** determines which fetchers (tools that collect data) and checks (rules or tests) are executed.
- Access tokens, credentials, and other necessary configuration settings are stored in the pipeline's **environment properties** to ensure secure and smooth operation.
- All the code needed to run this pipeline is already developed and stored in a repository called [iaas-scc-data-pipelines](https://github.ibm.com/ComplianceAutomation/iaas-scc-data-pipelines). This repository also includes some **default configurations** to make setup easier.

In simpler terms, this document guides you through setting up an automated system that will collect and process compliance-related data, then send it to the **SCC** for reporting. The tools and code are already prepared and stored in a specific repository, and this guide helps you configure and use them.


# <a name="_architecture_diagram"></a>2. Architecture Diagram

![A screenshot of a computer description automatically generated](images/001.jpeg)

# <a name="_prerequisites"></a>3. Prerequisites
### 3.1 <a name="_access_ca_repo"></a> Getting Access to the Repository

  To access the Automation Pipelines Repository [ComplianceAutomation -> iaas-scc-data-pipelines](https://github.ibm.com/ComplianceAutomation/iaas-scc-data-pipelines), follow these steps:
  - Go to [AccessHub Portal](https://ibm-support.saviyntcloud.com/) and log in.
  - Click on **"Request Access for Self"**
  - In the search bar, type **‘CA-Datalake’**
  - Select Role(Read access only)
  - Add appropriate justification
  - Submit request
    
These steps will give you access to the iaas-scc-data-pipelines repository, which contains the code needed to run the data collection and SCC fact generation pipelines.

### 3.2 <a name="_create_credentials"></a>Required Tokens and Credentials

  Before you can use the automation pipelines, you need to create and gather the following tokens and credentials:
  - **Artifactory Access Token:**
      - You'll need to create an Artifactory Access Token. For detailed steps on how to do this, check the guide on [**Creating an Access Token via the UI**](https://taas.cloud.ibm.com/guides/artifactory-authentication-access-tokens.md#creating-an-access-token-via-the-ui).
      - When you follow the steps, be sure to select [NA Artifactory](https://na.artifactory.swg-devops.com/ui/repos/tree/General) in step 1.
  - **GitHub Personal Access Token:**
    - If you haven’t already created a GitHub Personal Access Token, you need to do so. Follow the steps in this guide: [Create the Token](https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line).
  - **Other Required Credentials:**
    Depending on the [Auditree Central providers](https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider) you're using, you might need additional credentials:
    - For example, if you use xforce, you'll need an **xforce_key**.
    - If other providers are used, you might need **IBM API keys** for authentication.
These tokens and credentials are necessary for setting up and running the automation pipeline effectively. Make sure to create them before moving forward.
      
### 3.3 Create SCC Instance

Before setting up the **SCC (Security and Compliance Center)**, make sure you meet the following prerequisites:

#### 3.3.1 Getting Access

1. **Request Access for Audit Management**:
   - Ask the SCC team to **allowlist** your account for **Audit Management** access.
   - To request access, you can:
     - Create a ticket [**here**](https://github.ibm.com/project-fortress/scc-internal-adoption/issues/new?assignees=Ramesh-Kothandapany%2C+agiammar%2C+mark-duquette%2C+Ashwini-PC&labels=internal-compliance-onboarding&template=internal-compliance-onboarding.md&title=Internal+Compliance+Onboarding).
       - [(Sample ticket for reference)](https://github.ibm.com/project-fortress/scc-internal-adoption/issues/5)
     - Post your request in the [**#scc-adopters**](https://ibm.enterprise.slack.com/archives/C0116MQSHRS) Slack channel and tag **Sugata Mazumdar** (@sugata.mazumdar1).

#### 3.3.2 Create SCC Instance

- To create an **SCC instance**, follow the setup guide available [**here**](https://pages.github.ibm.com/project-fortress/scc-internal-adoption/setup/how-to-set-up-scc/).

#### 3.3.3 Provider ID Setup

- **Set up a Provider ID** for your SCC instance by following the instructions in the documentation [**here**](https://pages.github.ibm.com/project-fortress/scc-internal-adoption/onboarding/etl/#provider-id-setup).
- **Naming Convention**: Use the format `<servicename>-<environment-type>` for the **Provider ID**.

Once you’ve completed the steps for creating the SCC instance and attaching it, your setup will be ready.

![SCC Attachment](images/scc_attachment.png)


# <a name="_configuring_tekton"></a><a name="_setup_data_collection"></a>4. Setup Compliance Automation Toolchain Pipeline

**Note**: If you already have an existing pipeline (Jenkins or any other pipeline) that is collecting evidences either into a GitHub evidence locker or COS bucket, you can skip this section and move to the [**Setup SCC Fact Generation Pipeline**](#_pushing_data_to) section.

**Audience**: Teams that do not have the setup to run the Auditree fetcher.

This pipeline is used to fetch compliance evidences using **Auditree-central fetchers**, and the collected evidence will be stored in the **COS bucket** specified in the given configuration.

## <a name="_create_a_toolchain"></a>4.1 Create a Toolchain

1. Log in to your [**IBM Cloud account**](https://cloud.ibm.com/).
2. Navigate to **Platform Automation -> Toolchains** and click on the **Create toolchain** button.
3. Search for and select the **‘Build your own toolchain’** template.
4. Specify a unique name for the toolchain and choose the appropriate **resource group** and **location**.

![Toolchain Setup Screenshot 1](images/002.png)

![Toolchain Setup Screenshot 2](images/003.png)

![Toolchain Setup Screenshot 3](images/004.png)

![Toolchain Setup Screenshot 4](images/005.png)

## <a name="_add_tool_integrations"></a>**4.2 Add tool integrations**

You need to add a few tool integrations as follows:

- GitHub Enterprise Whitewater
- Delivery Pipeline Private Workers
- Configure Environment
- Configure Slack
- Delivery Pipeline

### <a name="_github_enterprise_whitewater"></a>4.2.1 GitHub Enterprise Whitewater

1. **Click on the 'Add' button** on the right-hand side. This will open the 'Add tool integration' screen.

2. **Configure GitHub Enterprise Whitewater** as an integration tool and set up your GitHub config repository from which Tekton files are to be sourced. Enter the following values:

   - **Auth type**: Personal Access Token
   - **Personal Access Token**: Enter the GitHub personal access token of the service ID with read access to the repository listed below.
   - **Repository type**: Existing
   - **Repository URL**: <https://github.ibm.com/ComplianceAutomation/iaas-scc-data-pipelines.git>
   - **Deselect** the checkbox for **Enable GitHub Issues & Track deployment of code changes**.

Here are the images for reference:

![Image 1](images/006.png)  
![Image 2](images/007.png)  
![Image 3](images/008.png)  

### <a name="_delivery_pipeline_private"></a>4.2.2 Delivery Pipeline Private Workers

- Tekton pipelines are executed by Workers, which can be provided either by adding and configuring a Private Worker tile on your toolchain, or by using the shared pool of IBM Managed Public Workers. If you want to run your pipelines on a Private Worker and haven’t added one yet, [click here](https://cloud.ibm.com/devops/catalog/private_worker?toolchainId=191d9326-fb6e-4c51-933e-ba062a75599c&env_id=ibm:yp:us-south).

- Some providers, such as IKS, Registry, and SOS, use IBM's private network for communication. The TaaS worker is crucial for enabling communication with these internal networks within the pipeline. For more information on obtaining a TaaS worker, please visit [here](https://taas.cloud.ibm.com/getting-started/tekton/tekton-onboarding.md).

- To add the Delivery Pipeline Private Worker integration:
  - Click the **‘Add’** button on the right-hand side to open the **‘Add tool integration’** screen.
  - Add **Delivery Pipeline Private Worker** as an integration tool.
  - Specify a **unique name** for the worker.
  - Add the **Service ID API Key** of the TaaS worker.


![Image 1](images/009.png)  
![Image 2](images/010.png)  

### <a name="_configure_environment"></a>4.2.3 Configure Environment

Add the **Configure Environment** integration to store global variables required for the Tekton pipeline.

1. Click the **‘Add’** button on the right-hand side to open the **‘Add tool integration’** screen.
2. Add **Configure Environment** as an integration tool.
3. Specify a **unique name** for it (e.g., **global-variable**).
4. If the COS bucket where you want to store evidence data has not been created yet, click [here](https://cloud.ibm.com/docs/devsecops?topic=devsecops-cd-devsecops-cos-config)
5. Add the following **environment variables** as global variables for Tekton:

   - **cos_bucket**: Name of the COS bucket where you want to store evidence data.  
     Example: `Input-bucket-env-devsecops-sre-team`
   
   - **cos_instance**: The COS instance CRN.  
     Example: `crn:v1:bluemix:public:cloud-object-storage:global:a/aaabbbcccc:eeeefffggg::`
   
   - **cos_region**: The COS instance region.  
     Example: `us-south`
   
   - **credential-apikey**: The IBM Cloud API key that has access to push the evidence data to the COS bucket.
   
   - **cos_endpoint_vlocker**: Endpoint for COS VLocker.  
     Example: `<https://s3.<cos_region>.cloud-object-storage.appdomain.cloud>`
   
   - **mono_repo**: Name of the GitHub repository containing pipeline definitions to run Auditree fetchers.  
     Example: `ComplianceAutomation/iaas-scc-data-pipelines`
   
   - **mono_repo_branch**: Name of the GitHub branch containing the pipeline definitions to run Auditree fetchers.  
     Example: `master`


![Image 3](images/011.png)  
![Image 4](images/012.png)  


### <a name="_configure_slack"></a>4.2.4 Configure Slack

With Slack, you can collaborate with your team and receive notifications from your tools.

- Click on the **‘Add’** button on the right-hand side. This will open the **‘Add tool integration’** screen.
- Search for and add **‘Configure Slack’** as an integration tool.
- Enter the following details and then click on **‘Create integration’**:

   - **Slack webhook**: Type the Slack webhook URL, which is generated by Slack as an incoming webhook. You can create or find your webhook in the Incoming Webhooks section of the [Slack API website](https://api.slack.com/messaging/webhooks). If you have been using an API key, update your configuration to use a webhook instead.
   
   - **Slack channel**: The name of the existing Slack channel where notifications should be posted.

   - **Slack team name**: If you're using a webhook, specify your **team name**, which is the part before `.slack.com` in your team URL.  
     For example, if your team URL is [](https://my-team.slack.com), the team name is `my-team`.

   - **Pipeline events**: Select the pipeline events for which you want to receive notifications. Check the following options:
     - Pipeline started
     - Pipeline succeeded
     - Pipeline failed
       
![Image](images/015.png)  



### <a name="_delivery_pipeline"></a>4.2.5 Delivery Pipeline

- Click on the **‘Add’** button on the right-hand side. This will open the **‘Add tool integration’** screen.
- Add **Delivery Pipeline** as an integration tool.
- Specify a **unique name** for the pipeline and designate **"Tekton"** as the chosen **"Pipeline type"**.

![Image](images/016.png)  

![Image](images/017.png)

![Image](images/018.png)  


4. After adding the pipeline, go back to the **dashboard** of the Toolchain.
5. Configure your Delivery Pipeline by clicking on the pipeline created in the previous step.
6. Click on **Settings**.

#### <a name="_pipeline_definitions"></a>**4.2.5.1 - Pipeline Definitions**

- Click on **Settings** -> **Definitions** -> **Add**.
- In the **‘Definition Repository’** section, enter the following values:

   - **Repository**: [iaas-scc-data-pipelines](https://github.ibm.com/ComplianceAutomation/iaas-scc-data-pipelines.git)
   - **Input type**: Branch
   - **Branch**: Integration
   - **Path**: `deployments/toolchains/data-collection/auditree-runner`
   
- Click **Save**.

**Note**: The **Integration** branch is the default branch for this repository.

![Image](images/019.png)


#### <a name="_worker"></a>**4.2.5.2 - Worker**

- Click on **Worker**.
- From the dropdown menu, select your designated **private worker** that you configured earlier.
- Click on **Save**.

![Image](images/020.png)  

#### <a name="_environment_properties"></a> **4.2.5.3 - Environment Properties**

- Click on **Environment properties**.
- Include all the necessary environment variables needed to run your **Auditree**. You can add additional variables as needed for any specific fetchers.

![Image](images/021.png)  

**Note**: Depending on the **Auditree Provider**, your environment properties may vary. You can also explore the pipeline code to see the use of specific environment properties.

Here are the key environment properties you might need to define:

- **accreditations**: `auditree`
- **artifactory_api_key**: Artifactory API key for installing packages.
- **artifactory_user**: Artifactory Username for installing packages.
- **compliance-baseimage**: The image used by Tekton code for executing Auditree code base.  
  Example: `<us.icr.io/auditree-runner-devsecops/ibmcloud-cmdb-automation-poc@sha256:183c2eaaaf643affdddbbf7a4581ef94f0f905cc195a7fa7bb04d38273b3904f>`
- **config_json**: The Auditree provider configuration file specific to your service.
- **fetchers**: Name of the Auditree fetcher.
- **fetchers-path**: Path for the Auditree fetcher.
- **fetchers_checks_selection**: Select both fetchers and checkers (`both`).
- **git-token**: GitHub token for functional ID or user ID.
- **github-useremail**: GitHub user email for functional ID or user ID.
- **github-username**: GitHub username for functional ID or user ID.
- **idx_bucket**: Indexation COS bucket with the latest files used to store temporary files.
- **inventory_api_key**: SOS API key for functional ID or user ID with access to your SOS inventory data.
- **inventory_email**: [SOS account email](mailto:caplatform@ibm.com) for functional ID or user ID.
- **reference**: Reference given to the vlocker to store data in the proper folder structure.
- **To obtain the `one-pipeline-dockerconfigjson`**, run the following commands:

```bash
kubectl create secret docker-registry my-docker-key \
--dry-run=client \
--docker-server=us.icr.io \
--docker-username=iamapikey \
--docker-password=<functional_id_ibm_cloud_apikey> \
--docker-email=<functional_id_email> \
--output="jsonpath={.data.\.dockerconfigjson}"
```

## <a name="_configuring_additional_fetchers"></a>**4.3 Configuring Fetchers and Checks**

1. You can add or modify the fetcher configuration file in the [**devel_json_files**](https://github.ibm.com/ComplianceAutomation/iaas-scc-data-pipelines/tree/integration/iac/auditree_config/devel_json_files) folder, as per your service team's requirements. You can refer to [**auditree-central**](https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider) for guidance. Each provider has a README that describes how to configure and run their fetchers and checks.  
   Example: `vpc-rias.json`

2. You can add or modify the check configuration file in the [**controls_json_files**](https://github.ibm.com/ComplianceAutomation/iaas-scc-data-pipelines/tree/integration/iac/auditree_config/controls_json_files) folder. This file associates the checks with an accreditation. You can refer to [**auditree-central**](https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider) for more details. Each provider’s README provides the necessary instructions for configuring and running fetchers and checks.  
   Example: `vpc-rias.json`

3. Files from the [**scc_auditree_config**](https://github.ibm.com/ComplianceAutomation/iaas-scc-data-pipelines/tree/integration/iac/auditree_config/scc_auditree_config) folder use the Python import method to execute multiple fetchers together for any service. You can create or modify these files to run multiple fetchers for your service.

### <a name="_configuring_notifiers"></a><a name="_configuring_seed_with"></a>Environment Properties for Configuration

These properties are already provided in the environment properties. Ensure you use the correct environment property names as follows:

- **config_json**: For fetcher configuration.
- **controls_json**: For check configuration.
- **fetchers-path**: The file path that contains the fetcher details.
- **fetchers**: This file contains the commands to run fetchers and checkers from the specified folder [**scc_auditree_config**](https://github.ibm.com/ComplianceAutomation/iaas-scc-data-pipelines/tree/integration/iac/auditree_config/scc_auditree_config).

### <a name="_help"></a><a name="_references"></a>Adding a Trigger to Run the Pipeline

1. Go back to the dashboard of your Delivery Pipeline and add a **Manual trigger** or a **Timed trigger** to run your pipeline.
   - **Manual trigger** can be executed anytime by a user.
   - **Timed trigger** will execute the pipeline at a specific time.

2. Specify a **unique name** for the trigger.
3. Select your **Git config repository** as the **EventListener**.
4. Select the **TaaS worker** as your **Worker**.

![Image](images/022.png)  
![Image](images/023.png)  
5. After configuring the trigger, the dashboard should look something like this:

![Image](images/024.png)  
6. To initiate a trigger, select the created trigger and then choose the **Run pipeline** option located in the top right corner.

![Image](images/025.png)  
![Image](images/026.png)  
7. Each pipeline run will display a status:
   - **Green**: Pipeline succeeded.
   - **Red**: Pipeline failed.
   - **Grey**: Pipeline cancelled.

![Image](images/027.png)  

# <a name="_pushing_data_to"></a> 5. Setup SCC Fact Generation Pipeline

This section provides detailed steps to configure a Tekton pipeline to transform raw evidence into SCC facts in service-owned COS buckets.

**Note:** You can reuse the Toolchain pipeline created in the previous section and some of its existing configuration for this pipeline. The only difference is that a new pipeline needs to be created, as it will use a different code base for pushing data to the SCC COS instance.

## <a name="_add_integration_tool"></a> Add Integration Tool

We will use the same **GitHub Enterprise Whitewater** and **Delivery Pipeline Private Workers** tool integrations. The only difference is in the **Delivery Pipeline**, which will be configured with the **SCC code base** and relevant environment properties.

### <a name="_delivery_pipeline_scc"></a>5.1 Delivery Pipeline

1. Add **Delivery Pipeline** as an integration tool.
2. Specify a **unique name** for the pipeline.
3. Designate **"Tekton"** as the chosen **"Pipeline type"**.

![Image](images/028.png)  
![Image](images/029.png)  


4. Go back to the **Toolchain dashboard** and configure your Delivery Pipeline by clicking on the pipeline created in the previous step.

#### **5.1.1 - Pipeline Definitions**

1. Click on **Settings** -> **Definitions** -> **Add**.
2. In the **‘Definition Repository’** section, enter the following values:

   - **Repository**: [iaas-scc-data-pipelines](https://github.ibm.com/ComplianceAutomation/iaas-scc-data-pipelines.git)
   - **Input type**: Branch
   - **Branch**: `Integration`
   - **Path**: `deployments/toolchains/scc-facts-generation/scc-facts-ingestion`

3. Click **Save**.

This will configure the SCC Fact Generation Pipeline with the correct repository and settings to start transforming evidence data into SCC facts.

#### *5.1.2 - Worker*

1. Click on **Worker**.
2. Choose **'IBM Managed Workers in DALLAS'** from the dropdown menu.
3. Click **Save**.

### <a name="_etl_script_setup"></a>**5.1.3 - Environment Properties**

Add the necessary **Environment properties** required to run your SCC code.

![Image](images/030.png)  
The following environment properties are required for configuring the pipeline. These properties depend on the **locker type** (COS or GIT):

#### **LOCKERTYPE** can be:
- **COS**: Requires a reference for COS objects, and the following properties:
  - **COS_BUCKET**
  - **COS_REGION**
  - **IDX_BUCKET**
  - **VLOCKER_REPO**
  - **VLOCKER_REPO_BRANCH**
  
- **GIT**: Requires a GitHub org/repo and branch.

#### General Environment Properties (for any locker type):
- **lockertype**: Type of locker used for this pipeline. (Possible values: `cos` or `git`)
- **compliance-baseimage**: Image name used when running the pipeline.
- **dry_run**: Enable dry run (`true` or `false`).
- **erictree_cos_bucket**: SCC config param for TOML file, used to store EricTree evidence’s COS bucket.
- **erictree_cos_endpoint**: SCC config param for TOML file, used to store EricTree evidence’s COS endpoint.
- **et_cos_instance_crn**: SCC config param for TOML file, used to store EricTree evidence’s COS CRN.
- **git_token**: GitHub token for the functional ID/user with read access to the evidence locker and **ComplianceAutomation/iaas-scc-data-pipelines**.
- **git_username**: GitHub username of the functional ID/user chosen to run the pipeline.
- **iam_api_key**: IBM Cloud API key for authentication that has access to the SCC instance and COS buckets required to push the facts and raw data.
- **one-pipeline-dockerconfigjson**: Credentials to retrieve images from the container registry.
- **scc_endpoint**: SCC config param for TOML file, used to store SCC endpoint.
- **scc_git_branch**: SCC config param for TOML file, used to store the SCC GitHub branch.
- **scc_git_repo**: SCC config param for TOML file, used to store the SCC GitHub repository.
- **provider_instance_id**: SCC config param for TOML file. You can [Click here](#_obtaining_script) for information on how to generate the provider instance ID.

You can obtain **one-pipeline-dockerconfigjson** by running the following commands:
  ```bash
  kubectl create secret docker-registry my-docker-key \
  --docker-server=us.icr.io \
  --docker-username=iamapikey \
  --docker-password=<functional_id_ibm_cloud_apikey> \
  --docker-email=<functional_id_email>

  kubectl  get secret  my-docker-key --output="jsonpath={.data.\.dockerconfigjson}"
  ```
#### Additional Environment Properties for Locker Type **GIT**:
- **locker_git_repo**: The GitHub repository used as the evidence locker.  
  Example: `vpnaas-dev/evidence_locker`.
- **locker_git_branch**: The branch of the GitHub repository used as the evidence locker.  
  Example: `master`.

#### Additional Environment Properties for Locker Type **COS**:
- **cos_bucket**: The COS bucket name used for cloning evidence from COS.
- **cos_region**: The COS region where the evidence locker is located.
- **idx_bucket**: The bucket used by VLocker to store and fetch configuration files for the COS locker.
- **locker_cos_instance**: The COS instance CRN (Cloud Resource Name).
- **vlocker_repo**: The VLocker repository used for installation.  
  Example: `ComplianceAutomation/datalake`.
- **vlocker_repo_branch**: The VLocker repository branch used for installation.  
  Example: `integration`.
- **reference**: The reference used for the COS locker to store data in the correct folder structure.

### **5.2 Add Trigger**

1. Go back to the **dashboard** of your **Delivery Pipeline** and add a **Manual trigger** to run your pipeline. Alternatively, you can select a **timed trigger** to automatically execute the pipeline on a scheduled time after every fixed interval.

2. Specify a unique name for the trigger.

3. Select the previously created **`iaas-scc-data-pipelines`** Git config repository as the **EventListener**.

4. Select **"Inherited from Pipeline Configuration (IBM Managed workers)"** as the **Worker**.

After configuring the trigger, your dashboard should look something like this:

![A screenshot of a computer description automatically generated](images/031.png)


### **5.3 Run Trigger**

1. To initiate a trigger, select the created trigger and then choose the **Run pipeline** option located in the top right corner.

2. Each pipeline run will display a status:
   - **Green**: Indicates the pipeline has **succeeded**.
   - **Red**: Indicates the pipeline has **failed**.
   - **Grey**: Indicates the pipeline has been **cancelled**.

# <a name="_controls_and_fetchers_mapping"></a>6. Controls and fetchers mapping

<!-- 
|**Controls**|[**Providers**](https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider)|**Auditree Fetchers**|
| :- | :- | :- |
|Gen1 - Inventory Management|[SOS](https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/sos)|SOSFIMDetailsFetcher<br>SOSInventoryFetcher<br>SOSHealthCheckDetailsFetcher<br>SOSQRadarFetcher<br>TenableComplianceListFetcher<br>SOSTenablePatchFetcher<br>SOSTenableHealthCheckFetcher<br>SOSOpenVulnerabilityFetcher<br>SOSSystemVulnerabilityFetcher<br>SOSTenableConfiguredHealthChecks|
|Gen1.1 - Inventory Listing/Source|[VPC](https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/vpc)|VPCResourceFetcher|
|D3/D5 – Intrusion Detection / Remote Access Monitoring|||
|E8 – Patch Management|||
|E9 - Container Patch Management|||
|E10 - Health Checks|||
|E11 - Container image health checks|||
 -->
 <table>
  <tr>
    <th>Controls</th>
    <th><a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider">Providers</a></th>
    <th>Auditree Fetchers</th>
  </tr>
  <tr>
    <td rowspan="2">Gen1 - Inventory Management</td>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/sos">SOS</a>
    </td>
    <td>
      SOSInventoryFetcher
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/iks">IKS</a>
    </td>
    <td>
      ClusterFetcher<br>WorkerFetcher
    </td>
  </tr>
  <tr>
    <td rowspan="2">D3/D5 – Intrusion Detection / Remote Access Monitoring</td>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/sos">SOS</a>
    </td>
    <td>
      SOSInventoryFetcher<br>SOSQRadarFetcher
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/iks">IKS</a>
    </td>
    <td>
      ClusterFetcher<br>WorkerFetcher
    </td>
  </tr>
  <tr>
    <td>E8 – Patch Management</td>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/sos">SOS</a>
    </td>
    <td>
      SOSInventoryFetcher<br>SOSQRadarFetcher<br>SOSTenablePatchFetcher
    </td>
  </tr>
  </tr>
  <tr>
    <td rowspan="2">E9/E11 - Container Patch Management/Container image health checks</td>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/iks">IKS</a>
    </td>
    <td>
      ClusterFetcher<br>ResourceFetcher
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/registry">Registry</a>
    </td>
    <td>
      ClusterImagesVulnCheck<br>ImageOwnerFetcher
    </td>
  </tr>
  <tr>
    <td>E10 - Health Checks</td>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/sos">SOS</a>
    </td>
    <td>
      SOSInventoryFetcher<br>HealthCheckDetailsCheck<br>SOSTenableConfiguredHealthChecks
    </td>
  </tr>
  <tr>
    <td>G1 - Change Management</td>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/changerequest">ChangeRequest</a>
    </td>
    <td>
      ChangeRequestFetcher
    </td>
  </tr>
  <tr>
    <td rowspan="2">E4/E5/E7 - Access Control</td>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/accesshub">AccessHub</a>
    </td>
    <td>
      AccessHubAccountsFetcher<br>AccessHubRequestHistoryFetcher<br>AccessHubRequestHistoryDetailsFetcher
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/iam">IAM</a>
    </td>
    <td>
      IAMFetcher
    </td>
  </tr>
  <tr>
    <td rowspan="3">H1 - Capacity Monitoring</td>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/sos">SOS</a>
    </td>
    <td>
      SOSInventoryFetcher
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/iks">IKS</a>
    </td>
    <td>
      ClusterFetcher<br>ResourceFetcher<br>WorkerFetcher
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/observability">Observability</a>
    </td>
    <td>
      ActivityTrackerInstanceFetcher<br>SysdigInstanceFetcher<br>SysdigAlertsFetcher<br>SysdigNotifChannelsConfigFetcher
    </td>
  </tr>
  <tr>
    <td rowspan="4">D2 - Network Traffic Monitoring</td>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/sos">SOS</a>
    </td>
    <td>
      SOSInventoryFetcher
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/iks">IKS</a>
    </td>
    <td>
      ClusterFetcher<br>ResourceFetcher<br>WorkerFetcher
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/observability">Observability</a>
    </td>
    <td>
      SysdigInstanceFetcher<br>SysdigAlertsFetcher
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/pagerduty">PagerDuty</a>
    </td>
    <td>
      PagerDutyEventsAnalyticsFetcher<br>PagerDutyEventsFetcher
    </td>
  </tr>
  <tr>
    <td rowspan="3">H6 - Backup Logs</td>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/icd">ICD</a>
    </td>
    <td>
      DatabasesFetcher<br>DatabaseBackupsFetcher
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/observability">Observability</a>
    </td>
    <td>
      ActivityTrackerInstanceFetcher<br>SysdigAlertsFetcher<br>
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider/pagerduty">PagerDuty</a>
    </td>
    <td>
      PagerDutyEventsAnalyticsFetcher<br>PagerDutyEventsFetcher
    </td>
  </tr>
</table>


# <a name="_help_and_references"></a>7. Help and References
  
Following are the links for additional information:
- Review the [Onboarding FAQ answers](https://pages.github.ibm.com/auditree/auditree-central-docs/#/faq/onboarding).
- Reach out to the auditree team in the [#auditree-users](https://ibm-cloudplatform.slack.com/archives/CH5MUUS9J) slack channel.
- [Read me for auditree tekton pipeline.](https://github.ibm.com/ComplianceAutomation/iaas-scc-data-pipelines/blob/integration/deployments/toolchains/data-collection/auditree_tekton/Readme.md)
- [Read me for scc fact ingestion pipeline.](https://github.ibm.com/ComplianceAutomation/iaas-scc-data-pipelines/blob/integration/deployments/toolchains/scc-facts-generation/scc-facts-ingestion/README.md)
- SCC repo - [scc-px-facts-model-python](https://github.ibm.com/project-fortress/scc-px-facts-model-python/)
- [Auditree Central Docs](https://pages.github.ibm.com/auditree/auditree-central-docs/#/)
- [SCC internal adoption](https://pages.github.ibm.com/project-fortress/scc-internal-adoption/onboarding/etl/)
- [Auditree Providers](https://github.ibm.com/auditree/auditree-central/tree/master/auditree_central/provider)
