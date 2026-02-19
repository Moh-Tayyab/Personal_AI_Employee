"""
MCP Server Base Class - Foundation for all MCP servers

This provides a base class for building MCP (Model Context Protocol) servers
that Claude Code can use to perform external actions.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import json
import logging
from typing import Any, Dict


class BaseMCPServer(ABC):
    """Base class for MCP server implementations."""

    def __init__(self, name: str, config: Dict = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    @abstractmethod
    def handle_request(self, method: str, params: Dict = None) -> Any:
        """
        Handle an MCP request.

        Args:
            method: The method name being called
            params: Parameters for the method

        Returns:
            The result of the method call
        """
        pass

    def get_tools(self) -> list:
        """
        Return list of available tools for this server.

        Returns:
            List of tool definitions
        """
        return []

    def get_resources(self) -> list:
        """
        Return list of available resources.

        Returns:
            List of resource definitions
        """
        return []

    def run_stdio(self):
        """Run as stdio server (MCP protocol)."""
        import sys

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                request = json.loads(line)
                method = request.get('method')
                params = request.get('params', {})

                result = self.handle_request(method, params)

                response = {
                    'jsonrpc': '2.0',
                    'id': request.get('id'),
                    'result': result
                }

                print(json.dumps(response))
                sys.stdout.flush()

            except Exception as e:
                self.logger.error(f"Error handling request: {e}")
                error_response = {
                    'jsonrpc': '2.0',
                    'id': request.get('id') if 'request' in locals() else None,
                    'error': {
                        'code': -32603,
                        'message': str(e)
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()


class MCPTool:
    """Represents a tool in the MCP protocol."""

    def __init__(self, name: str, description: str, input_schema: Dict):
        self.name = name
        self.description = description
        self.input_schema = input_schema

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description,
            'inputSchema': self.input_schema
        }


class MCPResource:
    """Represents a resource in the MCP protocol."""

    def __init__(self, uri: str, name: str, description: str = "", mime_type: str = "text/plain"):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type

    def to_dict(self) -> Dict:
        return {
            'uri': self.uri,
            'name': self.name,
            'description': self.description,
            'mimeType': self.mime_type
        }
