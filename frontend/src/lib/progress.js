// Consecutive-day streak: counts backward from today (or yesterday, so a
// missed "today" doesn't zero out a streak still in progress) as long as
// each day has at least one logged workout.
export function computeStreak(logs) {
  if (!logs?.length) return 0;

  const days = new Set(
    logs.map((l) => new Date(l.completed_at).toISOString().slice(0, 10))
  );

  const today = new Date();
  let streak = 0;
  let cursor = new Date(today);

  // If nothing logged today yet, start checking from yesterday instead -
  // otherwise a real streak would show as 0 for the rest of today.
  if (!days.has(cursor.toISOString().slice(0, 10))) {
    cursor.setDate(cursor.getDate() - 1);
  }

  while (days.has(cursor.toISOString().slice(0, 10))) {
    streak += 1;
    cursor.setDate(cursor.getDate() - 1);
  }

  return streak;
}

export function countThisWeek(logs) {
  if (!logs?.length) return 0;
  const now = new Date();
  const startOfWeek = new Date(now);
  const day = (startOfWeek.getDay() + 6) % 7; // Monday = 0
  startOfWeek.setDate(startOfWeek.getDate() - day);
  startOfWeek.setHours(0, 0, 0, 0);

  return logs.filter((l) => new Date(l.completed_at) >= startOfWeek).length;
}

// Buckets logs into the last `weeksBack` Monday-start weeks (oldest first)
// for a simple sessions-per-week chart.
export function buildWeeklyVolume(logs, weeksBack = 8) {
  const now = new Date();
  const startOfThisWeek = new Date(now);
  const day = (startOfThisWeek.getDay() + 6) % 7;
  startOfThisWeek.setDate(startOfThisWeek.getDate() - day);
  startOfThisWeek.setHours(0, 0, 0, 0);

  const weeks = [];
  for (let i = weeksBack - 1; i >= 0; i--) {
    const start = new Date(startOfThisWeek);
    start.setDate(start.getDate() - i * 7);
    const end = new Date(start);
    end.setDate(end.getDate() + 7);
    weeks.push({ start, end, sessions: 0, minutes: 0 });
  }

  for (const log of logs || []) {
    const at = new Date(log.completed_at);
    const bucket = weeks.find((w) => at >= w.start && at < w.end);
    if (bucket) {
      bucket.sessions += 1;
      bucket.minutes += log.duration_minutes || 0;
    }
  }

  return weeks.map((w) => ({
    label: w.start.toLocaleDateString(undefined, { month: "short", day: "numeric" }),
    sessions: w.sessions,
    minutes: w.minutes,
  }));
}

export const MILESTONES = [
  { id: "first", label: "First session", check: (s) => s.total_workouts >= 1 },
  { id: "five", label: "5 workouts logged", check: (s) => s.total_workouts >= 5 },
  { id: "ten", label: "10 workouts logged", check: (s) => s.total_workouts >= 10 },
  { id: "twentyfive", label: "25 workouts logged", check: (s) => s.total_workouts >= 25 },
  { id: "streak3", label: "3-day streak", check: (s) => s.streak >= 3 },
  { id: "streak7", label: "7-day streak", check: (s) => s.streak >= 7 },
  { id: "hours5", label: "5 hours trained", check: (s) => s.total_minutes >= 300 },
];
