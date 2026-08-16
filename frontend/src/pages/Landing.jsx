import { Link } from "react-router-dom";
import Reveal from "../components/Reveal";
import "./Landing.css";

// Fill these in once you have real reviews - the section only renders
// when this array is non-empty, so nothing fake ships in the meantime.
const TESTIMONIALS = [
  // { quote: "...", name: "...", detail: "e.g. Nairobi" },
];

const TRUST_POINTS = [
  "No equipment required to start",
  "Plans rebuilt around your own goals",
  "Pay by M-Pesa, cancel any time",
];

const GOALS = [
  {
    value: "lose_fat",
    title: "Lose fat",
    copy: "Cardio-forward circuits built to move the number without burning you out.",
  },
  {
    value: "build_muscle",
    title: "Build muscle",
    copy: "Strength-focused sessions targeting the muscle groups you choose.",
  },
  {
    value: "endurance",
    title: "Endurance",
    copy: "Interval-heavy training to build a bigger engine, week over week.",
  },
  {
    value: "mobility",
    title: "Mobility",
    copy: "Stretch, flow, and recover - built for a body that needs to move well daily.",
  },
];

const FEATURES = [
  {
    title: "A plan that's actually yours",
    copy: "Built from your height, weight, goal, equipment, and the body parts you want to hit hardest.",
  },
  {
    title: "Zero equipment needed",
    copy: "Every plan works with nothing but floor space - add dumbbells or bands if you've got them.",
  },
  {
    title: "A reason to show up daily",
    copy: "A fresh line of motivation waits for you every time you open the app.",
  },
  {
    title: "Proof you're doing the work",
    copy: "Every session logged, so progress is something you can see, not just feel.",
  },
];

const FAQ = [
  {
    q: "Do I need any equipment?",
    a: "No. Every plan defaults to bodyweight-only. If you've got dumbbells or bands, tell us and we'll work them in.",
  },
  {
    q: "How much does it cost?",
    a: "Nguvu Fit is free to use. Premium features - refreshable plans, full history, and more - are KES 300/month or KES 3,000/year, paid by M-Pesa.",
  },
  {
    q: "Can I cancel any time?",
    a: "Yes. Subscriptions aren't locked into a contract - let it lapse whenever you like.",
  },
  {
    q: "What if I have an injury or health condition?",
    a: "Check with a doctor before starting any new training program, especially with an existing condition. Nguvu Fit gives general guidance, not medical advice.",
  },
];

export default function Landing() {
  return (
    <div className="landing">
      <section className="hero container">
        <p className="mono hero-eyebrow hero-fade-in">HOME TRAINING, NO EQUIPMENT NEEDED</p>
        <h1 className="hero-title hero-fade-in hero-fade-in-delay-1">
          Train with
          <br />
          <span className="hero-title-accent">Nguvu.</span>
        </h1>
        <p className="hero-sub hero-fade-in hero-fade-in-delay-2">
          A plan built around your body, your goal, and your kitchen floor.
          Track every session, get a fresh reason to show up each day, and
          watch the number move.
        </p>
        <div className="hero-actions hero-fade-in hero-fade-in-delay-3">
          <Link to="/register" className="btn btn-primary">
            Start training free
          </Link>
          <Link to="/login" className="btn btn-secondary">
            I already have an account
          </Link>
        </div>
      </section>

      <div className="container trust-strip">
        {TRUST_POINTS.map((point) => (
          <span key={point} className="trust-point mono">
            {point}
          </span>
        ))}
      </div>

      <section className="container steps">
        {[
          { n: "01", title: "Tell us where you're starting", copy: "Height, weight, goal, equipment - takes under a minute." },
          { n: "02", title: "Get your weekly plan", copy: "Bodyweight or gym gear, built around the muscle groups you want to hit hardest." },
          { n: "03", title: "Log it, see it add up", copy: "Every session logged. Every week, proof you showed up." },
        ].map((s, i) => (
          <Reveal key={s.n} delay={i * 100} className="step">
            <span className="step-index mono">{s.n}</span>
            <h3>{s.title}</h3>
            <p>{s.copy}</p>
          </Reveal>
        ))}
      </section>

      <section className="section-block">
        <div className="container">
          <Reveal>
            <p className="mono section-eyebrow">PICK YOUR GOAL</p>
            <h2 className="section-heading">Every plan starts with what you want.</h2>
          </Reveal>
          <div className="goal-grid">
            {GOALS.map((g, i) => (
              <Reveal key={g.value} delay={i * 80}>
                <Link to="/register" className="goal-card">
                  <h3>{g.title}</h3>
                  <p>{g.copy}</p>
                  <span className="goal-cta mono">Start here →</span>
                </Link>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="section-block section-block-alt">
        <div className="container">
          <Reveal>
            <p className="mono section-eyebrow">WHY NGUVU FIT</p>
            <h2 className="section-heading">Built to fit an actual life.</h2>
          </Reveal>
          <div className="feature-grid">
            {FEATURES.map((f, i) => (
              <Reveal key={f.title} delay={i * 80} className="feature-item">
                <h3>{f.title}</h3>
                <p>{f.copy}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {TESTIMONIALS.length > 0 && (
        <section className="section-block">
          <div className="container">
            <p className="mono section-eyebrow">FROM PEOPLE TRAINING WITH US</p>
            <h2 className="section-heading">What early users are saying.</h2>
            <div className="testimonial-grid">
              {TESTIMONIALS.map((t) => (
                <div key={t.name} className="testimonial-card">
                  <p className="testimonial-quote">&ldquo;{t.quote}&rdquo;</p>
                  <p className="testimonial-name mono">
                    {t.name}
                    {t.detail ? ` · ${t.detail}` : ""}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      <section className="section-block section-block-alt">
        <div className="container">
          <Reveal>
            <p className="mono section-eyebrow">QUESTIONS</p>
            <h2 className="section-heading">Before you start.</h2>
          </Reveal>
          <Reveal delay={100}>
            <div className="faq-list">
              {FAQ.map((item) => (
                <details key={item.q} className="faq-item">
                  <summary>{item.q}</summary>
                  <p>{item.a}</p>
                </details>
              ))}
            </div>
          </Reveal>
        </div>
      </section>

      <Reveal className="closing-cta container">
        <h2>Your first session is one tap away.</h2>
        <Link to="/register" className="btn btn-primary">
          Start training free
        </Link>
      </Reveal>
    </div>
  );
}
