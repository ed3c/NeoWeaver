import {spawnSync} from 'node:child_process';
import {readFileSync, writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {resolve, dirname} from 'node:path';
const artifact = dirname(fileURLToPath(import.meta.url));
const root = resolve(artifact, '../../..');
const observations = [];
const commands = [
  ['python3', ['-m', 'py_compile', 'neoweaver/product_goal.py', 'neoweaver/product_cli.py', 'neoweaver/mcp_stdio.py', 'scripts/neoweaver.py', 'tests/test_product_goal.py', 'tests/test_product_cli.py', 'tests/test_mcp_cli.py', 'tests/test_agent_cli_harness.py', 'docs/experiments/neo-product-cli-loop/fault_replay.py']],
  ...['test_product_goal.py','test_product_cli.py','test_mcp_cli.py','test_agent_cli_harness.py','test_task_adapter.py'].map(pattern => ['python3', ['-B','-m','unittest','discover','-s','tests','-p', pattern,'-v']]),
  ['python3', ['-B','scripts/neoweaver.py','goal','reconcile','--help']],
  ['python3', ['-B','scripts/neoweaver.py','mcp']],
  ['python3', ['-B','docs/experiments/neo-product-cli-loop/fault_replay.py']],
];
for (const [command,args] of commands) {
  const r = spawnSync(command,args,{cwd:root,encoding:'utf8',input:'',timeout:120000});
  observations.push({command:[command,...args], status:r.error?.code === 'ENOENT' ? 'NOT_RUN' : r.status === 0 ? 'PASS' : 'FAIL', exit:r.status, error:r.error?.code ?? null, stdout:r.stdout ?? '',stderr:r.stderr ?? ''});
}
const spec = JSON.parse(readFileSync(resolve(root,'docs/compiled/specification.json')));
observations.push({command:['node','source-only inventory read'],status:spec.requirements.length===10 && spec.cards.length===44 ? 'PASS' : 'FAIL',requirements:spec.requirements.length,cards:spec.cards.length,evidence_ceiling:'SOURCE_ONLY_NOT_PYTHON_AST_OR_RUNTIME'});
const immutable = ['neoweaver/task_adapter.py','scripts/run_task_adapter.py','scripts/loop.py','docs/compiled/specification.json','docs/specs/neoweaver-product-program.md'];
observations.push({command:['node','read source digests'],status:'OBSERVED',files:immutable.map(path=>({path,sha256:createHash('sha256').update(readFileSync(resolve(root,path))).digest('hex')})),note:'Digests identify inspected bytes, not Native execution or authority.'});
const report = {acceptance_observed:false, observations, tlc:'NOT_RUN: Java/TLC/mise absent; did not invoke auto-installer', native_effect:'NOT_RUN',host_installation:'NOT_RUN',fresh_consumer_schema:'NOT_RUN'};
writeFileSync(resolve(artifact,'observations.json'),JSON.stringify(report,null,2)+'\n');
process.stdout.write(JSON.stringify(report,null,2)+'\n');
