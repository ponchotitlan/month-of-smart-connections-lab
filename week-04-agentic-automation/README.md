# Week 4: Intentions Matter

**Part of the [Month of Smart Connections Lab](https://github.com/ponchotitlan/month-of-smart-connections-lab)**

<div align="center">
<img src="../images/week4_agentic_arch.png"/>
</div>

Agentic AI automation for network operations using MCP (Model Context Protocol) servers, NetBox, pyATS, and GitHub. Describe what you want to do in plain language — let the agent figure out how to do it.

## Why Agentic AI for Network Automation?

Traditional automation scripts are great at repeating known tasks. But what happens when you need to reason across multiple tools, adapt to the current network state, or handle tasks that weren't scripted in advance? Agentic AI fills that gap:

- **Intent-Driven Workflows:** Describe the goal in natural language: the agent determines the sequence of actions
- **Multi-Tool Orchestration:** Chain NetBox queries, device connections, config pushes, and report generation automatically
- **Safety-First Execution:** The agent validates configurations against live device state and waits for your approval before making changes
- **Self-Documenting Outputs:** Save compliance reports, open GitHub issues, and generate network diagrams as part of the same conversation

This project wires together an AI assistant with a set of **MCP servers** so that all of these capabilities are available as natural-language commands.

## Model Context Protocol (MCP)

[MCP (Model Context Protocol)](https://modelcontextprotocol.io/) is an open standard that lets AI models discover and call external tools at runtime. Think of it as a universal plugin system for AI agents:

- Each MCP server exposes a well-defined set of **tools** the agent can invoke
- Tools are called with structured inputs and return structured results
- The AI client (e.g., LibreChat, Claude Desktop) acts as the orchestrator, deciding which tool to call based on the user's intent
- All four MCP servers in this project run as lightweight Docker containers, connected on a shared `mcp-net` bridge network

## Architecture Overview

| Component | Type | Description |
|-----------|------|-------------|
| **`AGENT.md`** | System Prompt | Instructions and rules loaded into the AI assistant at the start of every session |
| **`docker-compose.yml`** | Infrastructure | Spins up all four MCP servers as Docker containers |
| **`testbed.yaml`** | pyATS Testbed | Device inventory baseline for the Cisco Modeling Labs Always-On Sandbox |
| **`.env.example`** | Configuration | Template for all environment variables: copy to `.env` and fill in your values |
| **`compliance-reports/`** | Output Directory | Landing folder where the agent commits report files via GitHub MCP |

## MCP Servers

| Server | Access | Scope |
|--------|--------|-------|
| **NetBox MCP** | Read-only | Network source of truth: devices, platforms, IP addresses, credentials vault |
| **pyATS MCP** | Read/Write | Device testing, CLI command execution, testbed/inventory management |
| **GitHub MCP** | Read/Write | Repository operations: file commits, issue creation, pull requests |
| **DrawIO MCP** | Read/Write | Network diagram creation and editing |

> ⚠️ **GitHub access is scoped** to `ponchotitlan/month-of-smart-connections-lab` only.

## Agent Capabilities (AGENT.md)

The `[AGENT.md](AGENT.md)` file is the **system prompt** loaded into your AI client. It defines the assistant's identity, tool usage rules, and safety guardrails.

| Capability | Trigger | Behavior |
|------------|---------|----------|
| `📋 Show Device Inventory` | "Show me the inventory" | Syncs NetBox → pyATS, displays result from pyATS |
| `💻 Execute CLI Commands` | "Run show interfaces on R1" | Reads current device state, executes read-only show commands |
| `🛡️ Validate & Push Configs` | "Configure loopback on R2" | Fetches running config, checks for conflicts, shows dry-run, waits for approval |
| `📝 Save Compliance Reports` | "Save the compliance report" | Commits file to `compliance-reports/` in the GitHub repository |
| `🐙 Create GitHub Issues` | "Open a ticket for high CPU on R1" | Creates an issue in the repo with title, body, and labels |
| `🗺️ Generate Network Diagrams` | "Draw the core topology" | Creates diagram with DrawIO, renders Mermaid preview inline in chat |

## Setup

### 1. Clone and configure environment

```bash
# Navigate to directory
cd week-04-agentic-automation

# Copy the environment template
cp .env.example .env
```

Open `.env` and fill in your real values:

| Variable | Required | Description |
|----------|----------|-------------|
| `NETBOX_URL` | Yes | URL of your NetBox API, reachable from Docker containers (for local Docker Desktop setups, `http://host.docker.internal:8080` is common) |
| `NETBOX_TOKEN` | Yes | NetBox API token (also used by pyATS to access NetBox secrets) |
| `NETBOX_MCP_PORT` | Yes | Port exposed by NetBox MCP (`8081` by default) |
| `PYATS_MCP_PORT` | Yes | Port exposed by pyATS MCP (`8082` by default) |
| `CREDENTIALS_VAULT_BASE_URL` | Yes | NetBox URL used by pyATS credentials vault integration (usually same as `NETBOX_URL`) |
| `GITHUB_PAT` | Yes | GitHub fine-grained personal access token |
| `GITHUB_MCP_PORT` | Yes | Port exposed by GitHub MCP (`8083` by default) |
| `DRAWIO_MCP_PORT` | Yes | Port exposed by DrawIO MCP (`8084` by default) |
| `GITHUB_TOOLSETS` | Optional | Comma-separated GitHub toolsets to expose |
| `NETBOX_MCP_LOG_LEVEL` | Optional | NetBox MCP log level (default: `INFO`) |
| `NETBOX_MCP_VERIFY_SSL` | Optional | NetBox MCP SSL verification flag (default: `true`) |

Quick endpoint reference from the current `docker-compose.yml`:

| Service | Default URL |
|---------|-------------|
| NetBox MCP | `http://localhost:8081/mcp` |
| pyATS MCP | `http://localhost:8082/mcp` |
| GitHub MCP | `http://localhost:8083/mcp` |
| DrawIO MCP | `http://localhost:8084/mcp` |


> **Don't have a NetBox instance?** You have two options:
>
> **Option A: Set up NetBox with the netbox-secrets plugin (full setup)**
>
> This project relies on NetBox having the [netbox-secrets](https://github.com/Onemind-Services-LLC/netbox-secrets) plugin enabled. The pyATS MCP server fetches device credentials from NetBox secrets stored under the roles `username` and `password` for each device. To set this up yourself on a local Docker NetBox, follow [this guide](netbox_secrets_setup.md).
>
> **Option B: Skip NetBox entirely and use the provided testbed (recommended for a quick start)**
>
> The included `testbed.yaml` already contains all devices from the **Cisco Modeling Labs Always-On Sandbox** on DevNet. Just [book the free sandbox](https://devnetsandbox.cisco.com) and connect via the provided VPN.
>
> When using `testbed.yaml`, replace the `pyats-mcp` service in `docker-compose.yml` with the simpler version below (no vault variables needed) and **remove the `netbox-mcp` service entirely**:
>
> ```yaml
> pyats-mcp:
>   build:
>     context: https://github.com/ponchotitlan/pyATS_MCP.git
>     dockerfile: Dockerfile
>   image: pyats-mcp:latest
>   container_name: pyats-mcp
>   environment:
>     MCP_TRANSPORT: ${PYATS_MCP_TRANSPORT}
>     MCP_HOST: ${PYATS_MCP_HOST}
>     MCP_PORT: ${PYATS_MCP_PORT}
>     PYATS_TESTBED_PATH: /app/testbed.yaml
>     PYATS_MCP_ARTIFACTS_DIR: /app/artifacts
>     PYATS_MCP_KEEP_ARTIFACTS: "1"
>   volumes:
>     - ./testbed.yaml:/app/testbed.yaml:ro
>     - pyats-mcp-artifacts:/app/artifacts
>   ports:
>     - "${PYATS_MCP_PORT}:${PYATS_MCP_PORT}"
>   networks:
>     - mcp-net
>   restart: unless-stopped
> ```

### 2. Start the MCP servers

```bash
docker compose up -d
```

This builds and starts four containers on the `mcp-net` bridge:

| Container | Default Port |
|-----------|-------------|
| `netbox-mcp` | `8081` |
| `pyats-mcp` | `8082` |
| `github-mcp` | `8083` |
| `drawio-mcp` | `8084` |

Verify all containers are running:

```bash
docker compose ps
```

Optional sanity checks:

```bash
docker compose logs -f --tail=100 netbox-mcp pyats-mcp github-mcp drawio-mcp
```

### 3. (Optional) Load the testbed

The included `testbed.yaml` targets the [**Cisco Modeling Labs Always-On Sandbox**](https://devnetsandbox.cisco.com/DevNet/catalog/cml-sandbox_cml). If you want to use it as a starting point for pyATS.

Adjust the IP addresses in `testbed.yaml` to match your sandbox allocation, or replace with your own devices.

### 4. Connect your AI client

Point your AI client (LibreChat, Claude Desktop, or any MCP-compatible client) to the four MCP server endpoints:

```json
{
  "mcpServers": {
    "netbox": { "url": "http://localhost:8081/mcp" },
    "pyats":  { "url": "http://localhost:8082/mcp" },
    "github": { "url": "http://localhost:8083/mcp" },
    "drawio": { "url": "http://localhost:8084/mcp" }
  }
}
```

If your client supports MCP transport selection, use **Streamable HTTP** for all four servers.

Load `AGENT.md` as the **system prompt** for your session.

## Running the Agent

Once connected, interact in plain language and follow this simple pattern:

1. Ask for discovery (inventory or topology context).
2. Ask for validation (checks, audits, command outputs).
3. Ask for action (configuration, report commit, issue creation, diagram export).

> Our YouTube video **[Ep.4: From Intent to Action with Agentic Automation](https://youtu.be/YCMW6qSJiD0)** showcases how to onboard the MCP servers and create the agent with [LibreChat](https://www.librechat.ai/), along with some prompt examples!


## Additional Resources

| Resource | Description |
|----------|-------------|
| [🤖 Model Context Protocol Specification](https://modelcontextprotocol.io/) | Official MCP documentation and SDK references |
| [📦 NetBox MCP Server](https://github.com/netboxlabs/netbox-mcp-server) | Source of the NetBox MCP server used in this project |
| [🐍 pyATS MCP Server with netbox-secrets support](https://github.com/ponchotitlan/pyATS_MCP/tree/netbox-secrets-support) | Custom pyATS MCP server with NetBox secrets integration |
| [🐙 GitHub MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/github) | Official GitHub MCP server |
| [✏️ DrawIO MCP Server](https://github.com/drawio-app/mcp) | DrawIO MCP server for diagram generation |
| [📘 NetBox Documentation](https://netbox.readthedocs.io/) | NetBox setup, API, and token management |
| [🧪 pyATS Documentation](https://developer.cisco.com/docs/pyats/) | pyATS test framework reference |
| [🎓 LibreChat](https://www.librechat.ai/) | Open-source AI client with MCP support |

---
**⬅️ Previous Week:** [Week 3 - Trust Issues](../week-03-automation-testing/)</br>
**📚 Main Repository:** [Month of Smart Connections Lab](https://github.com/ponchotitlan/month-of-smart-connections-lab)
