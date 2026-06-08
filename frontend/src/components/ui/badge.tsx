import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary/15 text-primary",
        secondary: "border-transparent bg-secondary text-secondary-foreground",
        outline: "border-border text-foreground",
        muted: "border-transparent bg-muted text-muted-foreground",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

// Цвет статуса просмотра -> вариант/классы
export function StatusBadge({ status, label }: { status: string | null; label: string | null }) {
  if (!status || !label) return <span className="text-muted-foreground">—</span>;
  const map: Record<string, string> = {
    planned: "bg-sky-500/15 text-sky-300",
    watching: "bg-amber-500/15 text-amber-300",
    completed: "bg-emerald-500/15 text-emerald-300",
    dropped: "bg-rose-500/15 text-rose-300",
    on_hold: "bg-violet-500/15 text-violet-300",
  };
  return (
    <span className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", map[status] ?? "bg-muted text-muted-foreground")}>
      {label}
    </span>
  );
}
