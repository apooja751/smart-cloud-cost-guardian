import React, { useState } from 'react';
import { Sparkles, Send, Bot, User, HelpCircle, ShieldCheck, ArrowRight } from 'lucide-react';
import api from '../services/api';
import { useAWSAccount } from '../context/AWSAccountContext';

interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  intent?: string;
  followups?: string[];
}

export const AIAssistantPage: React.FC = () => {
  const { activeAccount } = useAWSAccount();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: 'ai',
      text: `Hello! I am your **Smart Cloud Cost Guardian AI FinOps Copilot**.\n\nI am connected to your live AWS telemetry, Cost Explorer history, and resource utilization records.\n\nAsk me anything about your current spend, top idle waste resources, health score drivers, or database optimization!`,
      followups: [
        'Why are our EC2 costs high this month?',
        'What are the top 3 idle resources incurring waste?',
        'Explain our Cloud Health Score breakdown.'
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg: ChatMessage = { sender: 'user', text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.post('/assistant/ask', {
        question: textToSend,
        aws_account_id: activeAccount?.id
      });
      if (res.data.success) {
        const aiMsg: ChatMessage = {
          sender: 'ai',
          text: res.data.data.answer,
          intent: res.data.data.intent,
          followups: res.data.data.suggested_followups
        };
        setMessages((prev) => [...prev, aiMsg]);
      }
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { sender: 'ai', text: 'Sorry, I encountered an error querying your AWS metrics. Please verify account connectivity.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
          <Sparkles className="w-7 h-7 text-indigo-400" />
          <span>AI FinOps Copilot</span>
        </h1>
        <p className="text-xs md:text-sm text-slate-400 mt-1">
          Zero-hallucination conversational cloud intelligence grounded directly in your factual AWS dataset.
        </p>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 glass-panel rounded-3xl p-6 border border-slate-800 overflow-y-auto space-y-4">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex items-start gap-3 ${m.sender === 'user' ? 'flex-row-reverse' : ''}`}>
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 ${
                m.sender === 'ai'
                  ? 'bg-gradient-to-tr from-indigo-600 to-sky-600 text-white shadow-md'
                  : 'bg-slate-800 text-slate-300'
              }`}
            >
              {m.sender === 'ai' ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
            </div>

            <div
              className={`max-w-2xl rounded-2xl p-4 text-xs md:text-sm leading-relaxed whitespace-pre-wrap ${
                m.sender === 'user'
                  ? 'bg-sky-600 text-white font-medium'
                  : 'bg-slate-900/90 text-slate-200 border border-slate-800'
              }`}
            >
              {m.text}

              {/* Suggested Followups */}
              {m.followups && m.followups.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-800 space-y-1.5">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                    Suggested Inquiries:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {m.followups.map((f, fIdx) => (
                      <button
                        key={fIdx}
                        onClick={() => handleSend(f)}
                        className="text-xs px-3 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-sky-300 border border-slate-700 transition text-left"
                      >
                        {f}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center animate-pulse">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-3 rounded-2xl bg-slate-900 text-xs text-slate-400 animate-pulse border border-slate-800">
              Querying AWS telemetry and synthesizing factual FinOps recommendation...
            </div>
          </div>
        )}
      </div>

      {/* Input Bar */}
      <div className="glass-panel p-2.5 rounded-2xl border border-slate-800 flex items-center gap-2">
        <input
          type="text"
          placeholder="Ask anything about your cloud spend, idle servers, or budget projections..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          className="flex-1 bg-transparent px-4 py-2 text-xs md:text-sm text-white focus:outline-none placeholder:text-slate-500"
        />
        <button
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
          className="p-2.5 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 text-white font-bold shadow disabled:opacity-50 transition"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
