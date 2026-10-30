"""MCP 2025-11-25 framing only. All business operations live in product_cli."""
from contextlib import redirect_stdout
import json
import sys

from neoweaver.product_cli import OPERATIONS, execute, operation_schemas
from neoweaver.task_adapter import _json

VERSION = '2025-11-25'


def error(identifier, code, message):
    return {'jsonrpc': '2.0', 'id': identifier, 'error': {'code': code, 'message': message}}


def serve(reader=None, writer=None):
    reader = reader if reader is not None else sys.stdin.buffer
    writer = writer if writer is not None else sys.stdout
    phase = 'new'
    try:
        for line in reader:
            try:
                request = _json(line)
            except (ValueError, UnicodeError):
                response = error(None, -32700, 'Parse error')
            else:
                identifier = request.get('id') if isinstance(request, dict) else None
                if (not isinstance(request, dict) or request.get('jsonrpc') != '2.0'
                        or not isinstance(request.get('method'), str)
                        or ('id' in request and type(identifier) not in (int, str))
                        or set(request) - {'jsonrpc', 'id', 'method', 'params'}):
                    response = error(None, -32600, 'Invalid Request')
                elif 'id' not in request:
                    if (request['method'] == 'notifications/initialized' and phase == 'initializing'
                            and request.get('params', {}) == {}):
                        phase = 'ready'
                    continue
                else:
                    method = request['method']
                    params = request.get('params', {})
                    result = None
                    response = None
                    if not isinstance(params, dict):
                        response = error(identifier, -32602, 'Object params required')
                    elif method == 'ping':
                        result = {}
                    elif method == 'initialize':
                        client = params.get('clientInfo')
                        if phase != 'new':
                            response = error(identifier, -32600, 'Already initialized')
                        elif (not isinstance(params.get('protocolVersion'), str)
                              or not isinstance(params.get('capabilities'), dict)
                              or not isinstance(client, dict)
                              or not isinstance(client.get('name'), str)
                              or not isinstance(client.get('version'), str)):
                            response = error(identifier, -32602, 'protocolVersion, capabilities and clientInfo required')
                        else:
                            result = {'protocolVersion': VERSION, 'capabilities': {'tools': {}},
                                      'serverInfo': {'name': 'neoweaver', 'version': '0.1.0'}}
                            phase = 'initializing'
                    elif phase != 'ready':
                        response = error(identifier, -32600, 'Initialize and notify initialized first')
                    elif method == 'tools/list':
                        if set(params) - {'_meta'}:
                            response = error(identifier, -32602, 'This fixed tool list has no cursor')
                        else:
                            result = {'tools': operation_schemas()}
                    elif method == 'tools/call':
                        name = params.get('name')
                        arguments = params.get('arguments', {})
                        if (not isinstance(name, str) or name not in OPERATIONS
                                or not isinstance(arguments, dict)
                                or set(params) - {'name', 'arguments', '_meta'}):
                            response = error(identifier, -32602, 'Named tool and object arguments required')
                        else:
                            try:
                                with redirect_stdout(sys.stderr):
                                    output = execute(name, arguments)
                                result = {'content': [{'type': 'text', 'text': json.dumps(output, ensure_ascii=True, allow_nan=False)}],
                                          'structuredContent': output,
                                          'isError': output.get('status') in ('refused', 'failed', 'unknown', 'REFUSED', 'BLOCKED')}
                            except Exception as exception:
                                print('operation_exception:' + type(exception).__name__, file=sys.stderr)
                                response = error(identifier, -32603, 'Internal error; inspect original Owner before retry')
                    else:
                        response = error(identifier, -32601, 'Method not found')
                    if response is None:
                        response = {'jsonrpc': '2.0', 'id': identifier, 'result': result}
            writer.write(json.dumps(response, ensure_ascii=True, allow_nan=False) + '\n')
            writer.flush()
    except (KeyboardInterrupt, BrokenPipeError):
        return 130
    return 0
