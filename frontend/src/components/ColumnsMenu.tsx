import { Columns3 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { ColumnDef } from "@/lib/types";

interface Props {
  available: ColumnDef[];
  visible: string[];
  defaults: string[];
  onChange: (next: string[]) => void;
}

export function ColumnsMenu({ available, visible, defaults, onChange }: Props) {
  function toggle(key: string) {
    if (visible.includes(key)) {
      // не даём скрыть последнюю колонку
      if (visible.length <= 1) return;
      onChange(visible.filter((k) => k !== key));
    } else {
      // сохраняем порядок как в available
      const next = available.filter((c) => visible.includes(c.key) || c.key === key).map((c) => c.key);
      onChange(next);
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">
          <Columns3 className="size-4" />
          Колонки
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="max-h-[60vh] overflow-y-auto">
        <DropdownMenuLabel>Отображаемые колонки</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {available.map((col) => (
          <DropdownMenuCheckboxItem
            key={col.key}
            checked={visible.includes(col.key)}
            onSelect={(e) => {
              e.preventDefault();
              toggle(col.key);
            }}
          >
            {col.label}
          </DropdownMenuCheckboxItem>
        ))}
        <DropdownMenuSeparator />
        <DropdownMenuItem onSelect={() => onChange(defaults)}>Сбросить по умолчанию</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
