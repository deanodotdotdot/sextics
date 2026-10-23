// Discussion permalinks should stay on the site only for mapped project threads.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.join(__dirname,'..'),index=JSON.parse(fs.readFileSync(path.join(root,'discussions/index.json')));
const context={HodgeDrafts:require('../assets/discussion-drafts.js'),HodgeRoutes:require('../assets/routes.js'),window:{},URL,location:{href:'https://hodge.computer/#home'},
  document:{querySelectorAll:()=>[],body:{}},MutationObserver:class{observe(){}},
  fetch:async()=>({ok:true,json:async()=>index})};
vm.runInNewContext(fs.readFileSync(path.join(root,'assets/discussions.js'),'utf8'),context);
(async()=>{
  const api=context.window.HodgeDiscussion;
  assert.equal(api.internalLink('https://github.com/hodge-computer/sextics/discussions/44'),null);
  await api.startLinks();
  for(const [id,entry] of Object.entries(index.instances)){
    const github=`https://github.com/${index.repository}/discussions/${entry.number}`,local=`#case/${id}/discussion`;
    assert.equal(api.internalLink(github),local);
    assert.equal(api.internalLink(github+'/#discussioncomment-19003085'),local+'/19003085');
    assert.equal(api.internalLink(github+'?sort=old#discussioncomment-19003085'),local+'/19003085');
    assert.equal(api.internalLink(github+'#discussion-123'),local);
    assert.equal(api.internalLink(github+'#unrecognized-anchor'),null);
  }
  for(const url of [
    'https://github.com/hodge-computer/sextics/discussions/99999999',
    'https://github.com/another/project/discussions/44#discussioncomment-1',
    'https://github.com/hodge-computer/sextics/pull/44',
    'https://github.com/hodge-computer/sextics/blob/main/README.md',
    'https://github.com/hodge-computer/sextics/discussions/44/other',
    'https://github.com.evil.example/hodge-computer/sextics/discussions/44',
    'https://github.com@evil.example/hodge-computer/sextics/discussions/44',
    'https://name@github.com/hodge-computer/sextics/discussions/44',
    'https://github.com:444/hodge-computer/sextics/discussions/44',
    'javascript:alert(1)', 'mailto:ben@example.com',
    'https://hodge.computer/auth/github', 'https://hodge.computer/#unknown'
  ])assert.equal(api.internalLink(url),null,url);
  assert.equal(api.internalLink('https://GITHUB.com/HODGE-COMPUTER/SEXTICS/discussions/44#discussioncomment-1'),'#case/holdout/discussion/1');
  for(const route of ['#home','#case/holdout','#case/holdout/discussion/19003085','#technical-information/computation','#leaderboard/benediamond'])assert.equal(api.internalLink('https://hodge.computer/'+route),route);
  console.log(`Discussion links: ${Object.keys(index.instances).length} mapped threads, comment permalinks, site routes, and external-link boundaries passed.`);
})().catch(error=>{console.error(error);process.exitCode=1;});
