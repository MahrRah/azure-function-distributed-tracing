# `azure-function-distributed-tracing`

Distributed tracing sample for Azure Durable Functions

## Configurations

Copy the file `.env.sample` to be `.env` at the root of the repository.

```txt
FUNCTION_URL=<base-url-of-azure-function>
```

## Run application

### Fast API

#### 1. Run

To run the sample API use the following make command:

```bash
make serve
```

### Azure function orchestrator

#### 1. Set up and run Azurite

- Install VSCode extension([Azure market place: Azurite](https://marketplace.visualstudio.com/items?itemName=Azurite.azurite))
- Run Azurite ([VSCode Extension Commands](https://github.com/azure/azurite?tab=readme-ov-file#visual-studio-code-extension))

Run the function use the following make command:

#### 2. Run

```bash
make start-func 
```
