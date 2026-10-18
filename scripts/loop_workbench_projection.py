#!/usr/bin/env python3
"""Pure read-only projection: existing opaque original references -> UI envelope.

No storage, network, evaluator execution, reward inference, identity synthesis,
or owner authorization. A schema file documents this proposed display format.
"""
from math import isfinite


class ProjectionRefusal(ValueError):
    pass


def ref(value, *, optional=False):
    if optional and value is None:
        return None
    if not isinstance(value, str) or not 0 < len(value) <= 512:
        raise ProjectionRefusal("Missing or invalid original reference")
    return value


def project_episode(source):
    if not isinstance(source, dict):
        raise ProjectionRefusal("Episode source must be an object")
    for key in ("run_ref", "episode_ref", "task_ref", "environment_ref", "actor_ref"):
        ref(source.get(key))
    original_reward = source.get("reward")
    original_verification = source.get("verification")
    original_termination = source.get("termination")
    original_harness = source.get("harness")
    if not all(isinstance(v, dict) for v in (
            original_reward, original_verification, original_termination, original_harness)):
        raise ProjectionRefusal("No original producer's complete episode readback")
    status = original_verification.get("status")
    if status not in ("PASS", "FAIL", "INCONCLUSIVE", "NOT_RUN"):
        raise ProjectionRefusal("Unsupported verification state")
    verifier_ref = ref(original_verification.get("verifier_ref"), optional=True)
    if status in ("PASS", "FAIL") and verifier_ref is None:
        raise ProjectionRefusal("Claimed verifier result lacks original receipt")
    reward_status = original_reward.get("status")
    if reward_status not in ("observed", "unknown", "not_applicable"):
        raise ProjectionRefusal("Unsupported reward disposition")
    value, source_ref = original_reward.get("value"), ref(
        original_reward.get("source_ref"), optional=True)
    if reward_status == "observed":
        if (type(value) not in (int, float) or not isfinite(value)
                or source_ref is None or verifier_ref is None):
            raise ProjectionRefusal("Observed reward lacks independent evidence")
    elif value is not None:
        raise ProjectionRefusal("Unknown reward must be null, not zero or simulated")
    phase = original_harness.get("phase")
    if phase not in ("propose", "probe", "compose", "reflect", "unknown"):
        raise ProjectionRefusal("Unknown harness phase")
    end_status = original_termination.get("status")
    if end_status not in ("done", "truncated", "unknown"):
        raise ProjectionRefusal("Unknown episode termination")
    actions, observations = source.get("actions"), source.get("observations")
    if not isinstance(actions, list) or not isinstance(observations, list):
        raise ProjectionRefusal("Original action/observation refs are required")
    return {
        "schema_version": 0,
        **{key: ref(source[key]) for key in
           ("run_ref", "episode_ref", "task_ref", "environment_ref", "actor_ref")},
        "harness": {"phase": phase,
                    "baseline_ref": ref(original_harness.get("baseline_ref"), optional=True),
                    "candidate_ref": ref(original_harness.get("candidate_ref"), optional=True)},
        "actions": [ref(x) for x in actions],
        "observations": [ref(x) for x in observations],
        "verification": {"status": status, "verifier_ref": verifier_ref},
        "reward": {"status": reward_status, "value": value,
                   "source_ref": source_ref},
        "termination": {"status": end_status,
                        "reason_ref": ref(original_termination.get("reason_ref"), optional=True)},
    }
