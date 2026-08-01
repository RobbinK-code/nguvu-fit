import { Link } from "react-router-dom";
import "./Landing.css";

export default function Landing() {
  return (
    <div className="landing">
      <section className="hero container">
        <p className="mono hero-eyebrow">HOME TRAINING, NO EQUIPMENT NEEDED</p>
        <h1 className="hero-title">
          Train with
          <br />
          Nguvu.
        </h1>
        <p className="hero-sub">
          A plan built around your body, your goal, and your kitchen floor.
          Track every session, get a fresh reason to show up each day, and
          watch the number move.
        </p>
        <div className="hero-actions">
          <Link to="/register" className="btn btn-primary">
            Start training free
          </Link>
          <Link to="/login" className="btn btn-secondary">
            I already have an account
          </Link>
        </div>
      </section>

      <section className="container steps">
        <div className="step">
          <span className="step-index mono">01</span>
          <h3>Tell us where you're starting</h3>
          <p>Height, weight, goal, equipment - takes under a minute.</p>
        </div>
        <div className="step">
          <span className="step-index mono">02</span>
          <h3>Get your weekly plan</h3>
          <p>
            Bodyweight or gym gear, built around the muscle groups you want
            to hit hardest.
          </p>
        </div>
        <div className="step">
          <span className="step-index mono">03</span>
          <h3>Log it, see it add up</h3>
          <p>Every session logged. Every week, proof you showed up.</p>
        </div>
      </section>
    </div>
  );
}
