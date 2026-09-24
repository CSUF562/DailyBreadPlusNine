const socket = io();
const $ = id => document.getElementById(id);

const home = $('home');
const friendLobby = $('friendLobby');
const lobby = $('lobby');
const solo = $('solo');
const game = $('game');
const waiting = $('waiting');
const drawingStage = $('drawingStage');
const revealStage = $('revealStage');

let roomCode = null;
let playerId = null;
let roundEndsAt = 0;
let countdown = null;
let submitted = false;

function showOnly(target){
  [home, friendLobby, solo, game].forEach(el => el.classList.toggle('hidden', el !== target));
  window.scrollTo({top:0,behavior:'smooth'});
}

$('openFriend').addEventListener('click', () => showOnly(friendLobby));
$('openMood').addEventListener('click', () => {
  soloPainter.reset();
  $('soloResult').classList.add('hidden');
  showOnly(solo);
});
$('friendBack').addEventListener('click', () => showOnly(home));
$('soloBack').addEventListener('click', () => showOnly(home));
$('gameBack').addEventListener('click', () => location.reload());

$('create').onclick = () => socket.emit('room:create', { name: $('name').value }, r => {
  if (!r.ok) return $('lobbyMsg').textContent = r.error || 'Could not create room.';
  enterRoom(r.code, r.playerId);
});

$('join').onclick = () => socket.emit('room:join', { code: $('roomCode').value, name: $('name').value }, r => {
  if (!r.ok) return $('lobbyMsg').textContent = r.error || 'Could not join room.';
  enterRoom(r.code, r.playerId);
});

function enterRoom(code,id){
  roomCode=code;
  playerId=id;
  $('codeLabel').textContent=code;
  showOnly(game);
}

socket.on('room:update', room => {
  if(room.code!==roomCode)return;
  $('playersLabel').textContent=`${room.playerCount}/2`;
  $('roundLabel').textContent=room.round;
  waiting.classList.toggle('hidden', room.phase!=='lobby');
});

socket.on('room:message', text => alert(text));

socket.on('round:start', data => {
  submitted=false;
  roundEndsAt=data.endsAt;
  $('prompt').textContent=data.prompt;
  $('progress').textContent='';
  waiting.classList.add('hidden');
  revealStage.classList.add('hidden');
  drawingStage.classList.remove('hidden');
  multiPainter.reset();
  startCountdown();
  $('submit').disabled=false;
});

socket.on('round:progress', d => {
  $('progress').textContent=`${d.submitted} of ${d.total} drawings submitted`;
});

socket.on('round:submitted', () => {
  submitted=true;
  $('submit').disabled=true;
  $('progress').textContent='Drawing submitted. Waiting for the other player…';
});

socket.on('round:reveal', data => {
  clearInterval(countdown);
  drawingStage.classList.add('hidden');
  revealStage.classList.remove('hidden');
  $('revealPrompt').textContent=data.prompt;
  const box=$('drawings');
  box.innerHTML='';
  for(const d of data.drawings){
    const card=document.createElement('article');
    card.className='drawing-card';
    const h=document.createElement('h3');
    h.textContent=d.name;
    card.appendChild(h);
    if(d.image){
      const img=document.createElement('img');
      img.src=d.image;
      img.alt=`${d.name}'s drawing`;
      card.appendChild(img);
    }else{
      const p=document.createElement('p');
      p.textContent='No drawing submitted.';
      card.appendChild(p);
    }
    box.appendChild(card);
  }
});

$('nextRound').onclick = () => socket.emit('round:next',{code:roomCode});

$('submit').onclick = () => {
  if(submitted)return;
  socket.emit('round:submit',{
    code:roomCode,
    image:$('canvas').toDataURL('image/png')
  },r=>{
    if(!r.ok)alert(r.error||'Could not submit drawing.');
  });
};

function startCountdown(){
  clearInterval(countdown);
  const tick=()=>{
    const left=Math.max(0,Math.ceil((roundEndsAt-Date.now())/1000));
    $('timer').textContent=left+'s';
    if(left<=0){
      clearInterval(countdown);
      if(!submitted)$('submit').click();
    }
  };
  tick();
  countdown=setInterval(tick,250);
}

function createPainter({canvas, spreadEl, responseScaleEl, responsiveEl, lineWeightEl, lineOpacityEl, undoEl, redoEl, clearEl}){
  const ctx=canvas.getContext('2d');
  let drawing=false,current=[],strokes=[],redo=[],last=null,strokeStart=0;
  let metrics=freshMetrics(),mood=freshMood();

  function freshMetrics(){return{speed:0,length:0,turns:0,count:0,strokes:0,recentSpeed:0,recentTurn:0,recentFlow:0,lastMoveAt:0}}
  function freshMood(){return{energy:0,flow:0,tension:0,playfulness:0,pigment:.4}}
  const clamp=(n,a=0,b=1)=>Math.max(a,Math.min(b,n));
  const lerp=(a,b,t)=>a+(b-a)*t;

  function point(e){
    const r=canvas.getBoundingClientRect();
    return{
      x:(e.clientX-r.left)*canvas.width/r.width,
      y:(e.clientY-r.top)*canvas.height/r.height,
      t:performance.now()
    };
  }

  function spread(){
    return .55+(Number(spreadEl.value)/100)*1.3;
  }

  function responseScale(){
    return Number(responseScaleEl?.value || 55) / 100;
  }

  function solidWeight(){
    return Number(lineWeightEl?.value || 6);
  }

  function solidOpacity(){
    return Number(lineOpacityEl?.value || 100) / 100;
  }

  function isResponsive(){
    return responsiveEl.checked;
  }

  function updateMood(){
    mood.energy=clamp(metrics.recentSpeed/1.55);
    mood.flow=clamp(metrics.recentFlow/250);
    mood.tension=clamp(metrics.recentTurn);
    mood.playfulness=clamp(mood.energy*.34+mood.tension*.20+Math.min(metrics.strokes/18,.22));
    mood.pigment=clamp(.34+(1-mood.energy)*.28+mood.flow*.16,.25,.75);
  }

  function palette(m){
    let hues;
    if(m.tension>.74) hues=[338,355,315];
    else if(m.energy>.82) hues=[30,44,15];
    else if(m.playfulness>.64) hues=[270,292,220];
    else if(m.flow>.50) hues=[168,188,208];
    else hues=[202,220,242];

    const r=responseScale();
    return {
      hues,
      sat:lerp(46,88,r),
      light:lerp(56,71,r),
      variance:lerp(4,22,r),
      accentChance:lerp(.03,.22,r),
      accentShift:lerp(8,36,r)
    };
  }

  function dab(x,y,r,m,a,seed,s=spread()){
    const p=palette(m);
    const [h1,h2,h3]=p.hues;
    const j1=Math.sin(seed*1.7)*p.variance;
    const j2=Math.cos(seed*1.1)*p.variance*.7;
    const j3=Math.sin(seed*2.3)*p.variance*.5;
    const R=r*s;
    const g=ctx.createRadialGradient(x,y,0,x,y,R);
    g.addColorStop(0,`hsla(${h1+j1},${p.sat}%,${p.light}%,${a*1.25})`);
    g.addColorStop(.42,`hsla(${h2+j2},${Math.max(28,p.sat-6)}%,${p.light+5}%,${a})`);
    g.addColorStop(.74,`hsla(${h3+j3},${Math.max(24,p.sat-12)}%,${p.light+10}%,${a*.52})`);
    g.addColorStop(1,`hsla(${h1},${Math.max(24,p.sat-24)}%,${p.light+16}%,0)`);
    ctx.fillStyle=g;
    ctx.beginPath();
    ctx.arc(x,y,R,0,Math.PI*2);
    ctx.fill();

    if(Math.random()<p.accentChance || seed%9===0){
      const accentHue=h2+((seed%2===0)?p.accentShift:-p.accentShift*.5);
      ctx.fillStyle=`hsla(${accentHue},${Math.min(95,p.sat+4)}%,${Math.min(82,p.light+4)}%,${a*.4})`;
      ctx.beginPath();
      ctx.arc(
        x+Math.sin(seed)*r*.18*s,
        y+Math.cos(seed)*r*.18*s,
        r*.42*s,0,Math.PI*2
      );
      ctx.fill();
    }
  }

  function segment(a,b,snap,base=0){
    const dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy);
    const dt=Math.max(1,b.t-a.t);
    const speed=d/dt;
    const hold=b.t-snap.start;
    const vp=clamp(.35+clamp(hold/900)*.35+clamp(speed/1.4)*.2);
    const steps=Math.max(2,Math.floor(d/5));
    const r=lerp(9,23,vp);
    const alpha=lerp(.045,.14,1-clamp(speed/1.4))*snap.mood.pigment;

    for(let i=0;i<=steps;i++){
      const t=i/steps,seed=base+i,j=Math.min(2.4,r*.1)*snap.spread;
      const x=lerp(a.x,b.x,t)+Math.sin(seed*1.9)*j;
      const y=lerp(a.y,b.y,t)+Math.cos(seed*1.4)*j;
      dab(x,y,r*(.86+((Math.sin(seed*2.2)+1)/2)*.3),snap.mood,alpha,seed,snap.spread);

      if(speed>.9&&seed%8===0){
        dab(
          x+Math.sin(seed)*18*snap.spread,
          y+Math.cos(seed)*18*snap.spread,
          r*.25,snap.mood,alpha*.7,seed+4,snap.spread
        );
      }
    }
  }

  function drawSolidSegment(a,b,style={}){
    ctx.save();
    ctx.lineCap='round';
    ctx.lineJoin='round';
    ctx.lineWidth=style.lineWidth ?? solidWeight();
    ctx.strokeStyle=`rgba(38,36,31,${style.opacity ?? solidOpacity()})`;
    ctx.beginPath();
    ctx.moveTo(a.x,a.y);
    ctx.lineTo(b.x,b.y);
    ctx.stroke();
    ctx.restore();
  }

  function redraw(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    for(const st of strokes){
      for(let i=1;i<st.points.length;i++){
        if(st.mode==='solid'){
          drawSolidSegment(st.points[i-1],st.points[i],st);
        }else{
          segment(st.points[i-1],st.points[i],st,i+st.seed*17);
        }
      }
    }
  }

  function reset(){
    drawing=false;
    current=[];
    strokes=[];
    redo=[];
    metrics=freshMetrics();
    mood=freshMood();
    ctx.clearRect(0,0,canvas.width,canvas.height);
  }

  canvas.addEventListener('pointerdown',e=>{
    drawing=true;
    last=point(e);
    current=[last];
    strokeStart=last.t;
    metrics.strokes++;

    const idle=metrics.lastMoveAt?Math.max(0,last.t-metrics.lastMoveAt):1000;
    if(idle>450){
      const cool=Math.min(.72,idle/2200);
      metrics.recentSpeed*=1-cool;
      metrics.recentTurn*=1-cool;
      metrics.recentFlow*=1-cool*.55;
      updateMood();
    }

    canvas.setPointerCapture?.(e.pointerId);
  });

  canvas.addEventListener('pointermove',e=>{
    if(!drawing)return;

    const p=point(e);
    const d=Math.hypot(p.x-last.x,p.y-last.y);
    const dt=Math.max(1,p.t-last.t);
    const instantSpeed=d/dt;

    metrics.speed+=instantSpeed;
    metrics.length+=d;
    metrics.count++;
    metrics.lastMoveAt=p.t;
    metrics.recentSpeed=metrics.recentSpeed*.84+instantSpeed*.16;
    metrics.recentFlow=metrics.recentFlow*.90+d*.10;
    metrics.recentTurn*=.88;

    let turn=false;
    if(current.length>2&&d>2.5){
      const a=current[current.length-2],b=current[current.length-1];
      const x=Math.atan2(b.y-a.y,b.x-a.x);
      const y=Math.atan2(p.y-b.y,p.x-b.x);
      let diff=Math.abs(y-x);
      if(diff>Math.PI)diff=2*Math.PI-diff;
      if(diff>1.12){
        metrics.turns++;
        metrics.recentTurn=clamp(metrics.recentTurn*.76+.24);
        turn=true;
      }
    }

    updateMood();
    const snap={
      mood:{...mood},
      start:strokeStart,
      spread:spread(),
      seed:strokes.length+1,
      mode:isResponsive()?'watercolor':'solid',
      lineWidth:solidWeight(),
      opacity:solidOpacity()
    };

    if(snap.mode==='solid'){
      drawSolidSegment(last,p,snap);
    }else{
      segment(last,p,snap,current.length+snap.seed*19);
      if(turn&&current.length%5===0){
        dab(p.x+8,p.y-6,6,snap.mood,.05,snap.seed+current.length,snap.spread);
      }
    }

    current.push(p);
    last=p;
  });

  function end(){
    if(!drawing)return;
    drawing=false;
    if(current.length){
      strokes.push({
        points:current.slice(),
        mood:{...mood},
        start:strokeStart,
        spread:spread(),
        seed:strokes.length+1,
        mode:isResponsive()?'watercolor':'solid',
        lineWidth:solidWeight(),
        opacity:solidOpacity()
      });
      redo=[];
    }
    current=[];
  }

  canvas.addEventListener('pointerup',end);
  canvas.addEventListener('pointercancel',end);
  canvas.addEventListener('pointerleave',e=>{if(drawing&&e.buttons===0)end()});

  undoEl.addEventListener('click',()=>{if(strokes.length){redo.push(strokes.pop());redraw();}});
  redoEl.addEventListener('click',()=>{if(redo.length){strokes.push(redo.pop());redraw();}});
  clearEl.addEventListener('click',reset);

  return {
    reset,
    getMood:()=>({...mood}),
    hasDrawing:()=>strokes.length>0
  };
}

const multiPainter=createPainter({
  canvas:$('canvas'),
  spreadEl:$('spread'),
  responseScaleEl:$('responseScale'),
  responsiveEl:$('responsive'),
  lineWeightEl:$('lineWeight'),
  lineOpacityEl:$('lineOpacity'),
  undoEl:$('undo'),
  redoEl:$('redo'),
  clearEl:$('clear')
});

const soloPainter=createPainter({
  canvas:$('soloCanvas'),
  spreadEl:$('soloSpread'),
  responseScaleEl:$('soloResponseScale'),
  responsiveEl:$('soloResponsive'),
  lineWeightEl:$('soloLineWeight'),
  lineOpacityEl:$('soloLineOpacity'),
  undoEl:$('soloUndo'),
  redoEl:$('soloRedo'),
  clearEl:$('soloClear')
});

$('soloFinish').addEventListener('click',()=>{
  const result=$('soloResult');
  if(!soloPainter.hasDrawing()){
    result.textContent='Make a few marks first. The canvas has admirable patience, but very little material to interpret.';
    result.classList.remove('hidden');
    return;
  }

  const m=soloPainter.getMood();
  let text='The piece settled into a reflective, cool watercolor rhythm.';
  if(m.tension>.74) text='Sharper directional changes introduced a more concentrated, high-contrast watercolor character.';
  else if(m.energy>.82) text='Quicker recent gestures warmed the palette and created a more energetic watercolor bloom.';
  else if(m.playfulness>.64) text='Varied movement pushed the painting toward a more playful violet-blue rhythm.';
  else if(m.flow>.50) text='Longer, smoother movement encouraged teal and blue washes with a flowing character.';

  result.textContent=text+' This is an expressive reading of the drawing behavior, not an assessment of your emotional state.';
  result.classList.remove('hidden');
});
function syncPainterControls(responsiveId, spreadId, responseScaleId){
  const responsiveEl=$(responsiveId);
  const spreadEl=$(spreadId);
  const responseScaleEl=$(responseScaleId);
  const sync=()=>{
    const enabled=responsiveEl.checked;
    spreadEl.disabled=!enabled;
    responseScaleEl.disabled=!enabled;
  };
  responsiveEl.addEventListener('change',sync);
  sync();
}
syncPainterControls('responsive','spread','responseScale');
syncPainterControls('soloResponsive','soloSpread','soloResponseScale');


// MindSketch soundtrack: two original procedural ambient loops.
const musicPlay=$('musicPlay');
const musicMute=$('musicMute');
const musicVolume=$('musicVolume');
const musicTrack=$('musicTrack');
const musicStatus=$('musicStatus');
const spotifyConnect=$('spotifyConnect');
const spotifyStatus=$('spotifyStatus');

let audioCtx=null;
let masterGain=null;
let soundtrackTimer=null;
let soundtrackPlaying=false;
let soundtrackMuted=false;
let soundtrackTrack=0;
let soundtrackCycle=0;

const soundtrackNames=['Drift','Paper Lanterns'];

function ensureAudio(){
  if(audioCtx) return;
  const AC=window.AudioContext||window.webkitAudioContext;
  if(!AC){
    musicStatus.textContent='Audio is not supported in this browser.';
    musicPlay.disabled=true;
    return;
  }
  audioCtx=new AC();
  masterGain=audioCtx.createGain();
  masterGain.gain.value=Number(musicVolume.value)/100;
  masterGain.connect(audioCtx.destination);
}

function playTone(freq,start,duration,volume=.025,type='sine'){
  const osc=audioCtx.createOscillator();
  const gain=audioCtx.createGain();
  osc.type=type;
  osc.frequency.value=freq;
  gain.gain.setValueAtTime(0,start);
  gain.gain.linearRampToValueAtTime(volume,start+.15);
  gain.gain.exponentialRampToValueAtTime(.0001,start+duration);
  osc.connect(gain);
  gain.connect(masterGain);
  osc.start(start);
  osc.stop(start+duration+.05);
}

function scheduleTrack(trackIndex){
  if(!soundtrackPlaying||!audioCtx)return;
  const now=audioCtx.currentTime+.05;
  const length=16;
  const drift=[
    [220,277.18,329.63,415.3],
    [196,246.94,293.66,369.99]
  ];
  const lanterns=[
    [261.63,329.63,392,493.88],
    [233.08,293.66,349.23,440]
  ];
  const palette=trackIndex===0?drift:lanterns;
  const notes=palette[soundtrackCycle%palette.length];

  notes.forEach((n,i)=>{
    playTone(n,now+i*4,3.6,.018,trackIndex===0?'sine':'triangle');
    playTone(n*2,now+i*4+.2,2.1,.008,'sine');
  });

  soundtrackCycle++;
  musicTrack.textContent=soundtrackNames[trackIndex];
  clearTimeout(soundtrackTimer);
  soundtrackTimer=setTimeout(()=>{
    soundtrackTrack=(soundtrackTrack+1)%2;
    scheduleTrack(soundtrackTrack);
  },length*1000);
}

async function startSoundtrack(){
  ensureAudio();
  if(!audioCtx)return;
  if(audioCtx.state==='suspended') await audioCtx.resume();
  soundtrackPlaying=true;
  musicPlay.textContent='Pause';
  musicStatus.textContent='Playing';
  scheduleTrack(soundtrackTrack);
}

function stopSoundtrack(){
  soundtrackPlaying=false;
  clearTimeout(soundtrackTimer);
  soundtrackTimer=null;
  musicPlay.textContent='Play';
  musicStatus.textContent='Paused';
}

musicPlay.addEventListener('click',()=>{
  if(soundtrackPlaying) stopSoundtrack();
  else startSoundtrack();
});

musicMute.addEventListener('click',()=>{
  ensureAudio();
  soundtrackMuted=!soundtrackMuted;
  if(masterGain) masterGain.gain.value=soundtrackMuted?0:Number(musicVolume.value)/100;
  musicMute.textContent=soundtrackMuted?'Unmute':'Mute';
  musicStatus.textContent=soundtrackMuted?'Muted':(soundtrackPlaying?'Playing':'Ready');
});

musicVolume.addEventListener('input',()=>{
  if(masterGain&&!soundtrackMuted){
    masterGain.gain.value=Number(musicVolume.value)/100;
  }
});

async function initSpotifyAvailability(){
  try{
    const res=await fetch('/api/config',{cache:'no-store'});
    const cfg=await res.json();
    if(!cfg.spotifyEnabled){
      spotifyStatus.textContent='Spotify connection needs a developer Client ID.';
      spotifyConnect.disabled=true;
      return;
    }
    spotifyStatus.textContent='Available to connect';
    spotifyConnect.disabled=false;
    spotifyConnect.addEventListener('click',()=>{
      stopSoundtrack();
      spotifyStatus.textContent='Spotify authorization is configured next.';
      alert('Spotify is enabled on the server. The next step is completing OAuth/PKCE and Web Playback SDK setup for this deployment.');
    });
  }catch{
    spotifyStatus.textContent='Spotify connection unavailable.';
    spotifyConnect.disabled=true;
  }
}
initSpotifyAvailability();
