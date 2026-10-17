(()=>{
const parse=c=>{const m=c.match(/[\d.]+/g).map(Number);return {r:m[0],g:m[1],b:m[2],a:m.length>3?m[3]:1}};
const lum=({r,g,b})=>{const f=v=>{v/=255;return v<=.03928?v/12.92:((v+.055)/1.055)**2.4};return .2126*f(r)+.7152*f(g)+.0722*f(b)};
const over=(t,b)=>({r:t.r*t.a+b.r*(1-t.a),g:t.g*t.a+b.g*(1-t.a),b:t.b*t.a+b.b*(1-t.a),a:1});
const bgOf=el=>{let L=[],e=el;while(e){const c=parse(getComputedStyle(e).backgroundColor);if(c.a>0)L.push(c);if(c.a>=1)break;e=e.parentElement}let base={r:255,g:255,b:255,a:1};for(let i=L.length-1;i>=0;i--)base=over(L[i],base);return base};
const out=[];
document.querySelectorAll('body *').forEach(el=>{
 const txt=[...el.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim()).map(n=>n.textContent.trim()).join(' ');
 if(!txt)return; const cs=getComputedStyle(el),r=el.getBoundingClientRect();
 if(r.width===0||r.height===0||cs.visibility==='hidden'||cs.display==='none')return;
 if(el.closest('[disabled],[aria-disabled=true],.past,.sr,script,style,.lb-b'))return;
 const bg=bgOf(el),f=over(parse(cs.color),bg),L1=lum(f),L2=lum(bg),ratio=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
 const size=parseFloat(cs.fontSize),bold=parseInt(cs.fontWeight)>=700,large=size>=24||(size>=18.66&&bold),need=large?3:4.5;
 if(ratio<need)out.push({el:el.tagName.toLowerCase()+'.'+String(el.className||'').slice(0,26),txt:txt.slice(0,34),ratio:+ratio.toFixed(2),need});
});
return out})()
