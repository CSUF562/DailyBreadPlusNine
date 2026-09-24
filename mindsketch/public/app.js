const socket = io();
const $ = id => document.getElementById(id);
const lobby = $('lobby'), game = $('game'), waiting = $('waiting'), drawingStage = $('drawingStage'), revealStage = $('revealStage');
let roomCode = null, playerId = null, roundEndsAt = 0, countdown = null, submitted = false;

$('create').onclick = () => socket.emit('room:create', { name: $('name').value }, r => {
  if (!r.ok) return $('lobbyMsg').textContent = r.error || 'Could not create room.';
  enterRoom(r.code, r.playerId);
});
$('join').onclick = () => socket.emit('room:join', { code: $('roomCode').value, name: $('name').value }, r => {
  if (!r.ok) return $('lobbyMsg').textContent = r.error || 'Could not join room.';
  enterRoom(r.code, r.playerId);
});
function enterRoom(code,id){roomCode=code;playerId=id;lobby.classList.add('hidden');game.classList.remove('hidden');$('codeLabel').textContent=code;}

socket.on('room:update', room => {
  if(room.code!==roomCode)return;
  $('playersLabel').textContent=`${room.playerCount}/2`;
  $('roundLabel').textContent=room.round;
  waiting.classList.toggle('hidden', room.phase!=='lobby');
});
socket.on('room:message', text => alert(text));
socket.on('round:start', data => {
  submitted=false; roundEndsAt=data.endsAt; $('prompt').textContent=data.prompt; $('progress').textContent='';
  waiting.classList.add('hidden'); revealStage.classList.add('hidden'); drawingStage.classList.remove('hidden');
  resetCanvas(); startCountdown(); $('submit').disabled=false;
});
socket.on('round:progress', d => $('progress').textContent=`${d.submitted} of ${d.total} drawings submitted`);
socket.on('round:submitted', () => { submitted=true; $('submit').disabled=true; $('progress').textContent='Drawing submitted. Waiting for the other player…'; });
socket.on('round:reveal', data => {
  clearInterval(countdown); drawingStage.classList.add('hidden'); revealStage.classList.remove('hidden');
  $('revealPrompt').textContent=data.prompt; const box=$('drawings'); box.innerHTML='';
  for(const d of data.drawings){const card=document.createElement('article');card.className='drawing-card';const h=document.createElement('h3');h.textContent=d.name;card.appendChild(h);if(d.image){const img=document.createElement('img');img.src=d.image;img.alt=`${d.name}'s drawing`;card.appendChild(img);}else{const p=document.createElement('p');p.textContent='No drawing submitted.';card.appendChild(p);}box.appendChild(card);}
});
$('nextRound').onclick = () => socket.emit('round:next',{code:roomCode});
$('submit').onclick = () => {if(submitted)return;socket.emit('round:submit',{code:roomCode,image:canvas.toDataURL('image/png')},r=>{if(!r.ok)alert(r.error||'Could not submit drawing.');});};

function startCountdown(){clearInterval(countdown);const tick=()=>{const left=Math.max(0,Math.ceil((roundEndsAt-Date.now())/1000));$('timer').textContent=left+'s';if(left<=0){clearInterval(countdown);if(!submitted)$('submit').click();}};tick();countdown=setInterval(tick,250);}

const canvas=$('canvas'),ctx=canvas.getContext('2d');
let drawing=false,current=[],strokes=[],redo=[],last=null,strokeStart=0,metrics=freshMetrics(),mood=freshMood();
function freshMetrics(){return{speed:0,length:0,turns:0,count:0,strokes:0,recentSpeed:0,recentTurn:0,recentFlow:0,lastMoveAt:0}}
function freshMood(){return{energy:0,flow:0,tension:0,playfulness:0,pigment:.4}}
const clamp=(n,a=0,b=1)=>Math.max(a,Math.min(b,n)),lerp=(a,b,t)=>a+(b-a)*t;
function point(e){const r=canvas.getBoundingClientRect();return{x:(e.clientX-r.left)*canvas.width/r.width,y:(e.clientY-r.top)*canvas.height/r.height,t:performance.now()};}
function spread(){return .55+(Number($('spread').value)/100)*1.3}
function updateMood(){mood.energy=clamp(metrics.recentSpeed/1.55);mood.flow=clamp(metrics.recentFlow/250);mood.tension=clamp(metrics.recentTurn);mood.playfulness=clamp(mood.energy*.34+mood.tension*.20+Math.min(metrics.strokes/18,.22));mood.pigment=clamp(.34+(1-mood.energy)*.28+mood.flow*.16,.25,.75);}
function palette(m){if(!$('responsive').checked)return[205,220,190];if(m.tension>.74)return[338,355,315];if(m.energy>.82)return[30,44,15];if(m.playfulness>.64)return[270,292,220];if(m.flow>.50)return[168,188,208];return[202,220,242];}
function dab(x,y,r,m,a,seed,s=spread()){const [h1,h2,h3]=palette(m),R=r*s,g=ctx.createRadialGradient(x,y,0,x,y,R);g.addColorStop(0,`hsla(${h1},62%,56%,${a*1.25})`);g.addColorStop(.42,`hsla(${h2},55%,62%,${a})`);g.addColorStop(.74,`hsla(${h3},48%,68%,${a*.5})`);g.addColorStop(1,`hsla(${h1},40%,72%,0)`);ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,R,0,Math.PI*2);ctx.fill();if(seed%9===0){ctx.fillStyle=`hsla(${h2},55%,58%,${a*.45})`;ctx.beginPath();ctx.arc(x+Math.sin(seed)*r*.15*s,y+Math.cos(seed)*r*.15*s,r*.45*s,0,Math.PI*2);ctx.fill();}}
function segment(a,b,snap,base=0){const dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy),dt=Math.max(1,b.t-a.t),speed=d/dt,hold=b.t-snap.start,vp=clamp(.35+clamp(hold/900)*.35+clamp(speed/1.4)*.2),steps=Math.max(2,Math.floor(d/5)),r=lerp(9,23,vp),alpha=lerp(.045,.14,1-clamp(speed/1.4))*snap.mood.pigment;for(let i=0;i<=steps;i++){const t=i/steps,seed=base+i,j=Math.min(2.4,r*.1)*snap.spread;const x=lerp(a.x,b.x,t)+Math.sin(seed*1.9)*j,y=lerp(a.y,b.y,t)+Math.cos(seed*1.4)*j;dab(x,y,r*(.86+((Math.sin(seed*2.2)+1)/2)*.3),snap.mood,alpha,seed,snap.spread);if(speed>.9&&seed%8===0)dab(x+Math.sin(seed)*18*snap.spread,y+Math.cos(seed)*18*snap.spread,r*.25,snap.mood,alpha*.7,seed+4,snap.spread);}}
function redraw(){ctx.clearRect(0,0,canvas.width,canvas.height);for(const st of strokes){for(let i=1;i<st.points.length;i++)segment(st.points[i-1],st.points[i],st,i+st.seed*17);}}
function resetCanvas(){drawing=false;current=[];strokes=[];redo=[];metrics=freshMetrics();mood=freshMood();ctx.clearRect(0,0,canvas.width,canvas.height);}
canvas.addEventListener('pointerdown',e=>{drawing=true;last=point(e);current=[last];strokeStart=last.t;metrics.strokes++;const idle=metrics.lastMoveAt?Math.max(0,last.t-metrics.lastMoveAt):1000;if(idle>450){const cool=Math.min(.72,idle/2200);metrics.recentSpeed*=1-cool;metrics.recentTurn*=1-cool;metrics.recentFlow*=1-cool*.55;updateMood();}canvas.setPointerCapture?.(e.pointerId)});
canvas.addEventListener('pointermove',e=>{if(!drawing)return;const p=point(e),d=Math.hypot(p.x-last.x,p.y-last.y),dt=Math.max(1,p.t-last.t),instantSpeed=d/dt;metrics.speed+=instantSpeed;metrics.length+=d;metrics.count++;metrics.lastMoveAt=p.t;metrics.recentSpeed=metrics.recentSpeed*.84+instantSpeed*.16;metrics.recentFlow=metrics.recentFlow*.90+d*.10;metrics.recentTurn*=.88;let turn=false;if(current.length>2&&d>2.5){const a=current[current.length-2],b=current[current.length-1],x=Math.atan2(b.y-a.y,b.x-a.x),y=Math.atan2(p.y-b.y,p.x-b.x);let diff=Math.abs(y-x);if(diff>Math.PI)diff=2*Math.PI-diff;if(diff>1.12){metrics.turns++;metrics.recentTurn=clamp(metrics.recentTurn*.76+.24);turn=true;}}updateMood();const snap={mood:{...mood},start:strokeStart,spread:spread(),seed:strokes.length+1};segment(last,p,snap,current.length+snap.seed*19);if(turn&&current.length%5===0)dab(p.x+8,p.y-6,6,snap.mood,.05,snap.seed+current.length,snap.spread);current.push(p);last=p;});
function end(){if(!drawing)return;drawing=false;if(current.length){strokes.push({points:current.slice(),mood:{...mood},start:strokeStart,spread:spread(),seed:strokes.length+1});redo=[];}current=[];}
canvas.addEventListener('pointerup',end);canvas.addEventListener('pointercancel',end);canvas.addEventListener('pointerleave',e=>{if(drawing&&e.buttons===0)end()});
$('undo').onclick=()=>{if(strokes.length){redo.push(strokes.pop());redraw();}};$('redo').onclick=()=>{if(redo.length){strokes.push(redo.pop());redraw();}};$('clear').onclick=resetCanvas;