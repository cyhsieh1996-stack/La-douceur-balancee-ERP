create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists raw_materials_set_updated_at on public.raw_materials;
create trigger raw_materials_set_updated_at
before update on public.raw_materials
for each row
execute function public.set_updated_at();

drop trigger if exists products_set_updated_at on public.products;
create trigger products_set_updated_at
before update on public.products
for each row
execute function public.set_updated_at();

drop trigger if exists profiles_set_updated_at on public.profiles;
create trigger profiles_set_updated_at
before update on public.profiles
for each row
execute function public.set_updated_at();

alter table public.raw_materials enable row level security;
alter table public.products enable row level security;
alter table public.product_recipes enable row level security;
alter table public.inbound_records enable row level security;
alter table public.production_logs enable row level security;
alter table public.sales_records enable row level security;
alter table public.inventory_adjustments enable row level security;
alter table public.profiles enable row level security;

create policy "authenticated users can read raw_materials"
on public.raw_materials
for select
to authenticated
using (true);

create policy "authenticated users can read products"
on public.products
for select
to authenticated
using (true);

create policy "authenticated users can read product_recipes"
on public.product_recipes
for select
to authenticated
using (true);

create policy "authenticated users can read inbound_records"
on public.inbound_records
for select
to authenticated
using (true);

create policy "authenticated users can read production_logs"
on public.production_logs
for select
to authenticated
using (true);

create policy "authenticated users can read sales_records"
on public.sales_records
for select
to authenticated
using (true);

create policy "authenticated users can read inventory_adjustments"
on public.inventory_adjustments
for select
to authenticated
using (true);

create policy "user can read own profile"
on public.profiles
for select
to authenticated
using (auth.uid() = id);
