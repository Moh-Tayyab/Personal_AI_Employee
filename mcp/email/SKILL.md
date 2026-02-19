# Email MCP Server

This MCP server provides email sending capabilities for Claude Code.

## Features

- Send emails via Gmail API
- Draft emails
- Search emails
- Send with attachments

## Setup

1. Enable Gmail API in Google Cloud Console
2. Download credentials.json
3. Configure the MCP server

## Available Tools

### send_email
Send an email to a recipient.

**Parameters:**
- `to`: Recipient email address
- `subject`: Email subject
- `body`: Email body (plain text or markdown)
- `attachments`: Optional list of file paths

### draft_email
Create a draft email (doesn't send).

**Parameters:**
- `to`: Recipient email address
- `subject`: Email subject
- `body`: Email body

### search_emails
Search emails in Gmail.

**Parameters:**
- `query`: Gmail search query
- `max_results`: Maximum number of results (default: 10)

## Configuration

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["mcp/email/server.py"],
      "env": {
        "VAULT_PATH": "./vault"
      }
    }
  }
}
```
