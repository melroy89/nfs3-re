"""Check relative links in comparison reports, with a bounded plain-heading parser."""
import hashlib
import json
import re
from urllib.parse import unquote
from audit_thrash_loader_difference import ROOT


def anchors(path):
    result=set();counts={}
    for line in path.read_text().splitlines():
        match=re.match(r'^#{1,6} (.+)',line)
        if not match:continue
        name=re.sub(r'[`*_~]','',match[1]).lower()
        name=''.join(c for c in name if c.isalnum() or c in ' -_').replace(' ','-')
        count=counts.get(name,0);counts[name]=count+1
        result.add(name+(f'-{count}' if count else ''))
    return result


def main():
    files=sorted((ROOT/'analysis').glob('original-modern-*.md'))+[ROOT/'analysis/modern-patch-change-catalog.md']
    rows=[];errors=[];total=0
    for path in files:
        raw=path.read_bytes();links=0
        for match in re.finditer(r'\[[^\]]*\]\(([^\s)]+)\)',raw.decode()):
            target=match[1]
            if re.match(r'\w+://',target):continue
            target=unquote(target);relative,_,fragment=target.partition('#')
            destination=(path.parent/relative).resolve() if relative else path.resolve()
            links+=1
            error=None
            if not destination.exists():error='missing file'
            elif fragment and destination.suffix=='.md' and fragment not in anchors(destination):error='missing plain heading anchor'
            if error:errors.append({'source':str(path.relative_to(ROOT)),'target':target,'error':error})
        rows.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'relative_links':links});total+=links
    result={'kind':'comparison-document-relative-link-audit','files':rows,'file_count':len(rows),'relative_link_count':total,'errors':errors,
            'limits':['Recognizes inline Markdown links without spaces or closing parentheses in destination.','Heading anchors use plain ATX heading text with lowercase and punctuation removal; not a full GFM renderer.','Does not validate external URLs, reference-style links, HTML anchors, rendered layout or evidence truth.','Scope is original-modern-*.md reports plus the detailed change catalog, not every repository document.']}
    (ROOT/'analysis/evidence/validation/comparison-document-links.json').write_text(json.dumps(result,indent=2)+'\n')
    assert not errors,errors
    print(f'PASS: {len(rows)} documents, {total} relative links, no missing recognized file/heading targets')


if __name__=='__main__':main()
