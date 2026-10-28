from pathlib import Path
import gzip,json,hashlib
r=Path(__file__).resolve().parent
m=json.loads((r/'PUBLIC-MANIFEST.json').read_text())
for name,entry in m['compressed_inputs'].items():
 data=gzip.decompress((r/entry['gzip']).read_bytes())
 assert hashlib.sha256(data).hexdigest()==entry['sha256'],name
 p=r/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
print('Verified and unpacked',len(m['compressed_inputs']),'exact input/result files')
