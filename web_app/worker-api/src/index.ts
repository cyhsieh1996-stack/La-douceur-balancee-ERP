import { Hono } from "hono";
import { cors } from "hono/cors";
import { getDashboardData } from "./modules/dashboard";
import { createInboundRecord, listInboundRecords } from "./modules/inbound";
import { adjustInventory, getInventoryCenter } from "./modules/inventory";
import {
  createMaterial,
  deleteMaterial,
  getMaterialById,
  listMaterials,
  updateMaterial,
} from "./modules/materials";
import {
  createProductionLog,
  generateBatchNumber,
  getProductionPreview,
  listProductionLogs,
} from "./modules/production";
import { createProduct, deleteProduct, listProducts, updateProduct } from "./modules/products";
import { deleteRecipe, listRecipes, saveRecipe } from "./modules/recipes";
import { getReportsData } from "./modules/reports";
import { importSalesRecords, listSalesRecords } from "./modules/sales";

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
        "https://la-douceur-balancee-erp-web.pages.dev",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
      ]);

      if (allowedOrigins.has(origin)) {
        return origin;
      }

      if (/^https:\/\/[a-z0-9-]+\.la-douceur-balancee-erp\.pages\.dev$/.test(origin)) {
        return origin;
      }

      if (/^https:\/\/[a-z0-9-]+\.la-douceur-balancee-erp-web\.pages\.dev$/.test(origin)) {
        return origin;
      }

      return "";
    },
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
  return getDashboardData(c.env).then((result) => {
    if (!result.ok) {
      return c.json({ ok: false, error: result.error }, 500);
    }

    return c.json({
      ...result,
      source: "supabase",
    });
  });
});

app.get("/api/reports", (c) => {
  return getReportsData(c.env).then((result) => {
    if (!result.ok) {
      return c.json({ ok: false, error: result.error }, 500);
    }

    return c.json({
      ...result,
      source: "supabase",
    });
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

app.put("/api/materials/:id", async (c) => {
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) {
    return c.json({ ok: false, error: "Invalid material id" }, 400);
  }

  const payload = await c.req.json().catch(() => null);
  if (!payload) {
    return c.json({ ok: false, error: "Invalid JSON payload" }, 400);
  }

  const result = await updateMaterial(c.env, id, payload);
  if (!result.ok) {
    const status =
      result.error === "名稱不可空白" ? 400 : result.error === "Material not found" ? 404 : 500;
    return c.json({ ok: false, error: result.error }, status);
  }

  return c.json({
    ok: true,
    item: result.item,
    source: "supabase",
  });
});

app.delete("/api/materials/:id", async (c) => {
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) {
    return c.json({ ok: false, error: "Invalid material id" }, 400);
  }

  const result = await deleteMaterial(c.env, id);
  if (!result.ok) {
    const status = result.error === "Material not found" ? 404 : 500;
    return c.json({ ok: false, error: result.error }, status);
  }

  return c.json({
    ok: true,
    source: "supabase",
  });
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

app.put("/api/products/:id", async (c) => {
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) {
    return c.json({ ok: false, error: "Invalid product id" }, 400);
  }

  const payload = await c.req.json().catch(() => null);
  if (!payload) {
    return c.json({ ok: false, error: "Invalid JSON payload" }, 400);
  }

  const result = await updateProduct(c.env, id, payload);
  if (!result.ok) {
    const status =
      result.error === "產品名稱不可空白" ? 400 : result.error === "Product not found" ? 404 : 500;
    return c.json({ ok: false, error: result.error }, status);
  }

  return c.json({
    ok: true,
    item: result.item,
    source: "supabase",
  });
});

app.delete("/api/products/:id", async (c) => {
  const id = Number(c.req.param("id"));
  if (!Number.isFinite(id)) {
    return c.json({ ok: false, error: "Invalid product id" }, 400);
  }

  const result = await deleteProduct(c.env, id);
  if (!result.ok) {
    const status = result.error === "Product not found" ? 404 : 500;
    return c.json({ ok: false, error: result.error }, status);
  }

  return c.json({
    ok: true,
    source: "supabase",
  });
});

app.get("/api/products/:id/recipes", async (c) => {
  const productId = Number(c.req.param("id"));
  if (!Number.isFinite(productId)) {
    return c.json({ ok: false, error: "Invalid product id" }, 400);
  }

  const result = await listRecipes(c.env, productId);
  if (!result.ok) {
    return c.json({ ok: false, error: result.error }, 500);
  }

  return c.json({
    ok: true,
    items: result.items,
    source: "supabase",
  });
});

app.post("/api/products/:id/recipes", async (c) => {
  const productId = Number(c.req.param("id"));
  if (!Number.isFinite(productId)) {
    return c.json({ ok: false, error: "Invalid product id" }, 400);
  }

  const payload = await c.req.json().catch(() => null);
  if (!payload) {
    return c.json({ ok: false, error: "Invalid JSON payload" }, 400);
  }

  const result = await saveRecipe(c.env, productId, payload);
  if (!result.ok) {
    const status =
      result.error === "原料編號無效" || result.error === "每單位用量必須大於 0" ? 400 : 500;
    return c.json({ ok: false, error: result.error }, status);
  }

  return c.json({
    ok: true,
    item: result.item,
    source: "supabase",
  });
});

app.delete("/api/recipes/:id", async (c) => {
  const recipeId = Number(c.req.param("id"));
  if (!Number.isFinite(recipeId)) {
    return c.json({ ok: false, error: "Invalid recipe id" }, 400);
  }

  const result = await deleteRecipe(c.env, recipeId);
  if (!result.ok) {
    const status = result.error === "Recipe not found" ? 404 : 500;
    return c.json({ ok: false, error: result.error }, status);
  }

  return c.json({
    ok: true,
    source: "supabase",
  });
});

app.get("/api/inventory", async (c) => {
  const keyword = c.req.query("keyword") ?? "";
  const lowStockOnly = c.req.query("lowStockOnly") === "true";
  const result = await getInventoryCenter(c.env, { keyword, lowStockOnly, limit: 20 });

  if (!result.ok) {
    return c.json({ ok: false, error: result.error }, 500);
  }

  return c.json({
    ...result,
    source: "supabase",
  });
});

app.post("/api/inventory/adjustments", async (c) => {
  const payload = await c.req.json().catch(() => null);
  if (!payload) {
    return c.json({ ok: false, error: "Invalid JSON payload" }, 400);
  }

  const result = await adjustInventory(c.env, payload);
  if (!result.ok) {
    const status =
      result.error === "原料編號無效" || result.error === "盤點數量必須為 0 以上"
        ? 400
        : result.error === "找不到該原料"
          ? 404
          : 500;
    return c.json({ ok: false, error: result.error }, status);
  }

  return c.json({
    ok: true,
    item: result.item,
    adjustment: result.adjustment,
    source: "supabase",
  });
});

app.get("/api/inbound", async (c) => {
  const result = await listInboundRecords(c.env, 20);
  if (!result.ok) {
    return c.json({ ok: false, error: result.error }, 500);
  }

  return c.json({
    ok: true,
    items: result.items,
    source: "supabase",
  });
});

app.post("/api/inbound", async (c) => {
  const payload = await c.req.json().catch(() => null);
  if (!payload) {
    return c.json({ ok: false, error: "Invalid JSON payload" }, 400);
  }

  const result = await createInboundRecord(c.env, payload);
  if (!result.ok) {
    const status =
      result.error === "原料編號無效" ||
      result.error === "入庫數量必須大於 0" ||
      result.error === "進貨單價不得小於 0"
        ? 400
        : result.error === "找不到該原料"
          ? 404
          : 500;
    return c.json({ ok: false, error: result.error }, status);
  }

  return c.json(
    {
      ok: true,
      item: result.item,
      material: result.material,
      source: "supabase",
    },
    201,
  );
});

app.get("/api/production", async (c) => {
  const result = await listProductionLogs(c.env, 20);
  if (!result.ok) {
    return c.json({ ok: false, error: result.error }, 500);
  }

  return c.json({
    ok: true,
    items: result.items,
    source: "supabase",
  });
});

app.get("/api/production/batch-number", async (c) => {
  const productId = Number(c.req.query("productId"));
  if (!Number.isFinite(productId)) {
    return c.json({ ok: false, error: "Invalid product id" }, 400);
  }

  const result = await generateBatchNumber(c.env, productId);
  if (!result.ok) {
    return c.json({ ok: false, error: result.error }, 500);
  }

  return c.json({
    ok: true,
    batchNumber: result.batchNumber,
    source: "supabase",
  });
});

app.get("/api/production/preview", async (c) => {
  const productId = Number(c.req.query("productId"));
  const qty = Number(c.req.query("qty"));
  if (!Number.isFinite(productId) || !Number.isFinite(qty) || qty <= 0) {
    return c.json({ ok: false, error: "Invalid product id or qty" }, 400);
  }

  const result = await getProductionPreview(c.env, productId, qty);
  if (!result.ok) {
    return c.json({ ok: false, error: result.error }, 500);
  }

  return c.json({
    ok: true,
    items: result.items,
    shortages: result.shortages,
    source: "supabase",
  });
});

app.post("/api/production", async (c) => {
  const payload = await c.req.json().catch(() => null);
  if (!payload) {
    return c.json({ ok: false, error: "Invalid JSON payload" }, 400);
  }

  const result = await createProductionLog(c.env, payload);
  if (!result.ok) {
    const status =
      result.error === "產品編號無效" || result.error === "生產數量必須大於 0"
        ? 400
        : result.error === "找不到產品"
          ? 404
          : result.error.startsWith("原料不足")
            ? 409
            : 500;
    return c.json({ ok: false, error: result.error }, status);
  }

  return c.json(
    {
      ok: true,
      item: result.item,
      recipePreview: result.recipePreview,
      source: "supabase",
    },
    201,
  );
});

app.get("/api/sales", async (c) => {
  const result = await listSalesRecords(c.env, 100);
  if (!result.ok) {
    return c.json({ ok: false, error: result.error }, 500);
  }

  return c.json({
    ok: true,
    items: result.items,
    source: "supabase",
  });
});

app.post("/api/sales/import", async (c) => {
  const payload = await c.req.json().catch(() => null);
  if (!payload) {
    return c.json({ ok: false, error: "Invalid JSON payload" }, 400);
  }

  try {
    const result = await importSalesRecords(c.env, payload);
    if (!result.ok) {
      const status = result.error === "沒有可匯入的銷售資料" ? 400 : 500;
      return c.json({ ok: false, error: result.error }, status);
    }

    return c.json(
      {
        ok: true,
        importedCount: result.importedCount,
        source: "supabase",
      },
      201,
    );
  } catch (error) {
    return c.json({ ok: false, error: error instanceof Error ? error.message : String(error) }, 400);
  }
});

app.notFound((c) => c.json({ ok: false, error: "Not Found" }, 404));

export default app;
