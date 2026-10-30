"""Actual stdio subprocess parity probes. Synthetic Owner != installed Host."""
from copy import deepcopy
import json
import subprocess
import unittest

from test_product_cli import CLI, TransportFixture


def message(identifier, method, params=None):
    result = {'jsonrpc': '2.0', 'method': method}
    if identifier is not None:
        result['id'] = identifier
    if params is not None:
        result['params'] = params
    return result


INIT = message(1, 'initialize', {'protocolVersion': '2025-11-25', 'capabilities': {},
                                'clientInfo': {'name': 'test-control', 'version': '1'}})
READY = message(None, 'notifications/initialized')


class MCPCLITests(TransportFixture):
    def mcp(self, requests):
        run = subprocess.run(CLI + ['mcp'], input=''.join(json.dumps(r) + '\n' for r in requests),
                             text=True, capture_output=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stderr)
        return [json.loads(line) for line in run.stdout.splitlines()]

    def call(self, name, arguments):
        return self.mcp([INIT, READY, message(2, 'tools/call', {'name': name, 'arguments': arguments})])[-1]['result']

    def test_initialize_notifications_schema_and_protocol_errors(self):
        outputs = self.mcp([message(0, 'tools/list'), INIT, READY, message(2, 'tools/list'),
                            message(3, 'missing'), message(4, 'tools/call', {'name': 'shell', 'arguments': {}}),
                            message(5, 'initialize', INIT['params']), message(None, 'notifications/cancelled', {'requestId': 9})])
        self.assertEqual(len(outputs), 6)
        self.assertEqual(outputs[0]['error']['code'], -32600)
        self.assertEqual(outputs[1]['result']['protocolVersion'], '2025-11-25')
        self.assertIn('tools', outputs[1]['result']['capabilities'])
        schema_run = subprocess.run(CLI + ['schema'], capture_output=True, text=True, timeout=5)
        self.assertEqual(outputs[2]['result']['tools'], json.loads(schema_run.stdout))
        self.assertEqual(outputs[3]['error']['code'], -32601)
        self.assertEqual(outputs[4]['error']['code'], -32602)
        self.assertEqual(outputs[5]['error']['code'], -32600)

    def test_parse_error_continues_and_stdout_contains_only_rpc(self):
        raw = '{bad}\n{"jsonrpc":"2.0","id":1,"method":"ping"}\n'
        run = subprocess.run(CLI + ['mcp'], input=raw, capture_output=True, text=True, timeout=5)
        outputs = [json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual(outputs[0]['error']['code'], -32700)
        self.assertEqual(outputs[1]['result'], {})
        self.assertTrue(all(o['jsonrpc'] == '2.0' for o in outputs))

    def test_same_reconcile_cases_have_identical_cli_and_stdio_decisions(self):
        choices = [self.result, self.integrated(), {**self.result, 'status': 'blocked'},
                   {**self.result, 'status': 'completed'}, {**self.result, 'status': 'PASS'},
                   {**self.result, 'status': 'unknown'}]
        for index, result in enumerate(choices):
            self.selection['tasks']['A']['readback'] = self.save_result(result, 'case-' + str(index) + '.json')
            arguments = {'selection': self.selection}
            _, cli_output = self.run_cli('goal', 'reconcile', arguments)
            mcp_output = self.call('goal_reconcile', arguments)
            self.assertEqual(mcp_output['structuredContent'], cli_output)
            self.assertEqual(json.loads(mcp_output['content'][0]['text']), cli_output)
        for mutation in ('missing', 'wrong_goal', 'wrong_repo', 'drift', 'foreign_owner'):
            with self.subTest(mutation=mutation):
                selection = deepcopy(self.selection)
                if mutation == 'missing':
                    del selection['tasks']['A']['readback']
                elif mutation == 'wrong_goal':
                    selection['goal'] = selection['requirements']
                elif mutation == 'wrong_repo':
                    selection['repository'] = str(self.base)
                elif mutation == 'drift':
                    selection['goal']['sha256'] = 'not-an-original-digest'
                else:
                    selection['tasks']['A']['readback'] = self.save_result({**self.result, 'owner': 'fake'}, 'foreign.json')
                _, cli_output = self.run_cli('goal', 'reconcile', {'selection': selection})
                self.assertEqual(self.call('goal_reconcile', {'selection': selection})['structuredContent'], cli_output)

    def test_same_continue_effect_and_resend_decisions(self):
        arguments = self.continuation()
        _, cli_output = self.run_cli('task', 'continue', arguments)
        self.assertEqual(len(self.effects()), 1)
        (self.base / 'owner-state.json').unlink()
        (self.base / 'effects.json').unlink()
        arguments['capture'] = str(self.base / 'mcp-continue')
        mcp_output = self.call('task_continue', arguments)['structuredContent']
        self.assertEqual(mcp_output['status'], cli_output['status'])
        self.assertEqual(mcp_output['boundary'], cli_output['boundary'])
        self.assertEqual(mcp_output['next'], cli_output['next'])
        self.assertEqual(mcp_output['product']['obligations'][0]['status'], cli_output['product']['obligations'][0]['status'])
        self.assertEqual(len(self.effects()), 1)
        _, cli_retry = self.run_cli('task', 'continue', arguments)
        self.assertEqual(self.call('task_continue', arguments)['structuredContent'], cli_retry)
        self.assertEqual(len(self.effects()), 1)
        self.assertEqual(self.request_path.read_bytes(), self.request_bytes)

    def test_invalid_arguments_are_shared_tool_errors(self):
        _, output = self.run_cli('goal', 'reconcile', {'selection': {}, 'argv': ['false']})
        result = self.call('goal_reconcile', {'selection': {}, 'argv': ['false']})
        self.assertTrue(result['isError'])
        self.assertEqual(result['structuredContent'], output)


if __name__ == '__main__':
    unittest.main()
