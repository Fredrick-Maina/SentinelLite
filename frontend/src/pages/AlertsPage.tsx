import React, { useEffect, useState } from 'react';
import { AIAnalysis, Alert, AlertStatus } from '../types';
import { api } from '../services/api';
import { ShieldAlert, Sparkles, Filter, CheckCircle2, AlertOctagon, RefreshCw, X } from 'lucide-react';

interface AlertsPageProps {
  activeOrgId: string;
}

export const AlertsPage: React.FC<AlertsPageProps> = ({ activeOrgId }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [newNote, setNewNote] = useState('');
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadAlerts = () => {
    if (!activeOrgId) return;
    setLoading(true);
    api.getAlerts(activeOrgId, statusFilter, severityFilter)
      .then(setAlerts)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAlerts();
  }, [activeOrgId, statusFilter, severityFilter]);

  const handleSelectAlert = (alert: Alert) => {
    api.getAlertDetail(activeOrgId, alert.id)
      .then(data => {
        setSelectedAlert(data);
        setAiAnalysis(null);
      })
      .catch(console.error);
  };

  const handleStatusChange = async (alertId: string, newStatus: AlertStatus) => {
    try {
      const updated = await api.updateAlertStatus(activeOrgId, alertId, newStatus);
      if (selectedAlert && selectedAlert.id === alertId) {
        setSelectedAlert({ ...selectedAlert, status: updated.status });
      }
      loadAlerts();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAlert || !newNote.trim()) return;
    try {
      await api.addInvestigationNote(activeOrgId, selectedAlert.id, newNote);
      setNewNote('');
      const refreshed = await api.getAlertDetail(activeOrgId, selectedAlert.id);
      setSelectedAlert(refreshed);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunAI = async () => {
    if (!selectedAlert) return;
    setAiLoading(true);
    try {
      const result = await api.runAIAnalysis(activeOrgId, selectedAlert.id);
      setAiAnalysis(result);
    } catch (err) {
      console.error(err);
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header & Filter Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Security Alerts Workspace</h1>
          <p className="text-sm text-slate-400">Triage, investigate, and analyze security incidents</p>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-sm">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="" className="bg-slate-900">All Statuses</option>
              <option value="NEW" className="bg-slate-900">NEW</option>
              <option value="ACKNOWLEDGED" className="bg-slate-900">ACKNOWLEDGED</option>
              <option value="INVESTIGATING" className="bg-slate-900">INVESTIGATING</option>
              <option value="RESOLVED" className="bg-slate-900">RESOLVED</option>
              <option value="FALSE_POSITIVE" className="bg-slate-900">FALSE_POSITIVE</option>
            </select>
          </div>

          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-sm">
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="" className="bg-slate-900">All Severities</option>
              <option value="CRITICAL" className="bg-slate-900">CRITICAL</option>
              <option value="HIGH" className="bg-slate-900">HIGH</option>
              <option value="MEDIUM" className="bg-slate-900">MEDIUM</option>
              <option value="LOW" className="bg-slate-900">LOW</option>
            </select>
          </div>
        </div>
      </div>

      {/* Alert List */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-500">Loading alerts...</div>
        ) : alerts.length === 0 ? (
          <div className="p-12 text-center text-slate-500 space-y-2">
            <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-400" />
            <div>No alerts matching the selected filters.</div>
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                onClick={() => handleSelectAlert(alert)}
                className={`p-5 flex items-center justify-between cursor-pointer transition-colors ${
                  selectedAlert?.id === alert.id ? 'bg-slate-800/80 border-l-4 border-l-emerald-400' : 'hover:bg-slate-900/60'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-0.5 text-xs font-bold rounded ${
                      alert.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                      alert.severity === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                      'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    }`}>
                      {alert.severity}
                    </span>
                    <h4 className="font-semibold text-slate-100 text-sm">{alert.title}</h4>
                  </div>
                  <p className="text-xs text-slate-400">{alert.description}</p>
                </div>

                <div className="flex items-center space-x-4">
                  <span className="text-xs font-mono bg-slate-900 px-2.5 py-1 rounded text-slate-300 border border-slate-800">
                    Status: {alert.status}
                  </span>
                  <span className="text-xs text-slate-500 font-mono">
                    {new Date(alert.last_seen).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Alert Detail & AI Analyst Modal Drawer */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex justify-end">
          <div className="w-full max-w-2xl bg-slate-900 border-l border-slate-800 h-full overflow-y-auto p-6 space-y-6 shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <ShieldAlert className="w-6 h-6 text-emerald-400" />
                <h3 className="font-bold text-lg text-slate-100">Alert Details & Triage</h3>
              </div>
              <button onClick={() => setSelectedAlert(null)} className="p-1 text-slate-400 hover:text-slate-100">
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Alert Title & Status Selector */}
            <div className="space-y-4">
              <div>
                <span className="text-xs font-mono text-emerald-400">ALERT ID: {selectedAlert.id}</span>
                <h2 className="text-xl font-bold text-slate-100 mt-1">{selectedAlert.title}</h2>
                <p className="text-sm text-slate-300 mt-2">{selectedAlert.description}</p>
              </div>

              {/* Triage Status Control */}
              <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 space-y-2">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Update Triage Status</label>
                <div className="flex flex-wrap gap-2">
                  {(['NEW', 'ACKNOWLEDGED', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE'] as AlertStatus[]).map((st) => (
                    <button
                      key={st}
                      onClick={() => handleStatusChange(selectedAlert.id, st)}
                      className={`px-3 py-1.5 text-xs font-bold rounded-lg border transition-all ${
                        selectedAlert.status === st
                          ? 'bg-emerald-500 text-slate-950 border-emerald-400'
                          : 'bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      {st}
                    </button>
                  ))}
                </div>
              </div>

              {/* AI Analyst Assistant Button */}
              <div className="p-4 bg-emerald-950/20 border border-emerald-500/30 rounded-xl space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-emerald-400">
                    <Sparkles className="w-5 h-5" />
                    <span className="font-bold text-sm">AI Security Analyst Assistant</span>
                  </div>
                  <button
                    onClick={handleRunAI}
                    disabled={aiLoading}
                    className="px-3 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg transition-colors shadow-md flex items-center space-x-1"
                  >
                    {aiLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                    <span>{aiLoading ? 'Analyzing Evidence...' : 'Generate AI Explanation'}</span>
                  </button>
                </div>

                {aiAnalysis && (
                  <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 space-y-3 text-xs">
                    <div>
                      <span className="font-bold text-slate-300">Summary:</span>
                      <p className="text-slate-400 mt-0.5">{aiAnalysis.summary}</p>
                    </div>
                    <div>
                      <span className="font-bold text-slate-300">Technical Narrative:</span>
                      <p className="text-slate-400 mt-0.5">{aiAnalysis.explanation}</p>
                    </div>
                    {aiAnalysis.recommended_actions && (
                      <div>
                        <span className="font-bold text-emerald-400">Recommended Actions:</span>
                        <ul className="list-disc list-inside text-slate-300 mt-1 space-y-1">
                          {aiAnalysis.recommended_actions.map((act, i) => (
                            <li key={i}>{act}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Notes & Evidence */}
              <div className="space-y-4">
                <h4 className="font-semibold text-slate-200 text-sm">Analyst Investigation Notes</h4>
                <form onSubmit={handleAddNote} className="space-y-2">
                  <textarea
                    rows={3}
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    placeholder="Add an investigation note or threat intelligence finding..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
                  />
                  <button type="submit" className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-lg">
                    Add Note
                  </button>
                </form>

                <div className="space-y-2">
                  {selectedAlert.investigation_notes?.map(n => (
                    <div key={n.id} className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs space-y-1">
                      <div className="flex justify-between font-mono text-slate-400">
                        <span className="font-bold text-slate-200">{n.author_name}</span>
                        <span>{new Date(n.created_at).toLocaleString()}</span>
                      </div>
                      <p className="text-slate-300">{n.note}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
