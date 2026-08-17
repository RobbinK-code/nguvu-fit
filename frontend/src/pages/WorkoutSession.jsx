import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { api } from "../lib/api";
import ConfirmDialog from "../components/ConfirmDialog";
import { useCloseOnHide } from "../lib/useCloseOnHide";
import "./WorkoutSession.css";

const REST_SECONDS = 30;

// A short, dependency-free beep using the Web Audio API - no audio file
// to ship, works offline, and doesn't need any new permissions.
function playBeep() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.frequency.value = 880;
    gain.gain.setValueAtTime(0.15, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
    osc.start();
    osc.stop(ctx.currentTime + 0.35);
  } catch {
    // Web Audio unsupported/blocked - silently skip the beep, timer still works.
  }
}

export default function WorkoutSession() {
  const location = useLocation();
  const navigate = useNavigate();
  const day = location.state?.day;

  const [exerciseIndex, setExerciseIndex] = useState(0);
  const [setNumber, setSetNumber] = useState(1);
  const [phase, setPhase] = useState("exercise"); // exercise | resting | done
  const [secondsLeft, setSecondsLeft] = useState(null);
  const [exitConfirmOpen, setExitConfirmOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [videoOpen, setVideoOpen] = useState(false);
  useCloseOnHide(() => setVideoOpen(false));

  const startTimeRef = useRef(Date.now());

  const exercise = day?.exercises?.[exerciseIndex];
  const isTimed = exercise?.tracking_type === "hold" || exercise?.tracking_type === "duration";
  const totalExercises = day?.exercises?.length ?? 0;

  // Drive the countdown for timed exercises and for rest periods.
  useEffect(() => {
    setVideoOpen(false);
  }, [exerciseIndex]);

  useEffect(() => {
    if (!exercise) return;
    if (phase === "exercise" && isTimed) {
      setSecondsLeft(exercise.duration_seconds);
    } else if (phase === "resting") {
      setSecondsLeft(REST_SECONDS);
    } else {
      setSecondsLeft(null);
    }
  }, [phase, exerciseIndex, setNumber, isTimed, exercise]);

  useEffect(() => {
    if (secondsLeft === null) return;
    if (secondsLeft <= 0) {
      playBeep();
      if (phase === "exercise") advanceAfterSet();
      else if (phase === "resting") setPhase("exercise");
      return;
    }
    const t = setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [secondsLeft, phase]);

  function advanceAfterSet() {
    if (setNumber < exercise.sets) {
      setSetNumber((n) => n + 1);
      setPhase("resting");
    } else if (exerciseIndex < totalExercises - 1) {
      setExerciseIndex((i) => i + 1);
      setSetNumber(1);
      setPhase("resting");
    } else {
      setPhase("done");
    }
  }

  function handleCompleteSet() {
    advanceAfterSet();
  }

  function handleSkipExercise() {
    if (exerciseIndex < totalExercises - 1) {
      setExerciseIndex((i) => i + 1);
      setSetNumber(1);
      setPhase("exercise");
    } else {
      setPhase("done");
    }
  }

  function handleSkipRest() {
    setPhase("exercise");
  }

  async function handleFinish() {
    setSaving(true);
    setSaveError(null);
    const elapsedMinutes = Math.max(1, Math.round((Date.now() - startTimeRef.current) / 60000));
    try {
      await api.logWorkout({
        workout_name: `Day ${day.day_number} - ${day.focus}`,
        duration_minutes: elapsedMinutes,
      });
      navigate("/dashboard");
    } catch (err) {
      setSaveError(err.message);
    } finally {
      setSaving(false);
    }
  }

  const progressPct = useMemo(() => {
    if (!totalExercises) return 0;
    return Math.round(((exerciseIndex + (phase === "done" ? 1 : 0)) / totalExercises) * 100);
  }, [exerciseIndex, phase, totalExercises]);

  if (!day) {
    return (
      <div className="container workout-session-page">
        <p className="empty-state">
          No active workout session. Head back to your dashboard and hit "Start workout" on a day.
        </p>
        <Link to="/dashboard" className="btn btn-primary">
          Back to dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="container workout-session-page">
      <div className="session-progress-track">
        <div className="session-progress-fill" style={{ width: `${progressPct}%` }} />
      </div>

      {phase !== "done" ? (
        <>
          <div className="session-header">
            <span className="mono session-counter">
              EXERCISE {exerciseIndex + 1} / {totalExercises}
            </span>
            <button className="session-exit" onClick={() => setExitConfirmOpen(true)} aria-label="Exit workout">
              ✕
            </button>
          </div>

          {phase === "resting" ? (
            <div className="session-card session-resting">
              <p className="mono session-label">REST</p>
              <p className="session-timer">{secondsLeft}s</p>
              <p className="session-next-up">Next: {exercise.name}</p>
              <button className="btn btn-secondary" onClick={handleSkipRest}>
                Skip rest
              </button>
            </div>
          ) : (
            <div className="session-card">
              <p className="mono session-label">
                SET {setNumber} / {exercise.sets}
              </p>
              <h2 className="session-exercise-name">{exercise.name}</h2>

              {isTimed ? (
                <p className="session-timer">{secondsLeft}s</p>
              ) : (
                <p className="session-reps">{exercise.reps} reps</p>
              )}

              {exercise.video_id && (
                <>
                  <button
                    type="button"
                    className="session-skip-link"
                    onClick={() => setVideoOpen((v) => !v)}
                  >
                    {videoOpen ? "Hide video" : "Watch video"}
                  </button>
                  {videoOpen && (
                    <div className="session-video-wrap">
                      <iframe
                        src={`https://www.youtube.com/embed/${exercise.video_id}`}
                        title={`${exercise.name} demonstration`}
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                        loading="lazy"
                      />
                    </div>
                  )}
                </>
              )}

              {!isTimed && (
                <button className="btn btn-primary btn-block" onClick={handleCompleteSet}>
                  Complete set
                </button>
              )}

              <button className="session-skip-link" onClick={handleSkipExercise}>
                Skip this exercise
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="session-card session-done">
          <p className="mono session-label">WORKOUT COMPLETE</p>
          <h2 className="session-exercise-name">Nice work.</h2>
          <p className="session-done-copy">
            You just finished Day {day.day_number} - {day.focus}.
          </p>
          {saveError && <p className="error-text">{saveError}</p>}
          <button className="btn btn-primary btn-block" onClick={handleFinish} disabled={saving}>
            {saving ? "Saving…" : "Save and finish"}
          </button>
        </div>
      )}

      <ConfirmDialog
        open={exitConfirmOpen}
        title="Exit this workout?"
        message="Your progress in this session won't be saved unless you finish it."
        confirmLabel="Exit"
        danger
        onConfirm={() => navigate("/dashboard")}
        onCancel={() => setExitConfirmOpen(false)}
      />
    </div>
  );
}
