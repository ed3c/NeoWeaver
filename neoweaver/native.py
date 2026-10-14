"""Single native Codex capture and independent fixed-decision verification.

Filesystem bindings detect drift; they do not authenticate a Provider or prove
sandbox isolation. The Runner never receives the independent Oracle.
"""
from dataclasses import asdict, dataclass, fields
import json
import os
from pathlib import Path
import subprocess

from .patches import OwnerRef
from .replay import PairInspection, RunReadback, inspect_pair
from .snapshot import SnapshotRefusal, StagedSourcePair, validate_source_pair


class NativeRefusal(ValueError):
    def __init__(self, condition):
        self.condition = condition
        super().__init__(condition)


@dataclass(frozen=True, slots=True)
class NativeTask:
    executable: Path
    model: str
    effort: str
    prompt: bytes
    response_schema: bytes
    population: bytes
    timeout_seconds: int
    seed_policy: str


@dataclass(frozen=True, slots=True)
class FixedConditions:
    snapshot_ref: OwnerRef | None = None
    task_ref: OwnerRef | None = None
    environment_ref: OwnerRef | None = None
    solver_ref: OwnerRef | None = None
    seed_policy_ref: OwnerRef | None = None
    budget_ref: OwnerRef | None = None
    baseline_harness_ref: OwnerRef | None = None
    candidate_harness_ref: OwnerRef | None = None


@dataclass(frozen=True, slots=True)
class NativeCapture:
    arm: str
    source: StagedSourcePair
    task: NativeTask
    conditions: FixedConditions
    directory: Path
    argv: tuple[str, ...]
    exit_code: int | None
    timed_out: bool
    launch_error: str | None
    raw: bytes
    stderr: bytes
    last_message: bytes | None
    source_error: str | None
    effect_status: str = "unknown"
    isolation_verified: bool = False
    authorizes_landing: bool = False


@dataclass(frozen=True, slots=True)
class DecisionOracle:
    task: NativeTask
    expected: bytes
    reference: OwnerRef | None = None


@dataclass(frozen=True, slots=True)
class NativeOracleResult:
    status: str
    reasons: tuple[str, ...]
    completed: bool | None
    capture: NativeCapture
    oracle: DecisionOracle
    thread_id: str | None = None
    terminal: str = "unknown"
    usage: tuple[tuple[str, int], ...] = ()
    scope: str = "VALIDATION_ONLY_FIXED_PARSER_DECISIONS"
    authorizes_training: bool = False
    authorizes_landing: bool = False


@dataclass(frozen=True, slots=True)
class NativePairReport:
    oracle_results: tuple[NativeOracleResult, NativeOracleResult]
    readbacks: tuple[RunReadback, RunReadback]
    pair: PairInspection
    launch_mismatches: tuple[str, ...]
    treatment: str
    authorizes_training: bool = False
    authorizes_landing: bool = False


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise NativeRefusal("duplicate_json_key")
        result[key] = value
    return result


def _json(raw):
    def invalid_constant(value):
        raise NativeRefusal("nonfinite_json")
    try:
        return json.loads(raw, object_pairs_hook=_unique, parse_constant=invalid_constant)
    except (ValueError, UnicodeError, RecursionError) as error:
        if isinstance(error, NativeRefusal):
            raise
        raise NativeRefusal("malformed_json") from error


def _serialize(value):
    def encode(obj):
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, bytes):
            return obj.decode("utf-8")
        raise TypeError(type(obj).__name__)
    return json.dumps(value, default=encode, ensure_ascii=False, sort_keys=True).encode()


def _source_error(pair):
    try:
        validate_source_pair(pair)
    except SnapshotRefusal as error:
        return error.condition
    except OSError:
        return "source_unreadable"
    return None


def _check_task(task):
    if type(task) is not NativeTask:
        raise NativeRefusal("invalid_task")
    if (not isinstance(task.executable, Path) or not task.executable.is_absolute()
            or not task.executable.is_file() or not os.access(task.executable, os.X_OK)):
        raise NativeRefusal("executable_unavailable")
    for value in (task.model, task.effort, task.seed_policy):
        if type(value) is not str or not value.strip() or "\0" in value:
            raise NativeRefusal("invalid_launch_selection")
    if type(task.timeout_seconds) is not int or not 1 <= task.timeout_seconds <= 300:
        raise NativeRefusal("invalid_timeout")
    for raw in (task.prompt, task.response_schema, task.population):
        if type(raw) is not bytes or not raw:
            raise NativeRefusal("missing_task_bytes")
        try:
            raw.decode("utf-8")
        except UnicodeError as error:
            raise NativeRefusal("invalid_task_encoding") from error
    if type(_json(task.response_schema)) is not dict:
        raise NativeRefusal("invalid_response_schema")
    _population(task.population)


def _population(raw):
    population = _json(raw)
    if type(population) is not list or not population:
        raise NativeRefusal("invalid_population")
    ids = []
    for case in population:
        if type(case) is not dict or type(case.get("case")) is not str or not case["case"]:
            raise NativeRefusal("invalid_population")
        ids.append(case["case"])
    if len(set(ids)) != len(ids):
        raise NativeRefusal("repeated_population_case")
    return set(ids)


def _launch_record(pair, arm, task, conditions, directory, argv):
    return _serialize(dict(source=asdict(pair), arm=arm, task=asdict(task),
                           conditions=asdict(conditions), directory=directory, argv=argv))


def _process_record(capture):
    return _serialize(dict(exit_code=capture.exit_code, timed_out=capture.timed_out,
                           launch_error=capture.launch_error, source_error=capture.source_error))


def _safe_directory(path):
    requested = Path(path).absolute()
    if requested.is_symlink() or any(parent.is_symlink() for parent in requested.parents):
        raise NativeRefusal("symlink_capture_directory")
    return requested


def run_native_arm(pair: StagedSourcePair, arm: str, task: NativeTask,
                   conditions: FixedConditions, capture_directory: Path) -> NativeCapture:
    """Launch once, retain the raw prefix and check the original source again."""
    _check_task(task)
    if type(conditions) is not FixedConditions or arm not in ("baseline", "candidate"):
        raise NativeRefusal("invalid_launch_input")
    error = _source_error(pair)
    if error:
        raise NativeRefusal(error)
    directory = _safe_directory(capture_directory)
    roots = (pair.baseline.directory, pair.candidate.directory)
    if (directory.exists() or not directory.parent.is_dir()
            or any(directory == root or directory in root.parents or root in directory.parents
                   for root in roots)):
        raise NativeRefusal("capture_exists_or_overlaps_source")
    argv = (str(task.executable), "exec", "--skip-git-repo-check", "--json",
            "--model", task.model, "--sandbox", "read-only",
            "-c", 'approval_policy="never"',
            "-c", "model_reasoning_effort=" + json.dumps(task.effort),
            "--output-schema", str(directory / "schema.json"),
            "--output-last-message", str(directory / "last-message.txt"), "-")
    directory.mkdir(mode=0o700)
    for name, data in (("prompt.txt", task.prompt), ("schema.json", task.response_schema),
                       ("population.json", task.population),
                       ("launch.json", _launch_record(pair, arm, task, conditions, directory, argv))):
        (directory / name).write_bytes(data)
    exit_code, timed_out, launch_error = None, False, None
    with (directory / "raw.ndjson").open("xb") as stdout, (directory / "stderr.bin").open("xb") as stderr:
        try:
            result = subprocess.run(argv, cwd=getattr(pair, arm).directory,
                                    input=task.prompt, stdout=stdout, stderr=stderr,
                                    timeout=task.timeout_seconds, check=False)
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
        except OSError as error:
            launch_error = str(error)
    source_error = _source_error(pair)
    last = directory / "last-message.txt"
    if last.is_symlink() or (last.exists() and not last.is_file()):
        last_message = None
        launch_error = "unsafe_last_message"
    else:
        last_message = last.read_bytes() if last.exists() else None
    capture = NativeCapture(arm, pair, task, conditions, directory, argv, exit_code,
                            timed_out, launch_error, (directory / "raw.ndjson").read_bytes(),
                            (directory / "stderr.bin").read_bytes(), last_message, source_error)
    (directory / "process.json").write_bytes(_process_record(capture))
    return capture


def _capture_error(capture):
    directory = _safe_directory(capture.directory)
    expected = {
        "launch.json": _launch_record(capture.source, capture.arm, capture.task,
                                      capture.conditions, directory, capture.argv),
        "process.json": _process_record(capture),
        "prompt.txt": capture.task.prompt, "schema.json": capture.task.response_schema,
        "population.json": capture.task.population, "raw.ndjson": capture.raw,
        "stderr.bin": capture.stderr, "last-message.txt": capture.last_message,
    }
    for name, raw in expected.items():
        file = directory / name
        if file.is_symlink():
            return "capture_symlink"
        if raw is None:
            if file.exists():
                return "capture_drift"
        elif not file.is_file() or file.read_bytes() != raw:
            return "capture_drift"
    if capture.effect_status != "unknown" or capture.isolation_verified or capture.authorizes_landing:
        return "unsupported_capture_claim"
    return capture.source_error or _source_error(capture.source)


def _decode(capture):
    thread, turn_id, state, last = None, None, "before_thread", None
    usage, finished = (), set()
    provider_error = False
    for line in capture.raw.splitlines():
        if not line.strip():
            raise NativeRefusal("malformed_ndjson")
        event = _json(line)
        if type(event) is not dict or type(event.get("type")) is not str:
            raise NativeRefusal("malformed_event")
        kind = event["type"]
        if kind == "thread.started":
            if state != "before_thread" or type(event.get("thread_id")) is not str or not event["thread_id"]:
                raise NativeRefusal("repeated_or_invalid_thread")
            thread, state = event["thread_id"], "before_turn"
            continue
        if state == "before_thread":
            raise NativeRefusal("event_before_thread")
        if "thread_id" in event and event["thread_id"] != thread:
            raise NativeRefusal("contradictory_thread")
        if kind == "turn.started":
            if state != "before_turn":
                raise NativeRefusal("repeated_or_invalid_turn")
            turn_id, state = event.get("turn_id"), "in_turn"
            if turn_id is not None and (type(turn_id) is not str or not turn_id):
                raise NativeRefusal("invalid_turn_id")
            continue
        if "turn_id" in event and event["turn_id"] != turn_id:
            raise NativeRefusal("contradictory_turn")
        if state in ("completed", "failed"):
            raise NativeRefusal("event_after_terminal")
        if kind == "error":
            provider_error = True
        elif kind.startswith("item."):
            item = event.get("item")
            if type(item) is not dict or type(item.get("type")) is not str or type(item.get("id")) is not str:
                raise NativeRefusal("malformed_item")
            # The installed CLI emits a nonfatal hook warning before turn.started.
            if state != "in_turn" and not (state == "before_turn" and item["type"] == "error"):
                raise NativeRefusal("item_outside_turn")
            if kind not in ("item.started", "item.updated", "item.completed"):
                raise NativeRefusal("unsupported_event")
            if item["id"] in finished:
                raise NativeRefusal("repeated_completed_item")
            if kind == "item.completed":
                finished.add(item["id"])
                if item["type"] == "agent_message":
                    if type(item.get("text")) is not str:
                        raise NativeRefusal("malformed_agent_message")
                    last = item["text"].encode()
        elif kind in ("turn.completed", "turn.failed"):
            if state != "in_turn":
                raise NativeRefusal("terminal_outside_turn")
            state = "completed" if kind == "turn.completed" else "failed"
            if "usage" in event:
                data = event["usage"]
                if type(data) is not dict or any(type(v) is not int or v < 0 for v in data.values()):
                    raise NativeRefusal("malformed_usage")
                usage = tuple(data.items())
        else:
            raise NativeRefusal("unsupported_event")
    if state != "completed" or provider_error or capture.exit_code != 0 or capture.timed_out or capture.launch_error:
        return thread, "partial" if thread else "unknown", None, usage
    if last is None or capture.last_message is None:
        return thread, "partial", None, usage
    if last.strip() != capture.last_message.strip():
        raise NativeRefusal("last_message_mismatch")
    return thread, "completed", last, usage


def _decisions(raw, population):
    data = _json(raw)
    if type(data) is not dict or set(data) != {"decisions"} or type(data["decisions"]) is not list:
        raise NativeRefusal("invalid_decision_shape")
    decisions = {}
    for row in data["decisions"]:
        if type(row) is not dict or set(row) != {"case", "classification", "condition"}:
            raise NativeRefusal("invalid_decision_shape")
        case, classification, condition = row["case"], row["classification"], row["condition"]
        if (type(case) is not str or classification not in ("ParsedProposal", "DiagnosticRefusal")
                or (condition is not None and type(condition) is not str)):
            raise NativeRefusal("invalid_decision_shape")
        if case in decisions:
            raise NativeRefusal("repeated_case")
        decisions[case] = (classification, condition)
    if decisions.keys() != population:
        raise NativeRefusal("case_population_mismatch")
    return decisions


def _inspect(capture, oracle):
    thread, terminal, usage = None, "unknown", ()
    try:
        error = _capture_error(capture)
        if error:
            raise NativeRefusal(error)
        if capture.task != oracle.task:
            raise NativeRefusal("oracle_task_mismatch")
        population = _population(oracle.task.population)
        expected = _decisions(oracle.expected, population)
        thread, terminal, response, usage = _decode(capture)
        if response is None:
            return NativeOracleResult("INCONCLUSIVE", ("missing_native_completion",), None,
                                      capture, oracle, thread, terminal, usage)
        actual = _decisions(response, population)
        mismatches = tuple("decision_mismatch:" + case for case in sorted(population)
                           if actual[case] != expected[case])
        return NativeOracleResult("FAIL_SCOPED" if mismatches else "MATCH_SCOPED", mismatches,
                                  not mismatches, capture, oracle, thread, terminal, usage)
    except NativeRefusal as error:
        return NativeOracleResult("REFUSED", (error.condition,), None, capture, oracle,
                                  thread, terminal, usage)
    except OSError:
        return NativeOracleResult("INCONCLUSIVE", ("capture_unavailable",), None,
                                  capture, oracle, thread, terminal, usage)


def inspect_native_pair(baseline: NativeCapture, candidate: NativeCapture,
                        oracle: DecisionOracle) -> NativePairReport:
    """Verify each original capture, then call the original paired inspector once."""
    if (type(baseline) is not NativeCapture or type(candidate) is not NativeCapture
            or type(oracle) is not DecisionOracle):
        raise NativeRefusal("invalid_inspection_input")
    results = (_inspect(baseline, oracle), _inspect(candidate, oracle))
    mismatches = []
    for field in fields(NativeTask):
        if getattr(baseline.task, field.name) != getattr(candidate.task, field.name):
            mismatches.append("unmatched_launch_" + field.name)
    if baseline.source != candidate.source:
        mismatches.append("unmatched_source_pair")
    if (baseline.arm, candidate.arm) != ("baseline", "candidate"):
        mismatches.append("wrong_capture_arm_order")
    readbacks = []
    for capture, result in zip((baseline, candidate), results):
        conditions = capture.conditions
        readbacks.append(RunReadback(
            arm=capture.arm, snapshot_ref=conditions.snapshot_ref, task_ref=conditions.task_ref,
            environment_ref=conditions.environment_ref, solver_ref=conditions.solver_ref,
            seed_policy_ref=conditions.seed_policy_ref, budget_ref=conditions.budget_ref,
            oracle_ref=oracle.reference,
            harness_ref=getattr(conditions, capture.arm + "_harness_ref"),
            run_ref=OwnerRef("codex", result.thread_id) if result.thread_id else None,
            sandbox_ref=None, capture_ref=OwnerRef("native-runner", str(capture.directory)),
            terminal=result.terminal, completed=result.completed, effect_status="unknown"))
    pair = inspect_pair(*readbacks)
    if mismatches:
        pair = PairInspection("INCONCLUSIVE" if pair.status != "REFUSED" else "REFUSED",
                              pair.reasons + tuple(mismatches), None)
    treatment = ("CONTROL_H0_H0" if baseline.source == candidate.source
                 and not baseline.source.treatment_applied
                 and baseline.source.baseline.manifest == baseline.source.candidate.manifest
                 else "APPLIED_TREATMENT" if baseline.source == candidate.source
                 and baseline.source.treatment_applied else "UNKNOWN")
    return NativePairReport(results, tuple(readbacks), pair, tuple(mismatches), treatment)
