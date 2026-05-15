import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadResume, analyzeResume, downloadReport } from './services/api';
import toast, { Toaster } from 'react-hot-toast';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
} from 'recharts';
import {
  Upload, FileText, Loader2, CheckCircle, XCircle, Lightbulb,
  Download, Sparkles, Zap, BookOpen, RefreshCw, Brain,
  ChevronDown, ChevronUp, GraduationCap, Briefcase, Award,
  Code2, User, Mail, Phone, Linkedin, Github, BarChart2,
} from 'lucide-react';

const atsColor = (s) => s >= 70 ? '#10b981' : s >= 50 ? '#f59e0b' : '#ef4444';
const atsLabel = (s) => s >= 70 ? 'Excellent' : s >= 50 ? 'Good' : s >= 35 ? 'Fair' : 'Needs Work';

function ScoreArc({ score, size = 140, stroke = 11 }) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const dash = Math.max(0, Math.min(score, 100)) / 100 * circ;
  const color = atsColor(score);
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1e2138" strokeWidth={stroke} />
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={stroke}
        strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
        transform={`rotate(-90 ${size/2} ${size/2})`}
        style={{ transition: 'stroke-dasharray 1.2s cubic-bezier(.4,0,.2,1)' }} />
      <text x={size/2} y={size/2-5} textAnchor="middle" fill={color}
        fontSize={size*0.19} fontWeight="700" fontFamily="Space Grotesk, sans-serif">
        {score.toFixed(0)}%
      </text>
      <text x={size/2} y={size/2+14} textAnchor="middle" fill="#6b7280"
        fontSize={size*0.09} fontFamily="DM Sans, sans-serif">
        {atsLabel(score)}
      </text>
    </svg>
  );
}

function MiniRing({ score, label, color }) {
  const r = 28, circ = 2 * Math.PI * r;
  const dash = Math.max(0, Math.min(score, 100)) / 100 * circ;
  return (
    <div className="flex flex-col items-center gap-1">
      <svg width="70" height="70" viewBox="0 0 70 70">
        <circle cx="35" cy="35" r={r} fill="none" stroke="#1e2138" strokeWidth="6" />
        <circle cx="35" cy="35" r={r} fill="none" stroke={color} strokeWidth="6"
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
          transform="rotate(-90 35 35)"
          style={{ transition: 'stroke-dasharray 1s ease' }} />
        <text x="35" y="40" textAnchor="middle" fill={color}
          fontSize="12" fontWeight="700" fontFamily="Space Grotesk, sans-serif">
          {score.toFixed(0)}%
        </text>
      </svg>
      <span className="text-xs text-gray-400 text-center leading-tight w-16">{label}</span>
    </div>
  );
}

function Badge({ text, found }) {
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium"
      style={{
        background: found ? 'rgba(16,185,129,0.12)' : 'rgba(239,68,68,0.12)',
        color: found ? '#10b981' : '#f87171',
        border: `1px solid ${found ? 'rgba(16,185,129,0.25)' : 'rgba(239,68,68,0.25)'}`,
      }}>
      {found ? <CheckCircle size={10} /> : <XCircle size={10} />}
      {text}
    </span>
  );
}

function Card({ children, className = '', style = {} }) {
  return (
    <div className={`rounded-2xl p-5 ${className}`}
      style={{ background: '#111320', border: '1px solid #1e2138', ...style }}>
      {children}
    </div>
  );
}

function Section({ icon: Icon, title, accent = '#4f6ef7', collapsible, children }) {
  const [open, setOpen] = useState(true);
  return (
    <Card>
      <button className="w-full flex items-center gap-3 mb-4"
        onClick={() => collapsible && setOpen(o => !o)}>
        <span className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ background: `${accent}20` }}>
          <Icon size={16} style={{ color: accent }} />
        </span>
        <span className="font-semibold text-white text-sm flex-1 text-left">{title}</span>
        {collapsible && (open
          ? <ChevronUp size={14} className="text-gray-500" />
          : <ChevronDown size={14} className="text-gray-500" />)}
      </button>
      {open && children}
    </Card>
  );
}

function Steps({ current }) {
  const steps = ['Upload Resume', 'Job Description', 'View Results'];
  return (
    <div className="flex items-center justify-center mb-10">
      {steps.map((s, i) => (
        <React.Fragment key={s}>
          <div className="flex flex-col items-center gap-1.5">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${i < current ? 'bg-green-500 text-white' : i === current ? 'text-white' : 'text-gray-600'}`}
              style={i === current ? { background: 'linear-gradient(135deg,#4f6ef7,#7c3aed)' } : i < current ? {} : { background: '#1e2138' }}>
              {i < current ? <CheckCircle size={14} /> : i + 1}
            </div>
            <span className={`text-xs whitespace-nowrap ${i === current ? 'text-white font-medium' : 'text-gray-500'}`}>{s}</span>
          </div>
          {i < steps.length - 1 && (
            <div className="h-px w-14 mx-2 mb-5 transition-all duration-500"
              style={{ background: i < current ? '#10b981' : '#1e2138' }} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

export default function App() {
  const [step, setStep] = useState(0);
  const [resumeId, setResumeId] = useState(null);
  const [filename, setFilename] = useState('');
  const [jd, setJd] = useState('');
  const [result, setResult] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const onDrop = useCallback(async (accepted) => {
    if (!accepted.length) return;
    const file = accepted[0];
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append('file', file);
      const { data } = await uploadResume(fd);
      setResumeId(data.resume_id);
      setFilename(file.name);
      setStep(1);
      toast.success('Resume parsed!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed');
    } finally { setUploading(false); }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1, disabled: uploading,
  });

  const handleAnalyze = async () => {
    if (jd.trim().length < 50) { toast.error('Please paste a longer job description (50+ chars)'); return; }
    setAnalyzing(true);
    try {
      const { data } = await analyzeResume({ resume_id: resumeId, job_description: jd });
      setResult(data); setStep(2);
      toast.success('Analysis complete!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed');
    } finally { setAnalyzing(false); }
  };

  const handleDownload = async () => {
    setDownloading(true);
    try { await downloadReport(result.id); toast.success('Report downloaded!'); }
    catch { toast.error('Download failed'); }
    finally { setDownloading(false); }
  };

  const reset = () => { setStep(0); setResumeId(null); setFilename(''); setJd(''); setResult(null); };

  const radarData = result ? [
    { metric: 'ATS Score',   value: result.ats_score },
    { metric: 'Skill Match', value: result.skill_match_percentage },
    { metric: 'TF-IDF',      value: result.tfidf_similarity },
    { metric: 'Cosine Sim',  value: result.cosine_similarity },
    { metric: 'Keywords',    value: Math.min(100, result.matched_skills.length * 5) },
  ] : [];

  const barData = result ? [
    { name: 'ATS Score',   v: result.ats_score,              color: atsColor(result.ats_score) },
    { name: 'Skill Match', v: result.skill_match_percentage,  color: '#7c3aed' },
    { name: 'TF-IDF',      v: result.tfidf_similarity,        color: '#3b82f6' },
    { name: 'Cosine Sim',  v: result.cosine_similarity,        color: '#06b6d4' },
  ] : [];

  const Topbar = () => (
    <header className="flex items-center justify-between px-6 py-4 sticky top-0 z-40"
      style={{ background: 'rgba(8,10,20,0.9)', backdropFilter: 'blur(12px)', borderBottom: '1px solid #1e2138' }}>
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ background: 'linear-gradient(135deg,#4f6ef7,#7c3aed)' }}>
          <Brain size={20} className="text-white" />
        </div>
        <div>
          <p className="text-sm font-bold text-white leading-none" style={{ fontFamily: 'Space Grotesk' }}>Resume AI</p>
          <p className="text-xs text-gray-500">ATS Analyzer</p>
        </div>
      </div>
      {step > 0 && (
        <button onClick={reset}
          className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white transition-colors px-3 py-1.5 rounded-lg"
          style={{ background: '#1e2138' }}>
          <RefreshCw size={12} /> New Analysis
        </button>
      )}
    </header>
  );

  /* ── STEP 0 : UPLOAD ─────────────────────────────────────────────────── */
  if (step === 0) return (
    <div className="min-h-screen" style={{ background: '#080a14' }}>
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/3 w-96 h-96 rounded-full blur-3xl opacity-8" style={{ background: '#4f6ef7' }} />
      </div>
      <Toaster position="top-right" toastOptions={{ style: { background: '#111320', color: '#e2e8f0', border: '1px solid #1e2138' } }} />
      <Topbar />
      <div className="relative max-w-xl mx-auto px-4 pt-12 pb-20">
        <Steps current={0} />
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-white mb-3" style={{ fontFamily: 'Space Grotesk' }}>Analyze Your Resume</h1>
          <p className="text-gray-400 text-sm">Instant ATS score, skill gap analysis &amp; improvement tips — no sign-up needed.</p>
        </div>
        <div {...getRootProps()} className="rounded-2xl p-12 text-center cursor-pointer transition-all duration-300"
          style={{ border: `2px dashed ${isDragActive ? '#4f6ef7' : '#252840'}`, background: isDragActive ? 'rgba(79,110,247,0.06)' : '#111320' }}>
          <input {...getInputProps()} />
          {uploading ? (
            <div className="flex flex-col items-center gap-4">
              <Loader2 size={44} className="animate-spin" style={{ color: '#4f6ef7' }} />
              <p className="text-gray-300 font-medium">Parsing your resume...</p>
            </div>
          ) : (
            <>
              <div className="w-18 h-18 rounded-2xl mx-auto mb-5 flex items-center justify-center"
                style={{ background: 'rgba(79,110,247,0.12)', width: 72, height: 72 }}>
                <Upload size={30} style={{ color: '#4f6ef7' }} />
              </div>
              <p className="text-white font-semibold text-xl mb-2">
                {isDragActive ? 'Drop it here!' : 'Drag & drop your resume'}
              </p>
              <p className="text-gray-500 text-sm mb-5">or click to browse files</p>
              <span className="text-xs px-3 py-1.5 rounded-full" style={{ background: '#1e2138', color: '#6b7280' }}>
                PDF · DOCX · Max 10 MB
              </span>
            </>
          )}
        </div>
        <div className="flex flex-wrap justify-center gap-3 mt-8">
          {[{ icon: Zap, t: 'ATS Score' }, { icon: BarChart2, t: 'Skill Match' }, { icon: Lightbulb, t: 'Suggestions' }, { icon: Download, t: 'PDF Export' }].map(({ icon: I, t }) => (
            <div key={t} className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs text-gray-400"
              style={{ background: '#111320', border: '1px solid #1e2138' }}>
              <I size={12} style={{ color: '#4f6ef7' }} /> {t}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  /* ── STEP 1 : JOB DESCRIPTION ─────────────────────────────────────────── */
  if (step === 1) return (
    <div className="min-h-screen" style={{ background: '#080a14' }}>
      <Toaster position="top-right" toastOptions={{ style: { background: '#111320', color: '#e2e8f0', border: '1px solid #1e2138' } }} />
      <Topbar />
      <div className="max-w-xl mx-auto px-4 pt-10 pb-20">
        <Steps current={1} />
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2" style={{ fontFamily: 'Space Grotesk' }}>Paste Job Description</h1>
          <div className="flex items-center gap-2 text-sm">
            <CheckCircle size={14} className="text-green-400" />
            <span className="text-green-400 font-medium truncate max-w-xs">{filename}</span>
            <span className="text-gray-500">ready</span>
          </div>
        </div>
        <Card className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-3">
            Job Description <span className="text-red-400">*</span>
          </label>
          <textarea value={jd} onChange={e => setJd(e.target.value)} rows={14}
            placeholder={"Paste the full job description here...\n\nInclude required skills, responsibilities, qualifications, and nice-to-haves.\n\nMore detail = better analysis!"}
            className="w-full rounded-xl p-4 text-sm text-gray-200 placeholder-gray-600 outline-none resize-none leading-relaxed"
            style={{ background: '#080a14', border: '1px solid #1e2138' }}
            onFocus={e => e.target.style.borderColor = '#4f6ef7'}
            onBlur={e => e.target.style.borderColor = '#1e2138'}
          />
          <div className="flex justify-between mt-2">
            <span className="text-xs text-gray-600">{jd.length} chars</span>
            <span className={`text-xs ${jd.length >= 50 ? 'text-green-500' : 'text-gray-600'}`}>
              {jd.length >= 50 ? '✓ Ready' : `${50 - jd.length} more needed`}
            </span>
          </div>
        </Card>
        <div className="flex gap-3">
          <button onClick={() => setStep(0)}
            className="flex items-center gap-2 px-4 py-3 rounded-xl text-sm text-gray-400 hover:text-white"
            style={{ background: '#1e2138' }}>← Back</button>
          <button onClick={handleAnalyze} disabled={analyzing || jd.length < 50}
            className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-white disabled:opacity-40"
            style={{ background: 'linear-gradient(135deg,#4f6ef7,#7c3aed)' }}>
            {analyzing
              ? <><Loader2 size={18} className="animate-spin" /> Analyzing...</>
              : <><Sparkles size={18} /> Analyze Resume</>}
          </button>
        </div>
      </div>
    </div>
  );

  /* ── STEP 2 : RESULTS ─────────────────────────────────────────────────── */
  if (step === 2 && result) {
    const ac = atsColor(result.ats_score);
    const info = result.extracted_info || {};
    return (
      <div className="min-h-screen" style={{ background: '#080a14' }}>
        <Toaster position="top-right" toastOptions={{ style: { background: '#111320', color: '#e2e8f0', border: '1px solid #1e2138' } }} />
        <Topbar />
        <div className="max-w-5xl mx-auto px-4 pt-8 pb-20">
          <Steps current={2} />
          {/* action bar */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Space Grotesk' }}>Analysis Results</h1>
              {result.job_title_guess && (
                <p className="text-sm text-gray-400 mt-0.5">Target role: <span style={{ color: '#a5b4fc' }}>{result.job_title_guess}</span></p>
              )}
            </div>
            <button onClick={handleDownload} disabled={downloading}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold text-white disabled:opacity-50"
              style={{ background: 'linear-gradient(135deg,#4f6ef7,#7c3aed)' }}>
              {downloading ? <Loader2 size={15} className="animate-spin" /> : <Download size={15} />} Export PDF
            </button>
          </div>

          {/* Score row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-5">
            <Card className="flex flex-col items-center justify-center py-6">
              <ScoreArc score={result.ats_score} />
              <p className="text-xs text-gray-500 mt-1">Overall ATS Score</p>
              <span className="mt-3 px-3 py-1 rounded-full text-xs font-semibold"
                style={{ background: `${ac}20`, color: ac }}>{atsLabel(result.ats_score)} Match</span>
            </Card>
            <Card className="flex flex-col justify-center">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-4">Score Breakdown</p>
              <div className="grid grid-cols-2 gap-4">
                <MiniRing score={result.skill_match_percentage} label="Skill Match" color="#7c3aed" />
                <MiniRing score={result.tfidf_similarity} label="TF-IDF Sim" color="#3b82f6" />
                <MiniRing score={result.cosine_similarity} label="Cosine Sim" color="#06b6d4" />
                <MiniRing score={Math.min(100, result.matched_skills.length * 5)} label="Keyword Hit" color="#10b981" />
              </div>
            </Card>
            <Card>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Radar Overview</p>
              <ResponsiveContainer width="100%" height={170}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#1e2138" />
                  <PolarAngleAxis dataKey="metric" tick={{ fill: '#6b7280', fontSize: 10 }} />
                  <Radar dataKey="value" stroke="#4f6ef7" fill="#4f6ef7" fillOpacity={0.2} strokeWidth={2} />
                </RadarChart>
              </ResponsiveContainer>
            </Card>
          </div>

          {/* Bar chart */}
          <Card className="mb-5">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Score Comparison</p>
            <ResponsiveContainer width="100%" height={110}>
              <BarChart data={barData} layout="vertical" barSize={12}>
                <XAxis type="number" domain={[0,100]} tick={{ fill:'#6b7280', fontSize:11 }} />
                <YAxis type="category" dataKey="name" width={90} tick={{ fill:'#9ca3af', fontSize:11 }} />
                <Tooltip contentStyle={{ background:'#111320', border:'1px solid #1e2138', borderRadius:10 }}
                  formatter={v => [`${v.toFixed(1)}%`]} labelStyle={{ color:'#9ca3af' }} />
                <Bar dataKey="v" radius={[0,6,6,0]}>
                  {barData.map((e,i) => <Cell key={i} fill={e.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Summary */}
          <Section icon={BookOpen} title="Resume Summary" accent="#6366f1">
            <p className="text-sm text-gray-300 leading-relaxed">{result.summary}</p>
          </Section>
          <div className="mb-4" />

          {/* Skills */}
          <div className="grid lg:grid-cols-2 gap-4 mb-4">
            <Section icon={CheckCircle} title={`Matched Skills (${result.matched_skills.length})`} accent="#10b981">
              {result.matched_skills.length > 0
                ? <div className="flex flex-wrap gap-2">{result.matched_skills.map(s => <Badge key={s} text={s} found />)}</div>
                : <p className="text-sm text-gray-500">No skills matched. Add more relevant skills to your resume.</p>}
            </Section>
            <Section icon={XCircle} title={`Missing Skills (${result.missing_skills.length})`} accent="#ef4444">
              {result.missing_skills.length > 0
                ? <div className="flex flex-wrap gap-2">{result.missing_skills.map(s => <Badge key={s} text={s} found={false} />)}</div>
                : <p className="text-sm text-green-400 font-medium">You matched all required skills!</p>}
            </Section>
          </div>

          {/* Suggestions */}
          <Section icon={Lightbulb} title="Improvement Suggestions" accent="#f59e0b">
            <div className="space-y-2.5">
              {result.suggestions.map((s, i) => (
                <div key={i} className="flex gap-3 p-3 rounded-xl" style={{ background:'#080a14' }}>
                  <span className="w-6 h-6 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold"
                    style={{ background:'rgba(245,158,11,0.15)', color:'#f59e0b' }}>{i+1}</span>
                  <p className="text-sm text-gray-300 leading-relaxed">{s}</p>
                </div>
              ))}
            </div>
          </Section>
          <div className="mb-4" />

          {/* Extracted Info */}
          <Section icon={Zap} title="Extracted Information" accent="#3b82f6" collapsible>
            <div className="grid md:grid-cols-2 gap-5">
              {[
                { key:'education',      label:'Education',      icon:GraduationCap, color:'#6366f1' },
                { key:'experience',     label:'Experience',     icon:Briefcase,     color:'#f59e0b' },
                { key:'certifications', label:'Certifications', icon:Award,         color:'#10b981' },
                { key:'projects',       label:'Projects',       icon:Code2,         color:'#3b82f6' },
              ].map(({ key, label, icon: Icon, color }) => (
                <div key={key}>
                  <div className="flex items-center gap-2 mb-2">
                    <Icon size={12} style={{ color }} />
                    <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">{label}</span>
                  </div>
                  {info[key]?.length > 0
                    ? <ul className="space-y-1">{info[key].map((item,i) => <li key={i} className="text-xs text-gray-300 flex gap-2"><span style={{ color }}>•</span>{item}</li>)}</ul>
                    : <p className="text-xs text-gray-600 italic">Not detected</p>}
                </div>
              ))}
            </div>
            {info.skills?.length > 0 && (
              <div className="mt-5 pt-4" style={{ borderTop:'1px solid #1e2138' }}>
                <div className="flex items-center gap-2 mb-2">
                  <Code2 size={12} style={{ color:'#a78bfa' }} />
                  <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">All Detected Skills</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {info.skills.map(s => (
                    <span key={s} className="text-xs px-2 py-0.5 rounded-full" style={{ background:'#1e2138', color:'#a5b4fc' }}>{s}</span>
                  ))}
                </div>
              </div>
            )}
            {info.contact && Object.keys(info.contact).length > 0 && (
              <div className="mt-5 pt-4" style={{ borderTop:'1px solid #1e2138' }}>
                <div className="flex items-center gap-2 mb-2">
                  <User size={12} style={{ color:'#34d399' }} />
                  <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">Contact Info</span>
                </div>
                <div className="flex flex-wrap gap-4">
                  {info.contact.email    && <span className="flex items-center gap-1.5 text-xs text-gray-300"><Mail     size={11} className="text-blue-400"  />{info.contact.email}</span>}
                  {info.contact.phone    && <span className="flex items-center gap-1.5 text-xs text-gray-300"><Phone    size={11} className="text-green-400" />{info.contact.phone}</span>}
                  {info.contact.linkedin && <span className="flex items-center gap-1.5 text-xs text-gray-300"><Linkedin size={11} className="text-blue-400"  />{info.contact.linkedin}</span>}
                  {info.contact.github   && <span className="flex items-center gap-1.5 text-xs text-gray-300"><Github   size={11} className="text-gray-300"  />{info.contact.github}</span>}
                </div>
              </div>
            )}
          </Section>

          {/* CTA */}
          <div className="mt-6 p-5 rounded-2xl flex items-center justify-between"
            style={{ background:'linear-gradient(135deg,rgba(79,110,247,0.1),rgba(124,58,237,0.1))', border:'1px solid rgba(79,110,247,0.2)' }}>
            <div>
              <p className="text-white font-semibold text-sm">Try with another resume?</p>
              <p className="text-gray-500 text-xs mt-0.5">Start a new analysis instantly</p>
            </div>
            <button onClick={reset} className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white"
              style={{ background:'linear-gradient(135deg,#4f6ef7,#7c3aed)' }}>
              <RefreshCw size={14} /> New Analysis
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
