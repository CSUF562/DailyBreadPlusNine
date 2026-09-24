import express from 'express';
import http from 'http';
import { Server } from 'socket.io';
import crypto from 'crypto';

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: false } });
const PORT = process.env.PORT || 3000;

app.use(express.static('public'));
app.get('/health', (_req, res) => res.json({ ok: true }));

const rooms = new Map();
const prompts = [
  'A cat wearing a crown', 'A house on the moon', 'A dancing cactus',
  'A fish riding a bicycle', 'A sleepy dragon', 'A piano in the rain',
  'A robot making breakfast', 'A lighthouse in a storm', 'A flying teacup',
  'A tree with a secret door', 'A penguin at the beach', 'A surprised banana'
];

function makeCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  for (let tries = 0; tries < 50; tries++) {
    let code = '';
    for (let i = 0; i < 4; i++) code += chars[crypto.randomInt(chars.length)];
    if (!rooms.has(code)) return code;
  }
  return crypto.randomUUID().slice(0, 6).toUpperCase();
}

function publicRoom(room) {
  return {
    code: room.code,
    playerCount: room.players.length,
    phase: room.phase,
    round: room.round,
    scores: room.players.map(p => ({ id: p.id, name: p.name, score: p.score }))
  };
}

function emitRoom(room) {
  io.to(room.code).emit('room:update', publicRoom(room));
}

function beginRound(room) {
  if (room.players.length !== 2) return;
  room.phase = 'drawing';
  room.round += 1;
  room.prompt = prompts[crypto.randomInt(prompts.length)];
  room.submissions = new Map();
  room.roundEndsAt = Date.now() + 30000;
  io.to(room.code).emit('round:start', {
    round: room.round,
    prompt: room.prompt,
    endsAt: room.roundEndsAt
  });
  emitRoom(room);

  clearTimeout(room.timer);
  room.timer = setTimeout(() => revealRound(room), 30500);
}

function revealRound(room) {
  if (!room || room.phase !== 'drawing') return;
  room.phase = 'reveal';
  const drawings = room.players.map(p => ({
    id: p.id,
    name: p.name,
    image: room.submissions.get(p.id) || null
  }));
  io.to(room.code).emit('round:reveal', { prompt: room.prompt, drawings });
  emitRoom(room);
}

function leaveRooms(socket) {
  for (const [code, room] of rooms) {
    const index = room.players.findIndex(p => p.id === socket.id);
    if (index === -1) continue;
    room.players.splice(index, 1);
    room.submissions?.delete(socket.id);
    socket.leave(code);
    clearTimeout(room.timer);
    room.timer = null;
    room.phase = 'lobby';
    if (room.players.length === 0) rooms.delete(code);
    else {
      io.to(code).emit('room:message', 'The other player left the room.');
      emitRoom(room);
    }
  }
}

io.on('connection', socket => {
  socket.on('room:create', ({ name } = {}, ack = () => {}) => {
    leaveRooms(socket);
    const code = makeCode();
    const room = {
      code,
      players: [{ id: socket.id, name: String(name || 'Player 1').slice(0, 24), score: 0 }],
      phase: 'lobby', round: 0, prompt: null, submissions: new Map(), timer: null
    };
    rooms.set(code, room);
    socket.join(code);
    ack({ ok: true, code, playerId: socket.id });
    emitRoom(room);
  });

  socket.on('room:join', ({ code, name } = {}, ack = () => {}) => {
    leaveRooms(socket);
    code = String(code || '').toUpperCase().trim();
    const room = rooms.get(code);
    if (!room) return ack({ ok: false, error: 'Room not found.' });
    if (room.players.length >= 2) return ack({ ok: false, error: 'That room already has two players.' });
    room.players.push({ id: socket.id, name: String(name || 'Player 2').slice(0, 24), score: 0 });
    socket.join(code);
    ack({ ok: true, code, playerId: socket.id });
    emitRoom(room);
    beginRound(room);
  });

  socket.on('round:submit', ({ code, image } = {}, ack = () => {}) => {
    const room = rooms.get(String(code || '').toUpperCase());
    if (!room || room.phase !== 'drawing') return ack({ ok: false });
    if (!room.players.some(p => p.id === socket.id)) return ack({ ok: false });
    if (typeof image !== 'string' || !image.startsWith('data:image/png;base64,') || image.length > 1500000) {
      return ack({ ok: false, error: 'Invalid drawing.' });
    }
    room.submissions.set(socket.id, image);
    socket.emit('round:submitted');
    io.to(room.code).emit('round:progress', { submitted: room.submissions.size, total: 2 });
    ack({ ok: true });
    if (room.submissions.size >= 2) revealRound(room);
  });

  socket.on('round:next', ({ code } = {}, ack = () => {}) => {
    const room = rooms.get(String(code || '').toUpperCase());
    if (!room || !room.players.some(p => p.id === socket.id)) return ack({ ok: false });
    if (room.phase !== 'reveal') return ack({ ok: false });
    beginRound(room);
    ack({ ok: true });
  });

  socket.on('disconnect', () => leaveRooms(socket));
});

server.listen(PORT, () => console.log(`MindSketch listening on port ${PORT}`));