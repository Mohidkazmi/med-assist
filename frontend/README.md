# AI Medical Scribe Platform - Frontend Application

This is the frontend single page application (SPA) for the **AI Medical Scribe Platform** built with **React 18**, **Vite**, **TypeScript**, and **Tailwind CSS**.

---

## Folder Structure

The application source layout is structured as follows:

```text
frontend/
├── src/
│   ├── assets/               # Local images, SVG assets, and static media
│   ├── components/           # Reusable generic UI components (buttons, badges)
│   ├── layouts/              # Structural wrappers (MainLayout.tsx with navbar & footer)
│   │   └── MainLayout.tsx
│   ├── pages/                # Page route views
│   │   ├── Home.tsx          # Platform landing page with backend connection indicator
│   │   └── Login.tsx         # Login placeholder screen
│   ├── routes/               # Declarative client-side routing definitions
│   │   └── index.tsx         # React Router DOM v6 mapping
│   ├── services/             # API client services
│   │   └── api.ts            # Axios instances loaded with VITE_API_URL settings
│   ├── styles/               # Global CSS files containing Tailwind rules
│   │   └── index.css
│   ├── App.tsx               # Entry application runner rendering the RouterProvider
│   └── main.tsx              # DOM mounting and StrictMode bootstrap
├── Dockerfile                # NodeJS-based local container configuration
├── vite.config.ts            # Host bindings & VM-friendly hot-reload configurations
├── tailwind.config.js        # Content file patterns and theme extensions
├── postcss.config.js         # CSS Postprocessor mapping
├── tsconfig.json             # TypeScript rules definition
└── package.json              # Scripts & dependency definitions
```

---

## Core Technologies & Dependencies

* **React 18 & TypeScript**: Core runtime and type safety engine.
* **Vite**: Rapid, modern ES-module frontend build tool.
* **Tailwind CSS (3.4.x)**: Utility-first CSS framework for modern, premium styling.
* **React Router DOM (6.x)**: Client-side routing engine.
* **Axios**: HTTP library for API consumption (loaded with base URL configuration).

---

## Local Development Setup

### 1. Installation
Ensure you are in the `frontend/` directory, then run:
```bash
# Bypass global cache permission conflicts if they exist
npm install --cache .npm-cache
```

### 2. Configure Environment Variables
Copy and set your local variables template:
```bash
# In the parent root workspace folder:
cp .env.example .env
```
Ensure `VITE_API_URL` is set to point to your backend API server (e.g. `http://localhost:8001/api/v1`).

### 3. Run Locally (Without Docker)
```bash
npm run dev
```
The server will start on [http://localhost:5173](http://localhost:5173).

---

## Docker Integration

To build and run the frontend inside a container:
```bash
# From the parent root workspace folder:
docker compose up -d frontend
```
The Docker container exposes Vite on port `5173` with host bindings enabled, meaning you can access it on your host machine at [http://localhost:5173](http://localhost:5173). Changes made to `src/` are hot-reloaded inside the container instantly via mounting.
