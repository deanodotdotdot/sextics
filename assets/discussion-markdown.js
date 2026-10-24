/* Bundled Markdown + KaTeX; HTML and links pass through the shared sanitizer. */
(()=>{
  'use strict';
  const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const math=(tex,display)=>`<span data-discussion-math="${escape(tex)}" data-display="${display?'yes':'no'}"></span>`;
  const inlineRule=/^(?:\$`([^\n]*?)`\$|\\\(([\s\S]*?)\\\)|\$(?!\s|\$)((?:\\.|[^\n$\\])+?)\$(?!\d))/;
  const displayRule=/^ {0,3}(?:\$\$([\s\S]*?)\$\$|\\\[([\s\S]*?)\\\])(?:[ \t]*\n|$)/;
  const parser=new marked.Marked({gfm:true,breaks:true,renderer:{
    code(token){if(token.lang?.trim()==='math')return math(token.text,true);return false;},
    image({href,text}){return `<a href="${escape(href)}">${escape(text||'View image')} ↗</a>`;}
  },extensions:[
    {name:'discussionDisplayMath',level:'block',start(src){return src.search(/\$\$|\\\[/);},tokenizer(src){const m=displayRule.exec(src);if(m)return {type:'discussionDisplayMath',raw:m[0],text:m[1]??m[2]};},renderer(token){return math(token.text,true);}},
    {name:'discussionInlineMath',level:'inline',start(src){return src.search(/\$|\\\(/);},tokenizer(src){const m=inlineRule.exec(src);if(m)return {type:'discussionInlineMath',raw:m[0],text:m[1]??m[2]??m[3]};},renderer(token){return math(token.text,false);}}
  ]});
  function render(target,source,baseUrl='https://github.com/hodge-computer/sextics/',remaining=Infinity){
    const fragment=DOMPurify.sanitize(parser.parse(String(source||'').slice(0,65536)),{
      RETURN_DOM_FRAGMENT:true,ALLOW_DATA_ATTR:false,
      ALLOWED_TAGS:['p','br','strong','em','del','a','ul','ol','li','blockquote','pre','code','h1','h2','h3','h4','h5','h6','hr','table','thead','tbody','tr','th','td','span','input','details','summary'],
      ALLOWED_ATTR:['href','title','start','type','checked','disabled','open','data-discussion-math','data-display']
    });
    // Trim preview nodes before typesetting mathematics that will not be shown.
    let truncated=false;
    function shorten(parent){
      for(const child of [...parent.childNodes]){
        if(remaining<=0){child.remove();truncated=true;continue;}
        if(child.nodeType===3){
          const text=child.textContent;
          if(text.length>remaining){child.textContent=text.slice(0,remaining).replace(/\s+\S*$/,'');truncated=true;}
          remaining-=text.length;
        }else if(child.nodeType===1){
          if(child.matches('[data-discussion-math],pre'))
            remaining-=(child.getAttribute('data-discussion-math')||child.textContent).length;
          else shorten(child);
        }
      }
    }
    if(Number.isFinite(remaining))shorten(fragment);
    if(truncated)fragment.append('…');
    for(const link of fragment.querySelectorAll('a')){
      try{const href=link.getAttribute('href');if(!href)throw Error();const url=new URL(href,baseUrl);if(!['https:','http:','mailto:'].includes(url.protocol))throw Error();link.href=url.href;link.target='_blank';link.rel='noopener noreferrer nofollow';}
      catch{link.removeAttribute('href');}
    }
    for(const input of fragment.querySelectorAll('input')){if(input.type!=='checkbox')input.remove();else input.disabled=true;}
    for(const node of fragment.querySelectorAll('[data-discussion-math]')){
      const tex=node.getAttribute('data-discussion-math'),display=node.getAttribute('data-display')==='yes';
      node.className=display?'discussion-math-display':'discussion-math-inline';
      node.removeAttribute('data-discussion-math');node.removeAttribute('data-display');
      try{if(tex.length>5000)throw Error();katex.render(tex,node,{displayMode:display,throwOnError:false,trust:false,strict:'ignore',maxExpand:200,maxSize:10,macros:{}});}
      catch{node.textContent=tex;}
    }
    target.replaceChildren(fragment);
  }
  window.HodgeDiscussionMarkdown={render};
})();
