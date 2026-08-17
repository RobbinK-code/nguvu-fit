import PageLoading from "../components/PageLoading";
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import EquipmentIcon from "../components/EquipmentIcon";
import { useCloseOnHide } from "../lib/useCloseOnHide";
import "./GymGuide.css";

const GROUP_LABELS = {
  legs: "Legs",
  chest: "Chest",
  back: "Back",
  shoulders: "Shoulders",
  arms: "Arms",
  core: "Core",
  full_body: "Full body",
  cardio: "Cardio",
};

export default function GymGuide() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const highlightGroup = searchParams.get("group");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [openId, setOpenId] = useState(null);
  const [openVideoId, setOpenVideoId] = useState(null);
  useCloseOnHide(() => setOpenVideoId(null));

  useEffect(() => {
    async function load() {
      try {
        const res = await api.getEquipment();
        setData(res);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  useEffect(() => {
    if (!highlightGroup || !data) return;
    const el = document.getElementById(`gym-group-${highlightGroup}`);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [highlightGroup, data]);

  if (loading) return <PageLoading message="Loading the gym guide…" />;
  if (error) return <p className="container error-text">{error}</p>;

  return (
    <div className="container gym-guide">
      <p className="mono hero-eyebrow">AT THE GYM</p>
      <h2>Same goals, different equipment.</h2>
      <p className="gym-guide-sub">
        No home gym isn't the only way to train - here's how to hit the same muscle groups on
        machines, with clear steps for how to use each one.
      </p>

      {!data?.is_premium && (
        <div className="card gym-guide-upsell">
          <p>
            <strong>You're seeing a preview.</strong> Subscribers get the full equipment library -
            every machine for every muscle group, not just one example.
          </p>
          <Link to="/subscribe" className="btn btn-primary">
            Unlock full library
          </Link>
        </div>
      )}

      {Object.entries(data?.equipment || {}).map(([group, items]) => (
        <section key={group} className={`gym-guide-section ${highlightGroup === group ? "gym-guide-section-highlight" : ""}`} id={`gym-group-${group}`}>
          <h3 className="gym-guide-group-title">{GROUP_LABELS[group] || group}</h3>
          <div className="equipment-grid">
            {items.map((item) => (
              <div key={item.id} className="card equipment-card">
                <div className="equipment-visual">
                  {item.image_url ? (
                    <img src={item.image_url} alt={item.name} className="equipment-image" loading="lazy" />
                  ) : (
                    <div className="equipment-icon">
                      <EquipmentIcon icon={item.icon} />
                    </div>
                  )}
                </div>
                <h4>{item.name}</h4>
                <p className="equipment-description">{item.description}</p>
                <div className="equipment-actions">
                  <button
                    type="button"
                    className="equipment-howto-toggle"
                    onClick={() => setOpenId(openId === item.id ? null : item.id)}
                  >
                    {openId === item.id ? "Hide how-to" : "How to use it"}
                  </button>
                  {item.video_id && (
                    <button
                      type="button"
                      className="equipment-howto-toggle"
                      onClick={() => setOpenVideoId(openVideoId === item.id ? null : item.id)}
                    >
                      {openVideoId === item.id ? "Hide video" : "Watch video"}
                    </button>
                  )}
                </div>
                {openId === item.id && (
                  <ol className="equipment-howto-list">
                    {item.how_to.map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ol>
                )}
                {openVideoId === item.id && item.video_id && (
                  <div className="equipment-video-wrap">
                    <iframe
                      src={`https://www.youtube.com/embed/${item.video_id}`}
                      title={`${item.name} demonstration`}
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      loading="lazy"
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}