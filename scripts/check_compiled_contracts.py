#!/usr/bin/env python3
"""Read declared specification consistency; no parser, semantic judge or runtime."""
from pathlib import Path
import argparse
import json
import sys


def load(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError('duplicate_json_key:' + key)
            out[key] = value
        return out
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def check(root, before=None):
    doc = root / 'docs/compiled'
    record = load(doc / 'specification.json')
    proposal = load(doc / 'card-proposals.json')
    sidecar = load(doc / 'semantic-sidecars.json')
    selection = load(doc / 'patch-scope-selection.json')
    clauses = load(doc / 'coverage.json')
    cards = {c['stable_id']: c for c in record['cards']}
    require(len(cards) == len(record['cards']), 'duplicate_card_identity')
    topics = {(c['series'], c['title']): c['stable_id'] for c in record['cards']}
    require(len(topics) == len(cards), 'ambiguous_card_topic')
    require(len(record['cards']) == len(proposal['cards']), 'card_proposal_count_mismatch')
    for card, semantic in zip(record['cards'], proposal['cards']):
        require((card['series'], card['title']) == (semantic['series'], semantic['title']), 'card_proposal_identity_mismatch')
        payload = '\n'.join(k + ': ' + v for k, v in semantic['semantics'].items())
        require(card['payload'] == payload, 'card_proposal_payload_mismatch:' + card['stable_id'])
        links = []
        for link in semantic['links']:
            target = topics.get((link['target_series'], link['target_topic']))
            require(target is not None, 'unbound_semantic_target:' + card['stable_id'])
            require(bool(link['applicability'].strip()) and bool(link['counterfactual'].strip()), 'missing_link_justification')
            links.append({'relation': link['relation'], 'target': target})
        require(links == card['typed_links'], 'card_link_projection_mismatch:' + card['stable_id'])
    parent_ids = [r['id'] for r in record['requirements']]
    require(len(parent_ids) == len(set(parent_ids)) == 10, 'original_ten_requirements_required')
    require(sidecar['Continuation']['original_requirement_ids'] == parent_ids, 'parent_inventory_changed')
    require(set(selection['requirement_ids']) <= set(parent_ids), 'unknown_selected_requirement')
    require(sidecar['Continuation']['outside_selected_scope'] == [x for x in parent_ids if x not in selection['requirement_ids']], 'outside_inventory_mismatch')
    manifest = sidecar['ScopeManifest']
    require(all(manifest[key] == value for key, value in selection.items()), 'scope_selection_projection_mismatch')
    require(sidecar['PromptDelta']['bullets'] == selection['prompt_delta'], 'prompt_delta_projection_mismatch')
    contract = manifest['local_contract']
    require(contract['outputs'] == ['ParsedProposal', 'DiagnosticRefusal'], 'parser_output_boundary_changed')
    require(contract['effects'] == [] and contract['executes_replay'] is False and contract['executes_training'] is False and contract['authorizes_landing'] is False, 'parser_effect_boundary_changed')
    require(sidecar['authority']['effects'] == [] and sidecar['authority']['authorizes_landing'] is False, 'proposal_authority_changed')
    require(sidecar['PromptDelta']['native_consumption'] == 'NOT_RUN', 'unobserved_native_consumption_claim')
    selected = selection['card_ids']
    require(len(selected) == len(set(selected)) and set(selected) <= cards.keys(), 'invalid_selected_cards')
    entries = manifest['card_applicability']
    require(len(entries) == len(cards) and {x['card_id'] for x in entries} == cards.keys(), 'applicability_inventory_mismatch')
    roles = {x['card_id']: x for x in entries}
    for identity, entry in roles.items():
        require(entry['role'] in ('local_exit', 'local_control', 'constraint', 'strategy', 'context_only', 'deferred'), 'unknown_applicability_role')
        require(entry['selected'] is (identity in selected), 'selected_applicability_mismatch')
        require((entry['role'] not in ('context_only', 'deferred')) is entry['selected'], 'deferred_card_selected_as_local')
    local_exit = [identity for identity in selected if roles[identity]['role'] == 'local_exit']
    local_controls = [identity for identity in selected if roles[identity]['role'] == 'local_control']
    require(local_exit == ['SPEC-trainability-boundary'], 'parser_local_exit_changed')
    require(local_controls == ['V-trainability-discriminating-controls'], 'parser_local_control_changed')
    require(set(manifest['covered_parent_clauses']) == set(selection['requirement_ids']), 'missing_selected_clause_coverage')
    require(set(sidecar['Continuation']['remaining_selected_requirement_clauses']) == set(selection['requirement_ids']), 'missing_remaining_parent_clause')
    required_gaps = {'REQ-two-policies': 'K-training-data-and-token-provenance-unavailable', 'REQ-learning-dataset': 'K-training-data-and-token-provenance-unavailable', 'REQ-plugin-transfer': 'K-native-codex-transfer-has-no-observed-consumer'}
    for req in record['requirements']:
        if req['id'] in required_gaps:
            require(required_gaps[req['id']] in req.get('depends_on', []), 'missing_declared_gap_dependency:' + req['id'])
    if before is not None:
        prior = load(before / 'docs/compiled/specification.json')
        require([(r['id'], r['statement'], r['falsifier']) for r in prior['requirements']] == [(r['id'], r['statement'], r['falsifier']) for r in record['requirements']], 'original_requirement_meaning_changed')
        require(load(before / 'docs/compiled/coverage.json') == clauses, 'original_clause_inventory_changed')
        require([(c['stable_id'], c['canonical_key']) for c in prior['cards']] == [(c['stable_id'], c['canonical_key']) for c in record['cards']], 'card_history_identity_changed')
        for previous, current in zip(prior['cards'], record['cards']):
            old_content = {k: v for k, v in previous.items() if k != 'revision'}
            new_content = {k: v for k, v in current.items() if k != 'revision'}
            require(current['revision'] == previous['revision'] + (old_content != new_content), 'invalid_card_revision:' + current['stable_id'])
    return {'valid': True, 'requirements': len(parent_ids), 'cards': len(cards), 'selected_cards': len(selected), 'proof_ceiling': 'DECLARED_ARTIFACT_CONSISTENCY_ONLY', 'source_semantics': 'UNVERIFIED', 'parser_implementation': 'NOT_RUN', 'native_pclass': 'NOT_RUN', 'effects': []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--before', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.root, args.before), ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
