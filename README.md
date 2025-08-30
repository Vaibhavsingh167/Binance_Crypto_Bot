# TripShield — Tourist Safety & Multi-Modal Incident Response

> **Team:** NextGen Solvers • **Theme:** Smart Travel Buddy

[Watch demo video](LINK_TO_DEMONSTRATION_VIDEO)

---

# Project overview & problem statement chosen

**Problem Statement:** *Tourist Safety & Multi-Modal Incident Response*

**Overview:** Tourism boosts the global economy 🌍 — but tourists face safety risks everywhere. TripShield is a smart safety ecosystem designed to give travelers fast, reliable help when they need it most. It solves common pain points such as:

- Safety risks in unknown areas 🚧
- Difficulty reaching the right emergency services 📞
- Language & cultural barriers 🌐
- Poor/no network in remote areas 📡
- Slow or fragmented emergency response systems 🐢

TripShield provides an integrated solution that combines SOS alerts, real-time risk warnings, AI translation, verified local volunteers, and offline emergency fallbacks (SMS / Bluetooth Mesh / Satellite) so travelers stay safe, connected, and protected—anytime, anywhere.

---

# Key features

- 🚨 **SOS Button** — One tap to request help (works online & offline)
- 🚑 **Multi-modal Response** — Police, ambulance, fire services, and verified volunteers
- 🌩 **Risk Alerts** — Crime, weather, crowding warnings in real-time
- 🌐 **AI Translation** — Breaks language barriers between tourists and responders
- 🤝 **Verified Volunteer Help** — Trusted local assistance network
- ⭐ **Safety Ratings & Feedback** — Community-sourced trust signals
- 📡 **Offline Emergency Mode** — SMS fallback, Bluetooth mesh, satellite links

---

# Workflow (flowchart)

```mermaid
flowchart TD
  Start["Start: Tourist Needs Help"]
  Start -->|"Press SOS"| SOS[SOS Alert]
  Start -->|"Risk Detected"| Risk[Risk Alerts]
  Start -->|"Translate"| Trans[Translation Help]
  Start -->|"Volunteer Requested"| Vol[Volunteer Support]
  SOS --> Dispatch["Help Dispatched + Data Logged"]
  Risk --> Notify[Notifications]
  Trans --> Connect["Connect tourist & responder"]
  Vol --> Nearest["Nearest helper identified"]
  Offline["Offline Mode (Fallback)"] -->|"Fallback comms"| Dispatch
  Dispatch --> SafetyIndex["Safety Ratings & Feedback"]
```

*Text flow summary:* Tourist triggers SOS or receives a risk alert → system determines best response channel (online responders, volunteers, or offline fallback) → responders are dispatched and event is logged → user can rate and leave feedback.

---

# Tech stack

- **Frontend (App & Web):** React Native (Expo) / Flutter, HTML/CSS/JS for web
- **Backend:** Node.js + Express
- **Database:** MongoDB (Atlas) / Firebase
- **Maps & Location:** Google Maps API
- **Notifications & SMS:** Twilio / Firebase Cloud Messaging (FCM)
- **AI/ML:** Risk detection models, translation models (e.g., open-source or cloud ML)
- **Offline support:** Bluetooth Mesh, SMS fallback, Satellite gateways (integration points)
- **Hosting / Cloud:** AWS / Google Cloud

---

# Demo

**Watch the demonstration video:** [LINK\_TO\_DEMONSTRATION\_VIDEO]

*(Replace the placeholder link above with the actual video URL — YouTube/Drive/Vimeo link.)*

---

# Getting started — Step-by-step setup instructions

> The repo is structured (suggested): `/backend` (API & services), `/mobile` (React Native / Expo), `/web` (optional dashboard), `/scripts`.

## Prerequisites

- Node.js (v16+ recommended) and npm / yarn
- MongoDB (local or Atlas) or Firebase project
- Expo CLI (if using React Native + Expo): `npm i -g expo-cli`
- Flutter & Dart (if you choose Flutter)
- Android Studio / Xcode (for mobile emulators)
- Firebase project (for FCM) and Twilio account (for SMS)

## Clone repository

```bash
git clone https://github.com/<your-org>/tripshield.git
cd tripshield
```

## Backend (Node.js / Express)

1. Navigate to the backend folder:

```bash
cd backend
```

2. Install dependencies:

```bash
npm install
```

3. Create environment file from example:

```bash
cp .env.example .env
# then edit .env and paste real credentials
```

4. Start the server (development):

```bash
npm run dev
# or
node src/index.js
```

## Mobile app (React Native - Expo)

1. Navigate to mobile folder:

```bash
cd ../mobile
```

2. Install dependencies:

```bash
npm install
```

3. Copy environment example and configure keys (if used):

```bash
cp env.example .env
```

4. Start Expo:

```bash
expo start
```

5. Scan QR with Expo Go or run an emulator.

### Flutter alternative

If you used Flutter for the mobile client:

```bash
cd mobile_flutter
flutter pub get
flutter run
```

## Web dashboard (optional)

```bash
cd web
npm install
npm start
```

---

# .env.example (sample)

```
# Backend
PORT=4000
MONGO_URI=mongodb+srv://<user>:<pass>@cluster0.mongodb.net/tripshield
JWT_SECRET=your_jwt_secret

# Google
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+11234567890

# Firebase (for push notifications)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_CLIENT_EMAIL=...
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

# Optional cloud keys
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Other
FCM_SERVER_KEY=your_fcm_server_key
```

---

# Running & testing

- Start backend and mobile app locally.
- Use the mobile app to press the SOS button and observe backend logs.
- Example: trigger SOS via curl (replace URL & payload as needed):

```bash
curl -X POST http://localhost:4000/api/v1/sos \
  -H "Content-Type: application/json" \
  -d '{"userId":"demo-user","location":{"lat":12.9716,"lng":77.5946},"message":"Help needed","mode":"online"}'
```

- Check that notifications are sent (FCM/Twilio) and that the event is recorded in the database.

## Simulating offline mode

- **SMS fallback:** Use Twilio test credentials or a Twilio sandbox to receive and inspect SMS events.
- **Bluetooth mesh:** Simulate in-development by emulating peer discovery messages in the backend.
- **Satellite fallback:** Documented integration point for satellite gateway providers — typically requires partner hardware or paid API.

---

# Deployment

- Backend: containerize (Dockerfile) and deploy to AWS ECS / Google Cloud Run.
- Mobile: publish to App Store / Play Store (or distribute via Expo).
- Web: host on Netlify / Vercel / S3 + CloudFront.

---

# API (example endpoints)

- `POST /api/v1/sos` — Trigger SOS
- `GET /api/v1/alerts` — Fetch active risk alerts
- `POST /api/v1/translate` — Request machine translation
- `POST /api/v1/volunteer/register` — Register as a verified volunteer

(Provide full API docs in `/docs` or use Swagger/OpenAPI file.)

---

# Security & privacy notes

- Personal data and location are highly sensitive — store only what’s necessary and follow GDPR/local laws.
- Use TLS/HTTPS everywhere, secure credentials, and rotate API keys periodically.
- Verify volunteers using KYC checks or a trust-verification workflow before dispatching them in real incidents.

---

# Impact

- Faster emergency response times
- Increased trust in destinations
- Enabled support for governments and smart city integrations
- Safer travel increases tourism and local economic benefits

---

# Team — NextGen Solvers

Please replace placeholder names with the real details below.

- **Team Name:** NextGen Solvers
- **Project Lead:** Vaibhav Singh — Product & frontend lead (replace if needed)
- **Backend:** [Name] — Backend & APIs
- **Mobile:** [Name] — Mobile app (React Native / Flutter)
- **ML / Data:** [Name] — Risk detection & translation models
- **Ops / Infra:** [Name] — Deployment & cloud infra

---

# How to contribute

1. Fork the repo
2. Create a feature branch `feat/your-feature`
3. Commit changes & open a PR
4. Add tests and update documentation

---

# License

This project is released under the MIT License. See `LICENSE` for details.

---

# Contact

For questions, feature requests, or collaboration: `team@nextgensolvers.example` (replace with your contact)

---

*Made with ❤️ by NextGen Solvers — Travel safer, travel smarter.*

