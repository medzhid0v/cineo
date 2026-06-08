import { useState } from "react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label, Spinner } from "@/components/ui/misc";
import { api } from "@/lib/api";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      // Прогреваем csrf-cookie, затем логинимся.
      await api.me();
      await api.login(username, password);
      window.location.href = "/";
    } catch {
      setError("Неверный логин или пароль");
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="bg-gradient-to-r from-primary to-sky-300 bg-clip-text text-4xl font-extrabold tracking-tight text-transparent">
            Cineo
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">Личная фильмотека</p>
        </div>
        <Card>
          <CardContent className="pt-6">
            <form onSubmit={onSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="username">Логин</Label>
                <Input
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoFocus
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="password">Пароль</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading && <Spinner className="size-4" />}
                Войти
              </Button>
            </form>
            <p className="mt-4 text-center text-xs text-muted-foreground">
              Нет аккаунта?{" "}
              <Link to="/signup" className="text-primary hover:underline">
                Регистрация
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
