import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Activity, ShieldCheck, Zap, Video, ChevronRight, ActivitySquare, CheckCircle, AlertTriangle, Download } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './index.css';

function App() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [loadingText, setLoadingText] = useState("INITIALIZING ENGINE...");

  React.useEffect(() => {
    if (!isProcessing) return;
    const messages = [
      "EXTRACTING SPATIAL LANDMARKS...",
      "SMOOTHING 3D COORDINATES...",
      "CALCULATING JOINT KINEMATICS...",
      "ALIGNING DTW TEMPO MODEL...",
      "INFERRING BIOMECHANICAL DEVIATIONS...",
      "GENERATING AI COACH FEEDBACK..."
    ];
    let i = 0;
    setLoadingText(messages[0]);
    const interval = setInterval(() => {
      i = (i + 1) % messages.length;
      setLoadingText(messages[i]);
    }, 2500);
    return () => clearInterval(interval);
  }, [isProcessing]);

  const handleDrag = (e) => {
    e.preventDefault(); e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setIsDragging(true);
    else if (e.type === "dragleave") setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault(); e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) setFile(e.target.files[0]);
  };

  const handleProcess = async () => {
    if (!file) return;
    setIsProcessing(true); setError(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/api/analyze", { method: "POST", body: formData });
      if (!response.ok) throw new Error("Analysis failed. Please ensure it's a valid video format.");
      const data = await response.json();
      
      // Transform telemetry data for Recharts
      if (data.telemetry) {
        const angleKey = data.exercise === "squat" ? "knee_flexion" : (data.exercise === "pullup" ? "elbow_flexion" : "hip_extension");
        
        data.chartData = data.telemetry.map(frame => ({
          frame: frame.frame_number,
          PrimaryAngle: frame.angles[angleKey],
          TorsoLean: frame.angles.torso_lean
        }));
      }

      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const resetState = () => { setFile(null); setResults(null); setError(null); };

  const staggerContainer = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.1 } } };
  const itemFadeUp = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } } };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      <motion.header initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} style={{ padding: '2rem 4rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={resetState}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: 'var(--grad-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Activity color="#fff" size={24} /></div>
          <span style={{ fontSize: '1.5rem', fontWeight: 700, letterSpacing: '-0.03em' }}>GYM<span style={{ color: 'var(--neon-cyan)' }}>BRO</span></span>
        </div>
        <button className="btn-outline">Documentation</button>
      </motion.header>

      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '2rem 4rem' }}>
        <AnimatePresence mode="wait">
          
          {/* Landing / Upload */}
          {!file && !results && (
            <motion.div key="landing" variants={staggerContainer} initial="hidden" animate="show" exit={{ opacity: 0, y: -20, filter: 'blur(10px)' }} style={{ maxWidth: 1200, width: '100%', marginTop: '4rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '4rem', alignItems: 'center' }}>
                <div>
                  <motion.div variants={itemFadeUp} style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 16px', background: 'rgba(0, 229, 255, 0.1)', border: '1px solid rgba(0, 229, 255, 0.2)', borderRadius: 100, marginBottom: '2rem', color: 'var(--neon-cyan)', fontWeight: 600, fontSize: '0.875rem' }}><Zap size={16} fill="var(--neon-cyan)" /> V2.0 Computer Vision Engine Active</motion.div>
                  <motion.h1 variants={itemFadeUp} style={{ marginBottom: '1.5rem' }}>Flawless Form. <br/>Powered by AI.</motion.h1>
                  <motion.p variants={itemFadeUp} style={{ color: 'var(--text-dim)', fontSize: '1.25rem', marginBottom: '3rem', maxWidth: 500, lineHeight: 1.8 }}>Upload your raw lifting footage. Our neural networks reconstruct your biomechanics in 3D to deliver elite, frame-by-frame coaching feedback.</motion.p>
                </div>
                <motion.div variants={itemFadeUp}>
                  <label className={`upload-zone glass-card ${isDragging ? 'drag-active' : ''}`} onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
                    <input type="file" accept="video/mp4,video/quicktime" style={{ display: 'none' }} onChange={handleChange} />
                    <motion.div animate={{ y: [0, -10, 0] }} transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }} style={{ width: 80, height: 80, borderRadius: '50%', background: 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '2rem', border: '1px solid rgba(255,255,255,0.1)' }}><Upload size={32} color="var(--neon-cyan)" /></motion.div>
                    <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Drop your video here</h3>
                    <p style={{ color: 'var(--text-dim)', marginBottom: '2rem' }}>MP4 or MOV up to 50MB</p>
                    <div className="btn-cyber">Select File</div>
                  </label>
                </motion.div>
              </div>
            </motion.div>
          )}

          {/* Processing */}
          {file && !results && (
            <motion.div key="processing" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }} style={{ maxWidth: 800, width: '100%', marginTop: '4rem' }}>
              <div className="glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16, marginBottom: '2rem' }}><Video size={32} color="var(--text-dim)" /><h2 style={{ fontSize: '2rem' }} className="mono-text">{file.name}</h2></div>
                {isProcessing ? (
                  <div style={{ position: 'relative', height: 200, background: 'rgba(0,0,0,0.5)', borderRadius: 16, overflow: 'hidden', marginBottom: '3rem', border: '1px solid rgba(255,255,255,0.1)' }}><div className="scanner-line"></div><div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: 'var(--neon-cyan)', fontFamily: 'JetBrains Mono', letterSpacing: 2, textAlign: 'center', width: '100%' }}>{loadingText}</div></div>
                ) : (
                  <div style={{ marginBottom: '3rem' }}><p style={{ color: 'var(--text-dim)' }}>File loaded. Ready to deploy spatial tracking algorithms.</p></div>
                )}
                {error && <div style={{ color: 'var(--neon-pink)', marginBottom: '1rem', padding: '1rem', background: 'rgba(255,0,127,0.1)', borderRadius: 8 }}>{error}</div>}
                <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}><button className="btn-outline" onClick={resetState} disabled={isProcessing}>Cancel</button><button className="btn-cyber" onClick={handleProcess} disabled={isProcessing}>{isProcessing ? 'Processing...' : 'Initialize Engine'} <ChevronRight size={20}/></button></div>
              </div>
            </motion.div>
          )}

          {/* Results Dashboard */}
          {results && (
            <motion.div key="results" variants={staggerContainer} initial="hidden" animate="show" style={{ maxWidth: 1400, width: '100%', marginTop: '1rem' }}>
              <motion.div variants={itemFadeUp} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                  <h2 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', textTransform: 'capitalize' }}>{results.exercise} Analysis</h2>
                  <div style={{ display: 'flex', gap: '1rem', color: 'var(--neon-cyan)' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}><CheckCircle size={16}/> Vision Tracked</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}><CheckCircle size={16}/> Biometrics Mapped</span>
                  </div>
                </div>
                <button className="btn-outline" onClick={resetState}>Analyze New Video</button>
              </motion.div>

              <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '2rem' }}>
                {/* Left Col: Video & Graph */}
                <motion.div variants={itemFadeUp} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                  <div className="glass-card" style={{ padding: '1.5rem' }}>
                    <div style={{ marginBottom: '1rem', color: 'var(--text-dim)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}><ActivitySquare size={18}/> SYNCHRONIZED POSE VIDEO</div>
                    <video controls autoPlay style={{ width: '100%', borderRadius: 12, border: '1px solid rgba(255,255,255,0.05)' }} src={`http://localhost:8000/${results.files.output_video.replace(/\\/g, '/')}`} />
                  </div>

                  {/* Telemetry Graph */}
                  {results.chartData && (
                    <div className="glass-card" style={{ padding: '1.5rem', height: 400 }}>
                      <div style={{ marginBottom: '1rem', color: 'var(--text-dim)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
                        <ActivitySquare size={18}/> KINEMATICS TELEMETRY
                      </div>
                      <ResponsiveContainer width="100%" height="90%">
                        <LineChart data={results.chartData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                          <XAxis dataKey="frame" stroke="var(--text-dim)" tick={{fill: 'var(--text-dim)'}} />
                          <YAxis stroke="var(--text-dim)" tick={{fill: 'var(--text-dim)'}} />
                          <Tooltip 
                            contentStyle={{ backgroundColor: 'var(--bg-panel)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#fff' }}
                            itemStyle={{ color: '#fff' }}
                          />
                          <Legend />
                          <Line type="monotone" name="Primary Joint Angle" dataKey="PrimaryAngle" stroke="var(--neon-cyan)" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                          <Line type="monotone" name="Torso Lean" dataKey="TorsoLean" stroke="var(--neon-purple)" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </motion.div>

                {/* Right Col: Telemetry & Coach */}
                <motion.div variants={itemFadeUp} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                  <div className="glass-card" style={{ padding: '2rem', background: 'rgba(157, 78, 221, 0.05)', borderColor: 'rgba(157, 78, 221, 0.2)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: '1.5rem' }}>
                      <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--grad-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>AI</div>
                      <div><div style={{ fontWeight: 600 }}>Gym Bro Coach</div><div style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>Powered by OpenRouter</div></div>
                    </div>
                    <p style={{ fontSize: '1.1rem', lineHeight: 1.7 }}>"{results.coach_feedback}"</p>
                  </div>

                  {/* Specific Lift Metrics */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    {results.exercise === "squat" && (
                      <>
                        <div className="glass-card" style={{ padding: '1.5rem' }}>
                          <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>DEEPEST KNEE ANGLE</div>
                          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--neon-cyan)' }}>{results.metrics.deepest_knee_angle?.toFixed(1)}°</div>
                          <div style={{ fontSize: '0.9rem', color: results.metrics.hit_depth ? 'var(--cyber-green)' : 'var(--neon-pink)', marginTop: 4 }}>
                            {results.metrics.hit_depth ? 'Optimal Depth' : 'Shallow Depth'}
                          </div>
                        </div>
                        <div className="glass-card" style={{ padding: '1.5rem' }}>
                          <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>MAX TORSO LEAN</div>
                          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--neon-purple)' }}>{results.metrics.max_torso_lean_at_bottom?.toFixed(1)}°</div>
                          <div style={{ fontSize: '0.9rem', color: results.metrics.max_torso_lean_at_bottom <= 45 ? 'var(--cyber-green)' : 'var(--neon-pink)', marginTop: 4 }}>
                            {results.metrics.max_torso_lean_at_bottom <= 45 ? 'Optimal Posture' : 'Excessive Lean'}
                          </div>
                        </div>
                      </>
                    )}
                    {results.exercise === "pullup" && (
                      <>
                        <div className="glass-card" style={{ padding: '1.5rem' }}>
                          <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>TOP ELBOW FLEXION</div>
                          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--neon-cyan)' }}>{results.metrics.min_elbow_angle?.toFixed(1)}°</div>
                          <div style={{ fontSize: '0.9rem', color: results.metrics.top_reached ? 'var(--cyber-green)' : 'var(--neon-pink)', marginTop: 4 }}>
                            {results.metrics.top_reached ? 'Strong Top' : 'Needs More Pull'}
                          </div>
                        </div>
                        <div className="glass-card" style={{ padding: '1.5rem' }}>
                          <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>TORSO LEAN AT TOP</div>
                          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--neon-purple)' }}>{results.metrics.torso_lean_at_top?.toFixed(1)}°</div>
                          <div style={{ fontSize: '0.9rem', color: results.metrics.torso_lean_at_top <= 35 ? 'var(--cyber-green)' : 'var(--neon-pink)', marginTop: 4 }}>
                            {results.metrics.torso_lean_at_top <= 35 ? 'Controlled' : 'Swinging'}
                          </div>
                        </div>
                      </>
                    )}
                    {results.exercise === "deadlift" && (
                      <>
                        <div className="glass-card" style={{ padding: '1.5rem' }}>
                          <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>MAX HIP EXTENSION</div>
                          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--neon-cyan)' }}>{results.metrics.max_hip_extension?.toFixed(1)}°</div>
                          <div style={{ fontSize: '0.9rem', color: results.metrics.has_lockout ? 'var(--cyber-green)' : 'var(--neon-pink)', marginTop: 4 }}>
                            {results.metrics.has_lockout ? 'Fully Locked' : 'Partial Lockout'}
                          </div>
                        </div>
                        <div className="glass-card" style={{ padding: '1.5rem' }}>
                          <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>SPINE CHECK</div>
                          <div style={{ fontSize: '2rem', fontWeight: 700, color: results.metrics.back_rounding_warning ? 'var(--neon-pink)' : 'var(--cyber-green)' }}>
                            {results.metrics.back_rounding_warning ? 'Warning' : 'Safe'}
                          </div>
                          <div style={{ fontSize: '0.9rem', color: results.metrics.back_rounding_warning ? 'var(--neon-pink)' : 'var(--cyber-green)', marginTop: 4 }}>
                            {results.metrics.back_rounding_warning ? 'Rounding Alert' : 'Clean Back'}
                          </div>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Tempo Metrics */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div className="glass-card" style={{ padding: '1.5rem' }}>
                      <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>DTW TEMPO SCORE</div>
                      <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--neon-cyan)' }}>{results.tempo.dtw_score ? results.tempo.dtw_score.toFixed(1) : 'N/A'}</div>
                      <div style={{ fontSize: '0.9rem', color: 'var(--text-pure)', marginTop: 4 }}>{results.tempo.tempo_label || 'Analysis unavailable'}</div>
                    </div>
                    <div className="glass-card" style={{ padding: '1.5rem' }}>
                      <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>SPEED RATIO</div>
                      <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--neon-purple)' }}>{results.tempo.speed_ratio ? `${results.tempo.speed_ratio.toFixed(2)}x` : 'N/A'}</div>
                      <div style={{ fontSize: '0.9rem', color: 'var(--text-pure)', marginTop: 4 }}>{results.tempo.speed_warning ? <span style={{ color: 'var(--neon-pink)', display: 'flex', alignItems: 'center', gap: 4 }}><AlertTriangle size={14}/> Warning</span> : 'Optimal Speed'}</div>
                    </div>
                  </div>

                  {results.metrics.overall_feedback && (
                    <div className="glass-card" style={{ padding: '1.5rem', background: 'rgba(255, 255, 255, 0.02)' }}>
                      <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Kinematic Summary</div>
                      <p style={{ fontSize: '1rem', color: '#e2e8f0' }}>{results.metrics.overall_feedback}</p>
                    </div>
                  )}

                  {/* CSV Downloads */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <a href={`http://localhost:8000/${results.files.raw_csv.replace(/\\/g, '/')}`} download className="btn-outline" style={{ justifyContent: 'center', fontSize: '0.9rem' }}>
                      <Download size={16}/> Raw Coordinates (CSV)
                    </a>
                    <a href={`http://localhost:8000/${results.files.smoothed_csv.replace(/\\/g, '/')}`} download className="btn-outline" style={{ justifyContent: 'center', fontSize: '0.9rem' }}>
                      <Download size={16}/> Smoothed Coordinates (CSV)
                    </a>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
