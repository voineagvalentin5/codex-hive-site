/* Codex Hive cohesion — header, mobile menu, progress, reveal */
(function(){
  var d=document,b=d.body,t=d.querySelector('.menu-toggle'),nav=d.getElementById('site-nav'),p=d.querySelector('.progress span');
  function setMenu(open){b.classList.toggle('menu-open',open);if(t){t.setAttribute('aria-expanded',open?'true':'false');t.setAttribute('aria-label',open?'Close menu':'Open menu');}}
  if(t){t.addEventListener('click',function(){setMenu(!b.classList.contains('menu-open'))});}
  if(nav){nav.addEventListener('click',function(e){if(e.target.closest('a'))setMenu(false)});}
  d.addEventListener('keydown',function(e){if(e.key==='Escape'&&b.classList.contains('menu-open')){setMenu(false);t&&t.focus();}});
  window.matchMedia('(min-width:901px)').addEventListener('change',function(m){if(m.matches)setMenu(false)});
  var tick=false;function upd(){var m=Math.max(d.documentElement.scrollHeight-innerHeight,1);if(p)p.style.transform='scaleX('+Math.min(Math.max(scrollY/m,0),1)+')';tick=false;}
  addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(upd)}},{passive:true});upd();
  var els=d.querySelectorAll('.reveal');
  if('IntersectionObserver' in window&&!matchMedia('(prefers-reduced-motion: reduce)').matches){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -8% 0px'});
    els.forEach(function(el){io.observe(el)});
  }else{els.forEach(function(el){el.classList.add('in')})}
  var v=d.querySelector('.globe-stage video');
  if(v&&matchMedia('(prefers-reduced-motion: reduce)').matches){v.removeAttribute('autoplay');v.pause();}
})();
/* same-origin embed frames (Daphnis Wake simulation, Hive Talks player): fit height to content */
(function(){
  var fr=[].slice.call(document.querySelectorAll('iframe[data-fit]'));
  function fit(i){try{var d=i.contentDocument;if(d&&d.body){var h=Math.max(d.documentElement.scrollHeight,d.body.scrollHeight);if(h>50)i.style.height=h+'px';}}catch(e){}}
  fr.forEach(function(i){i.addEventListener('load',function(){fit(i);setTimeout(function(){fit(i)},800);setTimeout(function(){fit(i)},2500)});});
  var t;addEventListener('resize',function(){clearTimeout(t);t=setTimeout(function(){fr.forEach(fit)},200)});
})();
