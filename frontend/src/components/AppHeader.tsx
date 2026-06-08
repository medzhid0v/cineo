import { LogOut } from "lucide-react";

import { AddDialog } from "@/components/AddDialog";
import { Button } from "@/components/ui/button";
import { useLogout, useMe } from "@/lib/auth";

export function AppHeader() {
  const { data: me } = useMe();
  const logout = useLogout();

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-[1400px] items-center justify-between gap-4 px-4 py-3 md:px-6">
        <a href="/" className="flex items-center gap-2">
          <span className="bg-gradient-to-r from-primary to-sky-300 bg-clip-text text-xl font-extrabold tracking-tight text-transparent">
            Cineo
          </span>
        </a>

        <div className="flex items-center gap-2">
          <AddDialog />
          <div className="mx-1 hidden h-6 w-px bg-border sm:block" />
          <span className="hidden text-sm text-muted-foreground sm:inline">{me?.username}</span>
          <Button variant="ghost" size="icon" onClick={logout} title="Выйти">
            <LogOut className="size-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
