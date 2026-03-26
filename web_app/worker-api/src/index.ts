import { Hono } from "hono";
import { cors } from "hono/cors";
import { createMaterial, getMaterialById, listMaterials } from "./modules/materials";
import { createProduct, listProducts } from "./modules/products";

type Bindings = {
  APP_NAME: string;
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
  SUPABASE_PUBLISHABLE_KEY?: string;
};

const app = new Hono<{ Bindings: Bindings }>();

app.use(
  "*",
  cors({
    origin: (origin) => {
      if (!origin) {
        return origin;
      }

      const allowedOrigins = new Set([
        "https://la-douceur-balancee-erp.pages.dev",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
      ]);

      if (allowedOrigins.has(origin)) {
        return origin;
      }

      if (/^https:\/\/[a-z0-9-]+\.la-douceur-balancee-erp\.pages\.dev$/.test(origin)) {
        return origin;
      }

      return "";
    },
    allowMethods: ["GET", "POST", "OPTIONS"],
    allowHeaders: ["Content-Type", "Authorization"],
  }),
);

app.get("/", (c) => {
  return c.json({
    name: c.env.APP_NAME,
    status: "ok",
    message: "Worker API skeleton is ready.",
  });
});

app.get("/api/health", (c) => {
  return c.json({
    ok: true,
    service: "worker-api",
    timestamp: new Date().toISOString(),
  });
});

app.get("/api/debug/bindings", (c) => {
  return c.json({
    hasSupabaseUrl: Boolean(c.env.SUPABASE_URL),
    hasSupabasePublishableKey: Boolean(c.env.SUPABASE_PUBLISHABLE_KEY),
    hasSupabaseServiceRoleKey: Boolean(c.env.SUPABASE_SERVICE_ROLE_KEY),
    appName: c.env.APP_NAME,
  });
});

app.get("/api/dashboard", (c) => {
  return c.json({
    summary: {
      lowStockCount: 0,
      expiringProductsCount: 0,
      expiringMaterialsCount: 0,
      todayInboundCount: 0,
      todayProductionCount: 0,
      todaySalesCount: 0,
    },
    source: "stub",
  });
});

app.get("/api/materials", (c) => {
  return listMaterials(c.env).then((result) => {
    if (!result.ok) {
      return c.json({ ok: false, error: result.error }, 500);
    }

    return c.json({
      items: result.items,
      source: "supabase",
    });
  });
});

app.get("/api/materials/:id", (c) => {
  const id = Number(c.req.param("id"));
  return getMaterialById(c.env, id).then((result) => {
    if (!result.ok) {
      const status = result.error === "Material not found" ? 404 : 500;
      return c.json({ ok: false, error: result.error }, status);
    }

    return c.json({
      item: result.item,
      source: "supabase",
    });
  });
});

app.post("/api/materials", async (c) => {
  const payload = await c.req.json().catch(() => null);
  if (!payload) {
    return c.json({ ok: false, error: "Invalid JSON payload" }, 400);
  }

  const result = await createMaterial(c.env, payload);
  if (!result.ok) {
    const status = result.error === "名稱不可空白" ? 400 : 500;
    return c.json({ ok: false, error: result.error }, status);
  }

  return c.json(
    {
      ok: true,
      item: result.item,
      source: "supabase",
    },
    201,
  );
});

app.get("/api/products", (c) => {
  return listProducts(c.env).then((result) => {
    if (!result.ok) {
      return c.json({ ok: false, error: result.error }, 500);
    }

    return c.json({
      items: result.items,
      source: "supabase",
    });
  });
});

app.post("/api/products", async (c) => {
  const payload = await c.req.json().catch(() => null);
  if (!payload) {
    return c.json({ ok: false, error: "Invalid JSON payload" }, 400);
  }

  const result = await createProduct(c.env, payload);
  if (!result.ok) {
    const status = result.error === "產品名稱不可空白" ? 400 : 500;
    return c.json({ ok: false, error: result.error }, status);
  }

  return c.json(
    {
      ok: true,
      item: result.item,
      source: "supabase",
    },
    201,
  );
});

app.notFound((c) => c.json({ ok: false, error: "Not Found" }, 404));

export default app;
