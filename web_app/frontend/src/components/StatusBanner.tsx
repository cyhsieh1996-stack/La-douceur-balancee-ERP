import type { ReactNode } from "react";

type StatusTone = "neutral" | "loading" | "success" | "error";

type StatusBannerProps = {
  tone?: StatusTone;
  title?: string;
  children: ReactNode;
};

export function StatusBanner({ tone = "neutral", title, children }: StatusBannerProps) {
  const role = tone === "error" ? "alert" : "status";

  return (
    <div className={`status-banner ${tone}`} role={role}>
      {title ? <strong>{title}</strong> : null}
      <span>{children}</span>
    </div>
  );
}
