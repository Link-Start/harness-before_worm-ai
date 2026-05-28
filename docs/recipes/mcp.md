# MCP Recipe

ABH exposes a local MCP stdio server for clients that prefer tool calls over shell commands.

## Server

```bash
python3 -m abh.mcp_server
```

Get setup metadata:

```bash
abh agent setup mcp --json
```

## Use

The MCP surface is built around the shared Agent-First command contract. Prefer read-only tools for attractor, roadmap, plan status, verification status, audits, memory, drift, and route information. Controlled write tools require explicit confirmation and reuse the same ABH domain gates as the CLI.

## Boundaries

This recipe does not install an MCP client config. It only documents the server command and safety model. Writing editor, Agent, or MCP config files is a later confirmed-write slice.
