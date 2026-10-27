(() => {
  'use strict';
  const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
  const motion=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const reveal=$$('.stat,.table-box,.popular-card,.ticket,.dish');
  if(!motion&&'IntersectionObserver'in window){const io=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('is-visible');io.unobserve(e.target)}}),{threshold:.08});reveal.forEach((el,i)=>{el.classList.add('reveal');el.style.transitionDelay=(i%6*45)+'ms';io.observe(el)})}
  function addFilters(container,cards,tabs,label,placeholder,getState){
    if(!container||!cards.length)return;
    const bar=document.createElement('div');bar.className='filterbar';
    bar.innerHTML='<input class="filter-input" type="search" placeholder="'+placeholder+'" aria-label="'+label+'"><div class="filter-tabs" role="group" aria-label="Filter results">'+tabs.map((t,i)=>'<button class="filter-tab'+(i===0?' active':'')+'" type="button" data-filter="'+t[0]+'" aria-pressed="'+(i===0)+'">'+t[1]+'</button>').join('')+'</div><span class="filter-count" aria-live="polite"></span>';
    container.before(bar);let filter='all';const input=$('.filter-input',bar),count=$('.filter-count',bar);
    const update=()=>{let visible=0;cards.forEach(card=>{const ok=card.textContent.toLowerCase().includes(input.value.trim().toLowerCase())&&(filter==='all'||getState(card)===filter);card.hidden=!ok;if(ok)visible++});count.textContent=visible+' of '+cards.length+' results'};
    input.addEventListener('input',update);$$('.filter-tab',bar).forEach(b=>b.addEventListener('click',()=>{filter=b.dataset.filter;$$('.filter-tab',bar).forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b))});update()}));update();
  }
  const grid=$('.table-grid');if(grid){const cards=$$('.table-box',grid);addFilters(grid,cards,[['all','All'],['available','Available'],['occupied','Occupied'],['reserved','Reserved']],'Search tables','Find a table…',card=>['available','occupied','reserved'].find(s=>card.classList.contains(s))||'all')}
  const orders=$('.orders');if(orders){const cards=$$('.ticket',orders);addFilters(orders,cards,[['all','All orders'],['pending','New'],['preparing','Preparing']],'Search kitchen orders','Search table or order…',card=>$('.status',card)?.textContent.toLowerCase().includes('preparing')?'preparing':'pending')}
  const form=$('form[action*="/order/submit/"]');if(form){const inputs=$$('input[type="number"][name^="qty_"]',form),submit=$('.submit',form);if(inputs.length){const summary=document.createElement('div');summary.className='order-summary';summary.hidden=true;summary.innerHTML='<div class="summary-copy"><strong class="summary-total">₹0</strong><span class="summary-count">0 items selected</span></div><span>Order summary ↑</span>';const row=$('.submit-row',form);if(row)form.insertBefore(summary,row);
    const update=()=>{let n=0,total=0;inputs.forEach(input=>{const dish=input.closest('.dish'),q=Math.max(0,Math.floor(Number(input.value)||0)),price=Number($('.dish-price',dish)?.textContent.replace(/[^\d.]/g,''))||0;n+=q;total+=q*price;dish.classList.toggle('selected',q>0)});summary.hidden=n===0;$('.summary-total',summary).textContent=new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:2}).format(total);$('.summary-count',summary).textContent=n+' item'+(n===1?'':'s')+' selected';if(submit)submit.disabled=n===0};
    inputs.forEach(input=>{const wrap=input.closest('.qty-wrap');[-1,1].forEach(step=>{const b=document.createElement('button');b.type='button';b.className='qty-step';b.textContent=step<0?'−':'+';b.setAttribute('aria-label',(step<0?'Decrease':'Increase')+' '+(input.getAttribute('aria-label')||'quantity'));b.addEventListener('click',()=>{input.value=String(Math.max(0,(Number(input.value)||0)+step));input.dispatchEvent(new Event('input',{bubbles:true}))});if(step<0)wrap.insertBefore(b,input);else wrap.append(b)});input.addEventListener('input',update);input.addEventListener('change',update)});
    form.addEventListener('submit',e=>{if(!inputs.some(i=>Number(i.value)>0)){e.preventDefault();inputs[0]?.focus()}});update();
  }}
})();
