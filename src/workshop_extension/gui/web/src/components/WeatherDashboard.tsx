import { CloudRain, Sun, Wind, Droplets, Umbrella, UmbrellaOff, Wifi, WifiOff } from "lucide-react";
import { useWeather } from "@/hooks/useWeather";
import type { WeatherData } from "@/lib/server";

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  } catch {
    return iso;
  }
}

function ConnectionBadge({ connected }: { connected: boolean }) {
  return (
    <span
      className={`flex items-center gap-1.5 text-xs px-2 py-1 rounded-full ${
        connected
          ? "bg-emerald-900/50 text-emerald-400"
          : "bg-zinc-800 text-zinc-500"
      }`}
    >
      {connected ? <Wifi size={12} /> : <WifiOff size={12} />}
      {connected ? "Live" : "Disconnected"}
    </span>
  );
}

function UmbrellaHero({ data }: { data: WeatherData }) {
  const yes = data.needs_umbrella;
  return (
    <div
      className={`rounded-2xl p-8 text-center transition-colors ${
        yes
          ? "bg-blue-950/60 border border-blue-800/40"
          : "bg-amber-950/40 border border-amber-800/30"
      }`}
    >
      <div className="flex justify-center mb-4">
        {yes ? (
          <Umbrella
            size={64}
            className="text-blue-400"
            strokeWidth={1.5}
          />
        ) : (
          <UmbrellaOff
            size={64}
            className="text-amber-400"
            strokeWidth={1.5}
          />
        )}
      </div>
      <p className={`text-2xl font-bold tracking-tight ${yes ? "text-blue-200" : "text-amber-200"}`}>
        {yes ? "Bring your umbrella" : "No umbrella needed"}
      </p>
      <p className="text-sm text-zinc-400 mt-1">{data.daily_desc}</p>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
      <div className="flex items-center gap-2 text-zinc-500 text-xs mb-2">
        {icon}
        {label}
      </div>
      <p className="text-zinc-100 font-semibold text-lg leading-tight">{value}</p>
    </div>
  );
}

function WeatherGrid({ data }: { data: WeatherData }) {
  return (
    <div className="grid grid-cols-2 gap-3">
      <StatCard
        label="Temperature"
        value={data.temp_f != null ? `${Math.round(data.temp_f)}°F` : "—"}
        icon={<Sun size={13} />}
      />
      <StatCard
        label="Conditions"
        value={data.current_desc}
        icon={<CloudRain size={13} />}
      />
      <StatCard
        label="Wind"
        value={data.wind_mph != null ? `${Math.round(data.wind_mph)} mph` : "—"}
        icon={<Wind size={13} />}
      />
      <StatCard
        label="Rain chance"
        value={`${data.precip_pct}%${data.precip_in > 0 ? ` · ${data.precip_in.toFixed(2)}"` : ""}`}
        icon={<Droplets size={13} />}
      />
    </div>
  );
}

export default function WeatherDashboard() {
  const { weather, connected } = useWeather();

  return (
    <div className="w-full max-w-sm flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-zinc-100">
            {weather?.display_name ?? "Pittsburgh, PA"}
          </h1>
          <p className="text-xs text-zinc-500">Weather Dashboard</p>
        </div>
        <ConnectionBadge connected={connected} />
      </div>

      {/* Umbrella indicator */}
      {weather ? (
        <UmbrellaHero data={weather} />
      ) : (
        <div className="rounded-2xl bg-zinc-900 border border-zinc-800 p-8 flex items-center justify-center">
          <p className="text-zinc-500 text-sm animate-pulse">Fetching weather…</p>
        </div>
      )}

      {/* Stats grid */}
      {weather && <WeatherGrid data={weather} />}

      {/* Footer */}
      {weather?.updated_at && (
        <p className="text-center text-xs text-zinc-600">
          Updated {formatTime(weather.updated_at)} · refreshes every 5 min
        </p>
      )}
    </div>
  );
}
