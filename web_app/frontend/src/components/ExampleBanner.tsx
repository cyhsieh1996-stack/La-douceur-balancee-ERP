import type { ReactNode } from "react";

type ExampleBannerProps = {
  title?: string;
  children: ReactNode;
};

export function ExampleBanner({ title = "範例", children }: ExampleBannerProps) {
  return (
    <div className="example-banner">
      <strong>{title}</strong>
      <span>{children}</span>
    </div>
  );
}
