# GitHub Auto Deploy Setup

This repository already has a GitHub remote:

- `origin`: `https://github.com/cyhsieh1996-stack/La-douceur-balancee-ERP.git`

Recommended deployment split:

1. `web_app/frontend`
   - Deploy with Cloudflare Pages using GitHub integration
   - Build command: `npm run build`
   - Build output directory: `dist`
   - Root directory: `web_app/frontend`

2. `web_app/worker-api`
   - Deploy with GitHub Actions
   - Workflow file: `.github/workflows/deploy-worker-api.yml`

## 1. Push this repository to GitHub

After reviewing local changes, run:

```bash
git add .
git commit -m "Reorganize desktop and web apps for Cloudflare deployment"
git push origin main
```

## 2. Connect Cloudflare Pages to GitHub

Create a new Pages project in Cloudflare. Do not reuse the existing Direct Upload project.

Suggested values:

- Project name: `la-douceur-balancee-erp-web`
- Production branch: `main`
- Framework preset: `Vite`
- Root directory: `web_app/frontend`
- Build command: `npm run build`
- Build output directory: `dist`

Pages environment variables:

- `VITE_API_BASE_URL` = `https://la-douceur-balancee-erp-api.cyhsieh1996.workers.dev`
- `VITE_SUPABASE_URL` = `https://reookovxqozjnefsdczd.supabase.co`
- `VITE_SUPABASE_ANON_KEY` = your publishable key

## 3. Configure GitHub Actions secrets

In GitHub repo settings, add these Actions secrets:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `SUPABASE_SERVICE_ROLE_KEY`

The worker workflow deploys automatically on pushes that touch `web_app/worker-api/**`.

## 4. Cloudflare token scope

Recommended token permissions:

- `Account` -> `Cloudflare Workers Scripts: Edit`
- `Zone` permissions are not required for this worker-only workflow

## 5. One-time note

The current Pages project `la-douceur-balancee-erp` was created via Direct Upload.
Cloudflare treats that as a separate setup from Git-connected Pages, so create a new Pages project for automatic deployments.
