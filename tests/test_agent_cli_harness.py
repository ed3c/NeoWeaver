"""control-cli harness on the actual entrypoint; no external Host or real tasks."""
import json
import os
import pty
import select
import signal
import subprocess
import time
import unittest

from test_product_cli import CLI, TransportFixture
from test_mcp_cli import INIT, READY, message


class AgentCLIHarnessTests(TransportFixture):
    def test_layered_help_through_a_real_pty(self):
        for arguments in ([], ['goal', '--help'], ['goal', 'reconcile', '--help'],
                          ['goal', 'refresh', '--help'], ['task', 'continue', '--help'],
                          ['training', 'inspect', '--help'], ['mcp', '--help'], ['schema', '--help']):
            master, slave = pty.openpty()
            process = subprocess.Popen(CLI + (arguments or ['--help']), stdin=slave, stdout=slave, stderr=slave)
            os.close(slave)
            output = b''
            deadline = time.monotonic() + 5
            try:
                while time.monotonic() < deadline:
                    ready, _, _ = select.select([master], [], [], 0.1)
                    if ready:
                        try:
                            chunk = os.read(master, 4096)
                        except OSError:
                            break
                        if not chunk:
                            break
                        output += chunk
                    elif process.poll() is not None:
                        break
                self.assertEqual(process.wait(timeout=2), 0)
                self.assertIn(b'Examples:', output)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
                os.close(master)

    def test_interrupt_keeps_capture_unknown_and_original_request_unchanged(self):
        for surface in ('cli', 'mcp'):
            with self.subTest(surface=surface):
                self.config['delay'] = 10
                self.save_config()
                arguments = self.continuation()
                arguments['capture'] = str(self.base / ('interrupt-' + surface))
                if surface == 'cli':
                    command = CLI + ['task', 'continue', '--stdin']
                    raw = json.dumps(arguments)
                else:
                    command = CLI + ['mcp']
                    raw = ''.join(json.dumps(r) + '\n' for r in
                                  (INIT, READY, message(2, 'tools/call', {'name': 'task_continue', 'arguments': arguments})))
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=True, start_new_session=True)
                try:
                    process.stdin.write(raw)
                    process.stdin.flush()
                    if surface == 'cli':
                        process.stdin.close()
                        process.stdin = None
                    deadline = time.monotonic() + 5
                    owner_ready = False
                    while time.monotonic() < deadline:
                        try:
                            json.loads((self.base / 'owner-state.json').read_text())
                            owner_ready = bool(self.effects())
                        except (OSError, json.JSONDecodeError):
                            owner_ready = False
                        if owner_ready:
                            break
                        time.sleep(0.01)
                    self.assertTrue(owner_ready)
                    self.assertEqual(len(self.effects()), 1)
                    os.killpg(process.pid, signal.SIGTERM)
                    process.communicate(timeout=5)
                    _, retry = self.run_cli('task', 'continue', arguments)
                    self.assertEqual(retry['status'], 'unknown')
                    self.assertEqual(len(self.effects()), 1)
                    _, readback = self.run_cli('goal', 'refresh', {'selection': self.selection,
                                                'capture': str(self.base / ('readback-' + surface))})
                    self.assertEqual(len(readback['locally_completed']), 1)
                    self.assertEqual(len(self.effects()), 1)
                    self.assertEqual(self.request_path.read_bytes(), self.request_bytes)
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.communicate(timeout=5)
                (self.base / 'effects.json').unlink()
                (self.base / 'owner-state.json').unlink()

    def test_parallel_mcp_same_capture_does_not_duplicate_effect(self):
        arguments = self.continuation()
        raw = ''.join(json.dumps(r) + '\n' for r in
                      (INIT, READY, message(2, 'tools/call', {'name': 'task_continue', 'arguments': arguments})))
        processes = [subprocess.Popen(CLI + ['mcp'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True) for _ in range(2)]
        for process in processes:
            process.stdin.write(raw)
            process.stdin.close()
            process.stdin = None
        outputs = []
        for process in processes:
            out, err = process.communicate(timeout=20)
            self.assertEqual(process.returncode, 0, err)
            outputs.append(json.loads(out.splitlines()[-1])['result']['structuredContent'])
        self.assertEqual(sum(o['status'] == 'unknown' for o in outputs), 1)
        self.assertEqual(len(self.effects()), 1)


if __name__ == '__main__':
    unittest.main()
