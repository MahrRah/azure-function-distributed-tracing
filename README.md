# `azure-function-distributed-tracing`

Distributed tracing sample for Azure Durable Functions

## Prerequisites
 
### Poetry

To create the virtual environment start by doing a poetry install

```bash
poetry install
```

### Provision infrastructure

In case you don't already have a [Application Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview) provisioned, you can use the make file to do so with.

Copy the file `.env.sample` to be `.env` at the root of the repository.
Used for the provisioning are the `ENV_LOCATION` and `ENV_PROJECT_NAME`, which are pre-populated with default values and can be replaced if needed.

```txt
FUNCTION_URL=http://localhost:7071/api/handlers
APPLICATIONINSIGHTS_CONNECTION_STRING=
ENV_LOCATION="westeurope"
ENV_PROJECT_NAME="func-spike"
```

## Run application

### Fast API

### 1. Configurations

In the `.env` at the root of the repository make sure the following section ar populated with the correct connection string.

```txt
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>
```

#### 2. Run

To run the sample API use the following make command:

```bash
make serve
```

### Azure function orchestrator

#### 1. Set up and run Azurite

- Install VSCode extension([Azure market place: Azurite](https://marketplace.visualstudio.com/items?itemName=Azurite.azurite))
- Run Azurite ([VSCode Extension Commands](https://github.com/azure/azurite?tab=readme-ov-file#visual-studio-code-extension))

#### 2. Configure

In the `function` directory create a `local.settings.json` with the following content:

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "APPLICATIONINSIGHTS_CONNECTION_STRING":"<Connection-String>"
  }
}
```

#### 3. Run

Run the function use the following make command:

```bash
make start-func 
```
