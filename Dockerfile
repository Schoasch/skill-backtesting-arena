# Glama-Release-Shim: brückt Glamas stdio-MCP-Evaluator → unseren Remote-HTTP-MCP-Server.
# Der Server ist remote-only (https://tradingstrategies.work/api/mcp); dieser Container gibt
# Glama etwas zum Bauen + Laufen, damit es die Tool-Definitionen enumerieren + scoren kann.
# tools/list ist public (unauth) → kein Token für die Quality-Eval nötig; mcp-remote löst
# den OAuth-Flow nur bei einem 401 aus, und initialize/tools/list antworten mit 200.
FROM node:22-alpine
ENTRYPOINT ["npx", "-y", "mcp-remote@latest", "https://tradingstrategies.work/api/mcp"]
