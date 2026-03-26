insert into public.raw_materials (name, category, brand, vendor, unit, unit_price, stock, safe_stock)
values
  ('無鹽奶油', '乳製品', 'Elle & Vire', '永豐商行', 'kg', 280, 6, 10),
  ('低筋麵粉', '粉類', '日清', '大統食品', 'kg', 52, 24, 20),
  ('砂糖', '糖類', '台糖', '中盤供應商', 'kg', 38, 0, 15);

insert into public.products (name, category, price, cost, stock, shelf_life)
values
  ('檸檬塔', '常溫蛋糕/塔', 160, 75, 0, 3),
  ('草莓鮮奶油蛋糕', '整模蛋糕', 980, 420, 0, 2);
