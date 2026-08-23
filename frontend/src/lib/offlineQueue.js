import { api } from "./api";

const QUEUE_KEY = "nguvu_offline_log_queue";

function readQueue() {
  try {
    return JSON.parse(localStorage.getItem(QUEUE_KEY)) || [];
  } catch {
    return [];
  }
}

function writeQueue(queue) {
  localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
}

export function queueLogWorkout(payload) {
  const queue = readQueue();
  queue.push({ ...payload, queuedAt: new Date().toISOString() });
  writeQueue(queue);
}

export function pendingQueueCount() {
  return readQueue().length;
}

/** Attempts to send every queued log. Successful ones are removed;
 * anything that fails (still offline, or a real error) stays queued
 * for the next attempt. Returns how many were successfully synced. */
export async function flushLogQueue() {
  const queue = readQueue();
  if (queue.length === 0) return 0;

  const remaining = [];
  let synced = 0;

  for (const entry of queue) {
    const { queuedAt, ...payload } = entry;
    try {
      await api.logWorkout(payload);
      synced += 1;
    } catch {
      remaining.push(entry);
    }
  }

  writeQueue(remaining);
  return synced;
}
