# `azure-function-distributed-tracing`

Distributed tracing sample for Azure Durable Functions

## Run application

### Fast API

### 1. Configurations

Copy the file `.env.sample` to be `.env` at the root of the repository.

```txt
FUNCTION_URL=<azure-function-url>
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
