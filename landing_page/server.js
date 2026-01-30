import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
import "dotenv/config";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import { db } from "./db.js";


const app = express();
app.use(cors());
app.use(express.json());
// ============================
// ADMIN KEY middleware
// ============================
function adminKey(req, res, next) {
  const key = req.headers["x-admin-key"];
  if (!key || key !== process.env.ADMIN_KEY) {
    return res.status(401).json({ message: "Unauthorized (admin key)" });
  }
  next();
}


const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Serve static site
app.use(express.static(path.join(__dirname, "public")));
function auth(req, res, next) {
  const h = req.headers.authorization || "";
  const token = h.startsWith("Bearer ") ? h.slice(7) : null;
  if (!token) return res.status(401).json({ message: "No token" });

  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    return res.status(401).json({ message: "Invalid token" });
  }
}

app.post("/api/signup", async (req, res) => {
  const { name, email, password } = req.body || {};
  if (!email || !password) return res.status(400).json({ message: "Missing email/password" });

  const [exists] = await db.query("SELECT id FROM users WHERE email = ?", [email]);
  if (exists.length) return res.status(409).json({ message: "Email already used" });

  const password_hash = await bcrypt.hash(password, 12);

  await db.query(
    "INSERT INTO users (name, email, password_hash) VALUES (?,?,?)",
    [name || null, email, password_hash]
  );

  res.json({ ok: true });
});


// API: demo
app.post("/api/demo", async (req, res) => {
  const { name, email, business, message } = req.body || {};
  if (!name || !email || !business) {
    return res.status(400).json({ message: "Missing fields (name/email/business)" });
  }

  await db.query(
    "INSERT INTO demo_requests (name, email, business, message) VALUES (?,?,?,?)",
    [name, email, business, message || null]
  );

  res.json({ ok: true });
});



// API: login (demo)
app.post("/api/login", async (req, res) => {
  const { email, password } = req.body || {};
  if (!email || !password) return res.status(400).json({ message: "Missing email/password" });

  const ip = req.headers["x-forwarded-for"]?.toString().split(",")[0]?.trim() || req.socket.remoteAddress;
  const ua = (req.headers["user-agent"] || "").toString().slice(0, 255);

  const [rows] = await db.query(
    "SELECT id, name, email, password_hash, role FROM users WHERE email = ?",
    [email]
  );

  // user not found => log failed
  if (!rows.length) {
    await db.query(
      "INSERT INTO login_logs (user_id, email, success, ip, user_agent) VALUES (NULL, ?, 0, ?, ?)",
      [email, ip || null, ua || null]
    );
    return res.status(401).json({ message: "Invalid credentials" });
  }

  const user = rows[0];
  const ok = await bcrypt.compare(password, user.password_hash);

  // log attempt
  await db.query(
    "INSERT INTO login_logs (user_id, email, success, ip, user_agent) VALUES (?, ?, ?, ?, ?)",
    [user.id, email, ok ? 1 : 0, ip || null, ua || null]
  );

  if (!ok) return res.status(401).json({ message: "Invalid credentials" });

  const token = jwt.sign(
    { id: user.id, email: user.email, name: user.name, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: "7d" }
  );

  res.json({
    ok: true,
    token,
    user: { id: user.id, name: user.name, email: user.email, role: user.role }
  });
});

// Fallback (optional): if you browse /login etc.
app.get("/api/me", auth, (req, res) => {
  res.json({ ok: true, user: req.user });
});

// Admin: stats
app.get("/api/admin/stats", adminKey, async (req, res) => {
  const [[u]] = await db.query("SELECT COUNT(*) as total FROM users");
  const [[d]] = await db.query("SELECT COUNT(*) as total FROM demo_requests");
  const [[l]] = await db.query("SELECT COUNT(*) as total FROM login_logs");
  const [[ok]] = await db.query("SELECT COUNT(*) as total FROM login_logs WHERE success=1");
  res.json({
    users: u.total,
    demos: d.total,
    logins: l.total,
    login_success: ok.total
  });
});

// Admin: list users (signups)
app.get("/api/admin/users", adminKey, async (req, res) => {
  const [rows] = await db.query(
    "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC LIMIT 500"
  );
  res.json(rows);
});

// Admin: list demo requests
app.get("/api/admin/demos", adminKey, async (req, res) => {
  const [rows] = await db.query(
    "SELECT id, name, email, business, message, created_at FROM demo_requests ORDER BY created_at DESC LIMIT 500"
  );
  res.json(rows);
});

// Admin: list login logs
app.get("/api/admin/logins", adminKey, async (req, res) => {
  const [rows] = await db.query(
    "SELECT id, user_id, email, success, ip, user_agent, created_at FROM login_logs ORDER BY created_at DESC LIMIT 500"
  );
  res.json(rows);
});


const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`✅ Server running: http://localhost:${PORT}`));
