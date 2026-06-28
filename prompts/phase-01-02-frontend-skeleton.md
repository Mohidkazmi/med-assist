# Phase 1.2: Frontend Skeleton Prompt

Below is the exact development prompt used to initialize the React + Vite + TypeScript + Tailwind CSS frontend service skeleton for the **AI Medical Scribe Platform** monorepo:

```markdown
You are a Senior Frontend Architect.

Before writing any code:

1. Inspect the complete repository.
2. Understand the existing backend.
3. Do not recreate existing files.
4. Modify only what is required.
5. Keep the architecture modular and scalable.

Project:
AI Medical Scribe Platform

Current Status:
- Docker working
- PostgreSQL working
- FastAPI backend completed
- Swagger working
- Health endpoint working

Goal:
Implement ONLY the frontend skeleton.

Technology Stack:

- React 18
- Vite
- TypeScript
- Tailwind CSS
- React Router DOM
- Axios
- ESLint
- Prettier

Create this structure:

frontend/

src/

components/
pages/
layouts/
routes/
hooks/
services/
assets/
styles/

App.tsx
main.tsx

Requirements:

1. Configure React using Vite.
2. Configure TypeScript.
3. Configure Tailwind CSS.
4. Configure React Router.
5. Configure Axios with a reusable API client.
6. Create a Home page.
7. Create a Login page placeholder.
8. Add navigation between pages.
9. Display project title:
   "AI Medical Scribe Platform"

10. Configure Docker for frontend.
11. Add frontend service to docker-compose.yml.
12. Enable hot reload.
13. Read backend URL from environment variables.
14. Do NOT call backend APIs yet.
15. Do NOT implement authentication.
16. Do NOT create dashboards.
17. Do NOT create business logic.
18. Do NOT use Stitch yet.

Expected Pages:

/

Shows:

AI Medical Scribe Platform

Backend Status:
(Not Connected Yet)

Button:
Go to Login

------------------------

/login

Shows:

Login Screen

"This screen will be implemented later."

Button:

Back to Home

After implementation:

Explain:

- Every file created.
- Folder structure.
- Docker configuration.
- Tailwind setup.
- Routing.
- Axios configuration.
- Environment variables.
- How to run.
- How to verify frontend.

Stop after Phase 1.2 only.

Do not implement any extra functionality.
```
