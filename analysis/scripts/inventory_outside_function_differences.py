"""Classify byte patterns outside saved Modern function ranges, not semantics."""
import hashlib
import json
import re
from collections import Counter
import pefile
from audit_thrash_loader_difference import ROOT



# Curated routes to inspected research, not automatic semantic-coverage credit.
LARGEST_RUN_ROUTES = [
    ('004b59c0', 'Renderer initializer tail', 'original-modern-renderer-initialization.md', 'Mapped Modern counterpart; complete driver/callee behavior remains partial.'),
    ('004b5e50', 'Corruption diagnostic', 'original-modern-startup-requirements.md', 'Body/tables and terminal API checked; pre-exit hooks and caller preconditions unresolved.'),
    ('004b5ea0', 'Texture-resource log', 'original-modern-startup-requirements.md', 'Threshold and formatted output checked; descriptor units and output destination unresolved.'),
    ('004b5f10', 'Resource admission checks', 'original-modern-startup-requirements.md', 'Mapped Modern counterpart; API failures and directory selection remain partial.'),
    ('004b6020', 'Subsystem setup', 'original-modern-resolution-defaults.md', 'Mapped Modern counterpart; all downstream initialization effects not qualified.'),
    ('004b6250', 'Shutdown envelope', 'original-modern-input-worker.md', 'Mapped Modern counterpart; no join/runtime shutdown proof.'),
    ('004b62a0', 'Six-byte remote prefix test', 'original-modern-startup-requirements.md', 'Body and compare semantics checked; global-source ownership and other callers pending.'),
    ('004b6320', 'Installation/media admission', 'original-modern-startup-requirements.md', 'Branches, CWD construction and shared enumeration checked; API failures/provider results untested.'),
    ('004b6400', 'Renderer registry values', 'original-modern-registry.md', 'Original removed helper checked; Modern driver-specific replacement mapping incomplete.'),
    ('004b64c0', 'Renderer description registry value', 'original-modern-registry.md', 'Original removed helper checked; error/fallback and external registry behavior untested.'),
    ('004b6520', 'Desktop registry path', 'original-modern-registry.md', 'Original screenshot dependency checked; query failure and lifecycle remain partial.'),
    ('004b6590', 'DirectDraw capability probe', 'original-modern-startup-requirements.md', 'Return paths and caller gate checked; provider interfaces/runtime untested.'),
]

def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    source=ROOT/'analysis/evidence/audits/original-modern-function-diff.json'
    inv=json.loads(source.read_text());images=[]
    for label in ('original','official_modern'):
        row=inv['binaries'][label];raw=(ROOT/row['path']).read_bytes();assert sha(raw)==row['sha256']
        images.append(pefile.PE(data=raw))
    start=0x401000;length=inv['code_byte_coverage']['code_bytes'];end=start+length
    old,new=[pe.get_data(start-0x400000,length) for pe in images];assert len(old)==len(new)==length
    covered=bytearray(length)
    for row in inv['functions']:
        for lo,hi in row['ranges']:
            a=max(start,int(lo,16));b=min(end,int(hi,16))
            if a<b:covered[a-start:b-start]=b'\x01'*(b-a)
    intervals=[];all_changes=Counter();i=0
    while i<length:
        if covered[i]:i+=1;continue
        lo=i
        while i<length and not covered[i]:i+=1
        hi=i;changes=[j for j in range(lo,hi) if old[j]!=new[j]]
        if not changes:continue
        counts=Counter(new[j] for j in changes);all_changes.update(counts)
        runs=[]
        for j in changes:
            if runs and runs[-1][1]==j:runs[-1][1]+=1
            else:runs.append([j,j+1])
        intervals.append({'start':f'{start+lo:08x}','end_exclusive':f'{start+hi:08x}','span_bytes':hi-lo,'changed_bytes':len(changes),'changed_modern_nop_bytes':counts[0x90],'changed_modern_zero_bytes':counts[0],'changed_other_bytes':len(changes)-counts[0x90]-counts[0],'original_sha256':sha(old[lo:hi]),'modern_sha256':sha(new[lo:hi]),'changed_runs':[[f'{start+a:08x}',f'{start+b:08x}'] for a,b in runs]})
    total=sum(all_changes.values());assert total==inv['code_byte_coverage']['changed_bytes_outside_modern_function_ranges']==21926
    assert all_changes[0x90]==18098 and all_changes[0]==605
    intervals.sort(key=lambda x:(-x['changed_bytes'],x['start']))
    original_source=inv['original_function_inventory']
    original_raw=(ROOT/original_source['path']).read_bytes();assert sha(original_raw)==original_source['sha256']
    original_functions=json.loads(original_raw)['functions']
    nop_runs=[]
    for interval in intervals:
        lo=int(interval['start'],16)-start;hi=int(interval['end_exclusive'],16)-start
        for match in re.finditer(b'\x90{64,}',new[lo:hi]):
            a=lo+match.start();b=lo+match.end()
            changed=sum(x!=y for x,y in zip(old[a:b],new[a:b]))
            if not changed:continue
            overlapping=[]
            for function in original_functions:
                if any(int(x,16)<start+b and start+a<int(y,16) for x,y in function['ranges']):overlapping.append(function['entry'])
            nop_runs.append({'start':f'{start+a:08x}','end_exclusive':f'{start+b:08x}','length':b-a,'changed_bytes':changed,'original_sha256':sha(old[a:b]),'modern_sha256':sha(new[a:b]),'original_autoanalysis_entries_overlapping':overlapping})
    nop_runs.sort(key=lambda r:(-r['changed_bytes'],r['start']))
    result={'kind':'outside-saved-function-byte-pattern-inventory','source':str(source.relative_to(ROOT)),'source_sha256':sha(source.read_bytes()),'baselines':{k:inv['binaries'][k] for k in ('original','official_modern')},'code_start':f'{start:08x}','code_end_exclusive':f'{end:08x}','counts':{'intervals_with_changes':len(intervals),'changed_bytes':total,'modern_nop':all_changes[0x90],'modern_zero':all_changes[0],'modern_other':total-all_changes[0x90]-all_changes[0]},'limits':['Byte-pattern classification only; NOP replacements are not proven unreachable or harmless padding.','Maximal intervals outside saved Modern body union; contain unchanged bytes and may cross old function/data boundaries.','Saved body gaps, removed original epilogues, moved code and unrecognized functions require disassembly/correspondence work.'],'intervals':intervals}
    result['long_nop_replacements']={'minimum_run_length':64,'run_count':len(nop_runs),'changed_bytes':sum(row['changed_bytes'] for row in nop_runs),'original_inventory_sha256':original_source['sha256'],'runs':nop_runs,'limits':'NOP runs clipped to uncovered intervals; original autoanalysis entries are overlap locators, not proven semantic counterparts.'}
    largest = nop_runs[0]
    assert largest['start'] == '004b5db1' and largest['end_exclusive'] == '004b67b0'
    assert {row[0] for row in LARGEST_RUN_ROUTES} == set(largest['original_autoanalysis_entries_overlapping'])
    routes = []
    for entry,role,report,remaining in LARGEST_RUN_ROUTES:
        path = ROOT/'analysis'/report
        assert path.is_file() and entry in path.read_text()
        routes.append({'original_entry': entry, 'role': role, 'report': 'analysis/'+report,
            'report_sha256': sha(path.read_bytes()), 'remaining': remaining,
            'status': 'entry classified; semantic validation partial'})
    result['largest_run_research_routes'] = {'start': largest['start'], 'end_exclusive': largest['end_exclusive'],
        'entries': routes, 'limit': 'All overlapping entry locators have research routes; not every byte/callee/runtime effect is explained.'}
    idle_interval = next(row for row in intervals if row['start']=='004961ef')
    assert idle_interval['end_exclusive']=='004962c2' and idle_interval['changed_bytes']==195
    idle_parts = []
    for lo,hi,role in [(0x4961ef,0x4961f0,'Leading Modern NOP'),
                       (0x4961f0,0x496200,'Modern filename pointers; original switch code targets'),
                       (0x496200,0x4962c2,'Modern idle controller; prefix of longer original controller')]:
        a,b = lo-start,hi-start
        idle_parts.append({'start': f'{lo:08x}', 'end_exclusive': f'{hi:08x}',
            'bytes': hi-lo, 'role': role, 'original_hex': old[a:b].hex(),
            'modern_hex': new[a:b].hex(), 'original_sha256': sha(old[a:b]),
            'modern_sha256': sha(new[a:b])})
    assert new[0x4961ef-start]==0x90
    assert new[0x4961f0-start:0x496200-start] == bytes.fromhex('acbe5300b8be5300c4be5300d0be5300')
    idle_report = ROOT/'analysis/original-modern-idle-movie.md'
    result['idle_interval_partition'] = {'interval': '004961ef..004962c2',
        'parts': idle_parts, 'report': str(idle_report.relative_to(ROOT)),
        'report_sha256': sha(idle_report.read_bytes()),
        'limit': 'Partition and existing semantic route verified; no runtime playback or new function creation.'}
    hud_interval = next(row for row in intervals if row['start']=='0045e95a')
    assert hud_interval['end_exclusive']=='0045f300' and hud_interval['changed_bytes']==242
    hud_changes = [start+i for i in range(0x45e95a-start,0x45f300-start) if old[i]!=new[i]]
    assert len(hud_changes)==242 and all(0x45e980<=va<0x45ea74 for va in hud_changes)
    hud_parts = []
    for lo,hi,role in [(0x45e95a,0x45e960,'Unchanged leading bytes'),
                       (0x45e960,0x45f07c,'Complete HUD settings initializer'),
                       (0x45f07c,0x45f300,'Unchanged trailing bytes; not classified as padding')]:
        a,b=lo-start,hi-start
        hud_parts.append({'start': f'{lo:08x}', 'end_exclusive': f'{hi:08x}',
            'bytes': hi-lo, 'role': role, 'changed_bytes': sum(x!=y for x,y in zip(old[a:b],new[a:b])),
            'original_sha256': sha(old[a:b]), 'modern_sha256': sha(new[a:b])})
    hud_report=ROOT/'analysis/original-modern-hud-settings-policy.md'
    result['hud_interval_partition'] = {'interval': '0045e95a..0045f300',
        'parts': hud_parts, 'report': str(hud_report.relative_to(ROOT)),
        'report_sha256': sha(hud_report.read_bytes()),
        'limit': 'All interval differences localized to documented policy; equality of surrounding bytes is not full semantic equivalence.'}
    cascade_interval=next(row for row in intervals if row['start']=='00461cf4')
    assert cascade_interval['end_exclusive']=='004628d0' and cascade_interval['changed_bytes']==207
    cascade_parts=[]
    for lo,hi,role in [(0x461cf4,0x461d00,'Unchanged leading bytes'),
                       (0x461d00,0x462314,'Cascade renderer'),
                       (0x462314,0x4624a0,'Unchanged intervening code/alignment'),
                       (0x4624a0,0x4628c8,'Cascade input compared envelope'),
                       (0x4628c8,0x4628d0,'Modern NOP alignment after unconditional jump')]:
        a,b=lo-start,hi-start
        cascade_parts.append({'start': f'{lo:08x}', 'end_exclusive': f'{hi:08x}',
            'bytes': hi-lo, 'role': role, 'changed_bytes': sum(x!=y for x,y in zip(old[a:b],new[a:b])),
            'original_sha256': sha(old[a:b]), 'modern_sha256': sha(new[a:b])})
    assert cascade_parts[0]['changed_bytes']==cascade_parts[2]['changed_bytes']==0
    assert new[0x4628c8-start:0x4628d0-start]==b'\x90'*8
    result['cascade_interval_partition']={'interval':'00461cf4..004628d0','parts':cascade_parts,
        'reports':['analysis/original-modern-car-alias.md','analysis/original-modern-common-menu-buttons.md'],
        'limit':'Renderer/input deltas routed to existing paired audits; alignment classification is local, not exclusion of alternate entry or complete UI equivalence.'}
    (ROOT/'analysis/evidence/audits/outside-function-differences.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Changed code outside saved function ranges','','Generated by `python3 analysis/scripts/inventory_outside_function_differences.py`. [Complete machine-readable inventory](evidence/audits/outside-function-differences.json), [baseline comparison](original-modern-differences.md).','',f"The **21,926 differing bytes** outside the saved Modern body union occupy **{len(intervals)} maximal uncovered intervals with changes**: **18,098** have Modern byte`90` (NOP), **605** have byte`00`, and **3,223** have other values. These are byte classes, not semantic explanations or completion percentages.",'','Intervals include unchanged bytes and can contain removed original code, old epilogues, embedded data or unrecognized Modern code. A NOP replacement is not automatically dead code or padding. Ranges are half-open. Full hashes and every contiguous changed run are retained in JSON.','', '## Largest intervals to triage','','Ranked by changed bytes; the complete inventory contains every interval, not only this table. Before following an entry, search existing reports for the span or its original counterpart. Establish instruction/data boundaries and callers before assigning semantics.','','| Start | End exclusive | Span bytes | Changed | Modern NOP | Modern zero | Other |','|---|---|---:|---:|---:|---:|---:|']
    for r in intervals[:25]:lines.append(f"| `{r['start']}` | `{r['end_exclusive']}` | {r['span_bytes']} | {r['changed_bytes']} | {r['changed_modern_nop_bytes']} | {r['changed_modern_zero_bytes']} | {r['changed_other_bytes']} |")
    lines+=['','## Large NOP replacements and reused research','',f'Within these uncovered intervals, **{len(nop_runs)}** Modern NOP runs of at least64 bytes contain **{sum(row["changed_bytes"] for row in nop_runs)}** changed bytes. Their exact original/Modern hashes and overlapping original autoanalysis entries are retained in JSON. Run lengths include original bytes already equal to NOP; they are not changed-byte counts.','', '| NOP start | End exclusive | Length | Changed bytes | Original entries overlapping |','|---|---|---:|---:|---:|']
    for row in nop_runs[:10]:lines.append(f'| `{row["start"]}` | `{row["end_exclusive"]}` | {row["length"]} | {row["changed_bytes"]} | {len(row["original_autoanalysis_entries_overlapping"])} |')
    lines+=['','The largest run `004b5db1..004b67b0` overlaps original startup/setup, registry and worker routines. Reuse the [startup counterpart](original-modern-startup-requirements.md), [renderer setup](original-modern-resolution-defaults.md), [registry](original-modern-registry.md) and [input-worker](original-modern-input-worker.md) comparisons: same-address NOP removal does not mean those entire features disappeared. Their mapped Modern counterparts are elsewhere. These chapters explain selected functions, not every byte of this large run.','', 'The next run `004f85c0..004f8b50` overlaps original renderer loader/initialization code. Reuse [renderer loading](original-modern-renderer-loading.md) and [initialization](original-modern-renderer-initialization.md). The [renderer snapshot follow-up](original-modern-renderer-loading.md#removed-original-renderer-snapshot-bank) now classifies original restore/save routines in `00517170..00517580` as an eight-slot renderer snapshot bank replaced by Modern NOPs. Remaining overlap entries still require classification; no generic dead-code claim is made.']
    lines+=['','The [CPU calibration follow-up](original-modern-cpu-tier.md#removed-calibration-helper-span) classifies `004f1ff0..004f22b0` as the old estimator tail and calibration helpers, including conditional RDTSC and a timestamp-polled DIV workload. Modern fills the span with NOPs; CPU feature-based tier selection remains separately documented.']
    lines+=['','The [DDE browser-code follow-up](original-modern-removed-dde.md) identifies original URL-command construction and its callback beneath the 621-byte NOP run `004901c3..00490430`. The run begins inside an original branch operand; lack of autoanalysis entries is not evidence of padding. Original caller reachability remains unresolved, and Modern still retains all seven DDE imports.']
    lines += [
        '', '## Mechanism triage from existing comparisons', '',
        'These links reconcile selected outside-body spans with already inspected mechanisms. They are not declarations that every instruction, caller or output in a row has been validated. In particular, the Modern saved-body boundary can split an original instruction or function.', '',
        '| Outside span / NOP run | Existing explanation | Remaining boundary |',
        '|---|---|---|',
        '| `00464fca..004654c0` | [Control-component key callback](original-modern-control-component-keys.md) localizes all52 differing bytes to paired269-byte callback004651e0, absent from both saved function inventories. | Smaller step deltas, component cancellation and raw return2-to0 are verified; InteriorBx binding and selected-entry return normalization established; other callers/rendered behavior remain unresolved. |',
        '| `0041d6e4..0041d7e4` | [Parameter presets](original-modern-parameter-preset.md) identifies the complete256-byte Modern WORD table immediately after its shortened initializer; original instructions occupy this address range. | Selector/auxiliary-state bounds, complete original arithmetic and runtime effects remain unresolved; Modern table bytes are data, not instruction candidates. |',
        '| `00472e1d..00472f20` | [Graphics defaults](original-modern-resolution-defaults.md#tier-tables-occupy-former-original-code-final-loadstore-mismatch) identifies54 table bytes at00472e20..00472e56 with surrounding NOPs, replacing original initializer instructions. | Final EDX-load/EAX-store mismatch is retained; intended last-field policy, valid tier producers and runtime effects remain bounded. |',
        '| `004961ef..004962c2` | [Idle movies](original-modern-idle-movie.md) partitions this interval into one leading NOP,16 bytes of filename pointers replacing original code targets, and194 bytes of Modern controller code. | Availability/admission/cycling differences have paired static evidence; actual playback, wrapping-state invariants and historical introduction remain unverified. |',
        '| `0045e95a..0045f300` | [HUD settings policy](original-modern-hud-settings-policy.md) localizes all242 changed bytes to0045e980..0045ea74 inside complete1820-byte initializer0045e960; surrounding interval bytes match. | Official asset/list binding and selected callback suppression are verified static; full input/render lifecycle, localization and runtime outcomes remain unverified. |',
        '| `00461cf4..004628d0` | [Cascade renderer](original-modern-car-alias.md) and [input handler](original-modern-common-menu-buttons.md) account for changed function regions; final eight bytes are Modern NOP alignment after its unconditional return-tail jump. | Surrounding spans match; external helper semantics, alternate entries, event/render output and backup asset provenance remain bounded. |',
        '| `0040fffb..00410330` | [Music selection](original-modern-music-selection.md) captures original selector `0040ffd0` and loader `00410030..00410329`; Modern uses its separately mapped selection/loading policy. | NOP interval starts inside the original selector; distribution, historical attribution and actual playback remain separate questions. |',
        '| `0047f9bd..0047fbe0` | [Border geometry](original-modern-border-geometry.md) retains the complete longer original builder from `0047f650`; Modern uses a shorter builder plus inset wrapper and thickness updater. | Repeated coordinate/thickness work is replaced, but every quad/UV assignment and rendered result is not validated. |',
        '| `0048575b..0048582c` | [HUD layout](original-modern-hud-layout.md) maps the original file/token parser and profile copying to Modern embedded presets and scaling. | This interval begins in the old parser; the unchanged shared-frame continuation at `0048582c` must not receive an invented standalone ABI. |',
        '| `004901c3..00490430` | [DDE code](original-modern-removed-dde.md) maps URL command construction and callback under the NOP run; Modern uses the earlier addresses for unrelated overlay/progress helpers. | No original direct callers identified; dormancy remains inferred and imports remain present. |',
        '| `004befcd..004bf110` | [Display modes](original-modern-display-modes.md) and [mode selection](original-modern-mode-selection.md) compare original apply routine `004bef50` with shorter Modern `004beeb0` and factored preparation helper. | Both versions have a mode-call failure test. Removed tail bytes do not prove that failure handling was newly introduced. |',
        '| `004ccdb4..004cce90` | [Window handling](original-modern-window-handling.md) maps the old focus-handler tail, focus-loss, close, pending-latch and no-op destroy callbacks to revised registrations and Modern callbacks. | Some behavior moves rather than disappears; the new power callback has a separately documented ABI/result anomaly. Runtime focus/power behavior is untested. |',
        '| `004fd280..004fd490` | [Projection](original-modern-projection.md) identifies the old origin/centre setter, angle/scale builder and conversion wrapper; Modern removes their calls from the compared wrapper. | Lookup-table interpretation, other caller coverage and runtime projection equivalence remain unresolved. |',
        '', 'Intervals not listed here remain available in the full JSON inventory. A row here is a research-routing decision, not semantic coverage credit. Whole-code counts and the stage limits above remain unchanged.'
    ]
    lines += ['', '## Largest removed startup span: entry-by-entry handoff', '',
        'All12 original autoanalysis entry locators overlapping `004b5db1..004b67b0` now have explicit research routes below. The script checks exact entry-set equality and report/address presence, retaining report hashes in JSON. This is reviewed classification/navigation, not a claim that every byte, callee, alternate path or runtime effect is understood. The first row is only the overlapping tail of a longer initializer; entries alone do not partition every byte of the NOP run.', '',
        '| Original entry | Inspected role | Evidence route | Remaining boundary |', '|---|---|---|---|']
    for entry,role,report,remaining in LARGEST_RUN_ROUTES:
        lines.append(f'| `{entry}` | {role} | [Report]({report}) | {remaining} |')
    lines += ['', 'Do not reopen these entries solely because they lie outside saved Modern bodies. Select a specific remaining boundary from the linked reports. Work elsewhere in the337-interval inventory remains independent; no whole-audit percentage is derived from this twelve-entry handoff.']
    lines+=['','This inventory closes the missing address/ranking map for the outside-body bytes. Their semantic classification remains pending. No binary, Ghidra database or runtime state was modified.']
    (ROOT/'analysis/original-modern-outside-function-index.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(result['counts']))


if __name__=='__main__':main()
