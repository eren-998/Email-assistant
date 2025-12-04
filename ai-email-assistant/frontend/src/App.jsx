import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
    Menu, Search, Settings, Grid,
    Inbox, Star, Send as SendIcon, Trash2,
    Plus, Sparkles, X, ChevronLeft,
    RefreshCw, Loader2, LogOut, Moon, Sun, Key,
    MessageSquare, Zap, Maximize2, ExternalLink
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_URL = 'http://localhost:8000';

// LocalStorage keys
const STORAGE_KEYS = {
    GEMINI_KEY: 'ai_email_gemini_key',
    SELECTED_MODEL: 'ai_email_selected_model',
    CHAT_HISTORY: 'ai_email_chat_history',
    USER_EMAIL: 'ai_email_user_email'
};

function App() {
    // --- STATE MANAGEMENT ---
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [hasGeminiKey, setHasGeminiKey] = useState(false);
    const [userEmail, setUserEmail] = useState('');
    const [emails, setEmails] = useState([]);

    // Chat State
    const [chatInput, setChatInput] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [isProcessing, setIsProcessing] = useState(false);

    // UI State
    const [showSettings, setShowSettings] = useState(false);
    const [geminiKeyInput, setGeminiKeyInput] = useState('');
    const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
    const [showNotification, setShowNotification] = useState(null);
    const [emailsLoading, setEmailsLoading] = useState(false);

    // New UI Layout States
    const [selectedEmail, setSelectedEmail] = useState(null);
    const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');

    // Summary State
    const [summarizeEmail, setSummarizeEmail] = useState(null);
    const [summarizeResult, setSummarizeResult] = useState('');
    const [summarizeLoading, setSummarizeLoading] = useState(false);
    const [summarizeError, setSummarizeError] = useState('');
    const chatEndRef = useRef(null);

    // Login State
    const [loginEmail, setLoginEmail] = useState('');
    const [loginPassword, setLoginPassword] = useState('');
    const [isLoggingIn, setIsLoggingIn] = useState(false);

    // --- EFFECTS & LOGIC ---
    useEffect(() => {
        const savedModel = localStorage.getItem(STORAGE_KEYS.SELECTED_MODEL);
        const savedGeminiKey = localStorage.getItem(STORAGE_KEYS.GEMINI_KEY);
        const savedChatHistory = localStorage.getItem(STORAGE_KEYS.CHAT_HISTORY);

        if (savedModel) setSelectedModel(savedModel);
        if (savedGeminiKey) {
            setGeminiKeyInput(savedGeminiKey);
            setHasGeminiKey(true);
        }
        if (savedChatHistory) {
            try {
                const history = JSON.parse(savedChatHistory);
                setChatHistory(Array.isArray(history) ? history.slice(-30) : []);
            } catch (e) {
                localStorage.removeItem(STORAGE_KEYS.CHAT_HISTORY);
            }
        }
        checkAuthStatus();
    }, []);

    useEffect(() => {
        if (chatHistory.length > 0) {
            const limitedHistory = chatHistory.slice(-30);
            localStorage.setItem(STORAGE_KEYS.CHAT_HISTORY, JSON.stringify(limitedHistory));
        }
    }, [chatHistory]);

    // Force Theme Update
    useEffect(() => {
        const root = document.documentElement;
        if (theme === 'dark') {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }
        localStorage.setItem('theme', theme);
    }, [theme]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatHistory, isProcessing]);

    const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

    const checkAuthStatus = useCallback(async () => {
        try {
            const res = await axios.get(`${API_URL}/api/status`);
            setIsAuthenticated(res.data.authenticated);
            const savedGeminiKey = localStorage.getItem(STORAGE_KEYS.GEMINI_KEY);
            setHasGeminiKey(savedGeminiKey ? true : res.data.has_gemini_key);
            if (res.data.authenticated) {
                setUserEmail(res.data.email);
                localStorage.setItem(STORAGE_KEYS.USER_EMAIL, res.data.email);
                fetchEmails();
            }
        } catch (err) { console.error(err); }
    }, []);

    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLoggingIn(true);
        try {
            await axios.post(`${API_URL}/auth/login`, { email: loginEmail, password: loginPassword });
            setIsAuthenticated(true);
            setUserEmail(loginEmail);
            fetchEmails();
        } catch (err) { alert("Login failed! Check App Password."); }
        finally { setIsLoggingIn(false); }
    };

    const handleSaveKey = async () => {
        if (!geminiKeyInput.trim()) return;
        try {
            await axios.post(`${API_URL}/api/settings/gemini`, { key: geminiKeyInput });
            localStorage.setItem(STORAGE_KEYS.GEMINI_KEY, geminiKeyInput);
            setHasGeminiKey(true);
            setShowSettings(false);
            showToast('success', 'API Key saved successfully');
        } catch (err) { showToast('error', 'Failed to save key'); }
    };

    const fetchEmails = useCallback(async () => {
        setEmailsLoading(true);
        try {
            const res = await axios.get(`${API_URL}/api/emails`);
            setEmails(res.data.emails.slice(0, 20));
            showToast('success', 'Inbox refreshed');
        } catch (err) { showToast('error', 'Failed to fetch emails'); }
        finally { setEmailsLoading(false); }
    }, []);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!chatInput.trim()) return;
        const userMsg = chatInput.trim().substring(0, 500);
        setChatInput('');
        setChatHistory(prev => [...prev, { role: 'user', content: userMsg }]);
        setIsProcessing(true);

        try {
            const apiKey = geminiKeyInput || localStorage.getItem(STORAGE_KEYS.GEMINI_KEY);
            if (!apiKey) throw new Error("No API Key");

            const res = await axios.post(`${API_URL}/api/agent`, {
                command: userMsg,
                model: selectedModel,
                gemini_key: apiKey
            });

            if (res.data.type === 'error') throw new Error(res.data.message);

            setChatHistory(prev => [...prev, { role: 'assistant', content: res.data.message }]);
            if (userMsg.toLowerCase().includes('refresh')) fetchEmails();

        } catch (err) {
            setChatHistory(prev => [...prev, { role: 'assistant', content: '❌ Error: Check API Key or Backend.' }]);
        } finally { setIsProcessing(false); }
    };

    // Auto summarize logic
    useEffect(() => {
        if (selectedEmail) {
            setSummarizeEmail(selectedEmail);
            setSummarizeResult('');
            handleSummarizeEmail(selectedEmail);
        }
    }, [selectedEmail]);

    const handleSummarizeEmail = async (emailToSummarize) => {
        const apiKey = geminiKeyInput || localStorage.getItem(STORAGE_KEYS.GEMINI_KEY);
        if (!apiKey) return;

        setSummarizeLoading(true);
        try {
            const command = `Summarize this email in 3 short bullet points. Be direct:\nSubject: ${emailToSummarize.subject}\nBody: ${emailToSummarize.body_snippet}`;
            const res = await axios.post(`${API_URL}/api/agent`, { command, model: selectedModel, gemini_key: apiKey });
            if (res.data.type === 'error') throw new Error(res.data.message);
            setSummarizeResult(res.data.message);
        } catch (err) { setSummarizeError('Could not summarize.'); }
        finally { setSummarizeLoading(false); }
    };

    const showToast = (type, message) => {
        setShowNotification({ type, message });
        setTimeout(() => setShowNotification(null), 3000);
    };

    const formatSender = (sender) => {
        if (!sender) return { name: 'Unknown', letter: '?' };
        const nameMatch = sender.match(/^(.+?)\s*</);
        const name = nameMatch ? nameMatch[1].trim() : sender.replace(/<.*>/, '').trim();
        return { name, letter: name[0]?.toUpperCase() || '?' };
    };

    // --- RENDER ---

    if (!isAuthenticated) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center p-6">
                <div className="w-full max-w-md p-8 rounded-2xl bg-zinc-900 border border-zinc-800 text-center">
                    <Sparkles className="w-12 h-12 text-blue-500 mx-auto mb-4" />
                    <h1 className="text-2xl font-bold text-white mb-2">Gmail Agent Login</h1>
                    <p className="text-zinc-400 text-sm mb-6">Use your App Password to connect.</p>
                    <form onSubmit={handleLogin} className="space-y-4">
                        <input type="email" placeholder="Email" value={loginEmail} onChange={e => setLoginEmail(e.target.value)} required className="w-full bg-zinc-800 border-none rounded-lg px-4 py-3 text-white outline-none focus:ring-2 focus:ring-blue-600" />
                        <input type="password" placeholder="App Password" value={loginPassword} onChange={e => setLoginPassword(e.target.value)} required className="w-full bg-zinc-800 border-none rounded-lg px-4 py-3 text-white outline-none focus:ring-2 focus:ring-blue-600" />
                        <button type="submit" disabled={isLoggingIn} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition-all">
                            {isLoggingIn ? 'Connecting...' : 'Connect Agent'}
                        </button>
                    </form>
                </div>
            </div>
        );
    }

    return (
        <div className={`flex h-screen overflow-hidden font-sans ${theme === 'dark' ? 'bg-black text-zinc-100' : 'bg-slate-50 text-slate-900'}`}>

            {/* 1. SIDEBAR */}
            <aside className={`w-16 flex flex-col items-center py-6 gap-6 border-r ${theme === 'dark' ? 'border-zinc-800 bg-zinc-900/50' : 'border-slate-200 bg-white'}`}>
                <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/30">
                    <Zap size={20} />
                </div>
                <div className="flex-1 flex flex-col gap-4 mt-4">
                    <button onClick={fetchEmails} className={`p-3 rounded-xl transition-all ${!selectedEmail ? 'bg-zinc-800 text-white' : 'text-zinc-500 hover:bg-zinc-800 hover:text-white'}`}>
                        <Inbox size={22} />
                    </button>
                    <button onClick={() => showToast('info', 'AI Chat is always active on the right')} className="p-3 text-zinc-500 hover:text-white hover:bg-zinc-800 rounded-xl transition-all">
                        <Sparkles size={22} />
                    </button>
                </div>
                <div className="flex flex-col gap-4">
                    <button onClick={toggleTheme} className="p-3 text-zinc-500 hover:text-white hover:bg-zinc-800 rounded-xl">
                        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                    </button>
                    <button onClick={() => setShowSettings(true)} className="p-3 text-zinc-500 hover:text-white hover:bg-zinc-800 rounded-xl">
                        <Settings size={20} />
                    </button>
                </div>
            </aside>

            {/* 2. MAIN INBOX */}
            <main className="flex-1 flex flex-col h-full relative z-0">
                <header className={`h-16 flex items-center px-6 justify-between border-b ${theme === 'dark' ? 'border-zinc-800 bg-black' : 'border-slate-200 bg-white'}`}>
                    <h1 className="text-xl font-bold tracking-tight">Inbox</h1>
                    <div className="flex items-center gap-3">
                        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${theme === 'dark' ? 'bg-zinc-900' : 'bg-slate-100'}`}>
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                            <span className="text-xs font-medium opacity-70">Agent Active</span>
                        </div>
                    </div>
                </header>

                <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
                    {emails.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-64 text-zinc-500">
                            <RefreshCw className={`mb-2 ${emailsLoading ? 'animate-spin' : ''}`} />
                            <p>No new emails</p>
                        </div>
                    ) : (
                        <div className="grid gap-3">
                            {emails.map((email) => (
                                <motion.div
                                    key={email.id}
                                    whileHover={{ scale: 1.01 }}
                                    onClick={() => setSelectedEmail(email)}
                                    className={`p-4 rounded-xl cursor-pointer border transition-all flex items-center justify-between group ${theme === 'dark'
                                            ? 'bg-zinc-900 border-zinc-800 hover:border-zinc-600'
                                            : 'bg-white border-slate-200 hover:border-blue-300 shadow-sm'
                                        }`}
                                >
                                    <div className="flex-1 min-w-0 pr-4">
                                        <div className="flex items-baseline justify-between mb-1">
                                            <h3 className={`text-sm truncate ${email.is_unread ? 'font-bold text-white' : 'text-zinc-400'}`}>
                                                {formatSender(email.sender).name}
                                            </h3>
                                            <span className="text-xs text-zinc-500 font-mono">{email.date}</span>
                                        </div>
                                        <div className={`truncate text-sm mb-1 ${theme === 'dark' ? 'text-zinc-200' : 'text-slate-800'}`}>
                                            {email.subject || '(No Subject)'}
                                        </div>
                                        <div className="text-xs text-zinc-500 truncate">{email.body_snippet}</div>
                                    </div>
                                    <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                                        <ExternalLink size={16} className="text-blue-500" />
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    )}
                </div>
            </main>

            {/* 3. AI CHAT PANEL */}
            <aside className={`w-[450px] flex flex-col border-l shadow-2xl z-10 ${theme === 'dark' ? 'border-zinc-800 bg-zinc-900/80 backdrop-blur-md' : 'border-slate-200 bg-white'}`}>
                <div className={`p-4 border-b flex justify-between items-center ${theme === 'dark' ? 'border-zinc-800' : 'border-slate-200'}`}>
                    <div className="flex items-center gap-2">
                        <Sparkles size={18} className="text-blue-500" />
                        <span className="font-bold">Agent Chat</span>
                    </div>
                    <button onClick={() => setChatHistory([])} className="text-xs text-zinc-500 hover:text-red-400">Clear</button>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                    {chatHistory.length === 0 && (
                        <div className="text-center mt-20 opacity-40">
                            <p className="text-sm">I can read your emails and draft replies.</p>
                            <p className="text-xs mt-2">"Summarize the last email"</p>
                        </div>
                    )}
                    {chatHistory.map((msg, i) => (
                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[90%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                                    ? 'bg-blue-600 text-white'
                                    : theme === 'dark' ? 'bg-zinc-800 text-zinc-200' : 'bg-slate-100 text-slate-800'
                                }`}>
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                            </div>
                        </div>
                    ))}
                    {isProcessing && <div className="text-xs text-zinc-500 ml-4 animate-pulse">Agent is thinking...</div>}
                    <div ref={chatEndRef} />
                </div>

                <div className="p-4">
                    <form onSubmit={handleSendMessage} className={`flex items-center gap-2 p-2 rounded-xl border ${theme === 'dark' ? 'bg-black border-zinc-700' : 'bg-slate-50 border-slate-300'}`}>
                        <input
                            value={chatInput}
                            onChange={e => setChatInput(e.target.value)}
                            placeholder="Command the agent..."
                            className="flex-1 bg-transparent px-2 text-sm outline-none"
                            autoFocus
                        />
                        <button type="submit" disabled={isProcessing} className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500">
                            <SendIcon size={16} />
                        </button>
                    </form>
                </div>
            </aside>

            {/* 4. EMAIL POPUP MODAL */}
            <AnimatePresence>
                {selectedEmail && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" onClick={() => setSelectedEmail(null)}>
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            onClick={e => e.stopPropagation()}
                            className={`w-full max-w-3xl max-h-[90vh] flex flex-col rounded-2xl shadow-2xl overflow-hidden ${theme === 'dark' ? 'bg-zinc-900 border border-zinc-700' : 'bg-white'}`}
                        >
                            {/* Summary Header */}
                            <div className="bg-gradient-to-r from-blue-900/40 to-purple-900/40 border-b border-blue-500/20 p-4 shrink-0">
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2 text-blue-400 font-bold text-sm uppercase">
                                        <Sparkles size={14} /> AI Analysis
                                    </div>
                                    <button onClick={() => setSelectedEmail(null)} className="p-1 hover:bg-white/10 rounded-full"><X size={20} className="text-white/70" /></button>
                                </div>
                                {summarizeLoading ? (
                                    <div className="text-zinc-400 text-sm flex gap-2"><Loader2 size={16} className="animate-spin" /> Generating Insight...</div>
                                ) : (
                                    <div className="text-zinc-200 text-sm leading-relaxed font-medium">
                                        <ReactMarkdown>{summarizeResult || "No summary available."}</ReactMarkdown>
                                    </div>
                                )}
                            </div>

                            {/* Email Content */}
                            <div className="flex-1 overflow-y-auto p-8 custom-scrollbar bg-opacity-50">
                                <h1 className={`text-2xl font-bold mb-4 ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
                                    {selectedEmail.subject || '(No Subject)'}
                                </h1>
                                <div className="flex items-center gap-3 mb-8 pb-4 border-b border-zinc-700/50">
                                    <div className="w-10 h-10 rounded-full bg-orange-500 flex items-center justify-center text-white font-bold">
                                        {formatSender(selectedEmail.sender).letter}
                                    </div>
                                    <div>
                                        <div className={`font-semibold ${theme === 'dark' ? 'text-zinc-200' : 'text-slate-800'}`}>
                                            {formatSender(selectedEmail.sender).name}
                                        </div>
                                        <div className="text-xs text-zinc-500">{selectedEmail.date}</div>
                                    </div>
                                </div>

                                {/* Formatted Body - FIXED: Wrapped in Div, removed className from ReactMarkdown */}
                                <div className={`prose max-w-none ${theme === 'dark' ? 'prose-invert text-zinc-300' : 'text-slate-700'}`}>
                                    <div className="whitespace-pre-wrap leading-relaxed">
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                            {selectedEmail.body_snippet}
                                        </ReactMarkdown>
                                    </div>
                                    <br />
                                    <p className="opacity-40 italic mt-8 text-sm border-t border-zinc-700/50 pt-4">
                                        -- <br />End of fetched content. The agent has optimized this view for reading.
                                    </p>
                                </div>
                            </div>

                            {/* Modal Footer */}
                            <div className={`p-4 border-t flex justify-end gap-3 ${theme === 'dark' ? 'bg-zinc-950 border-zinc-800' : 'bg-slate-50 border-slate-200'}`}>
                                <button onClick={() => setSelectedEmail(null)} className="px-4 py-2 rounded-lg text-sm hover:bg-white/5">Close</button>
                                <button onClick={() => {
                                    setChatInput(`Draft a reply to "${selectedEmail.subject}": `);
                                    setSelectedEmail(null);
                                }} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-500">Reply with Agent</button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* NOTIFICATION TOAST */}
            <AnimatePresence>
                {showNotification && (
                    <motion.div initial={{ y: 50, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 20, opacity: 0 }} className="fixed bottom-6 left-6 z-50 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg shadow-lg">
                        {showNotification.message}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* SETTINGS MODAL */}
            {showSettings && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80" onClick={() => setShowSettings(false)}>
                    <div className="w-96 bg-zinc-900 border border-zinc-800 p-6 rounded-2xl" onClick={e => e.stopPropagation()}>
                        <h2 className="text-white text-lg font-bold mb-4">Settings</h2>

                        <div className="mb-4">
                            <label className="block text-zinc-400 text-xs font-bold uppercase mb-2">
                                Gemini API Key
                            </label>
                            <input
                                type="password"
                                value={geminiKeyInput}
                                onChange={e => setGeminiKeyInput(e.target.value)}
                                placeholder="Paste your AI Studio Key here..."
                                className="w-full bg-zinc-800 text-white p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-600 border border-transparent focus:border-blue-600 transition-all"
                            />
                            <p className="text-[10px] text-zinc-500 mt-2">
                                Required for Chat and Auto-Summary features.
                            </p>
                        </div>

                        <button onClick={handleSaveKey} className="w-full bg-blue-600 text-white py-2.5 rounded-xl mb-3 font-medium hover:bg-blue-500 transition-colors">
                            Save Configuration
                        </button>
                        <button onClick={async () => { await axios.post(`${API_URL}/auth/logout`); window.location.reload(); }} className="w-full text-red-400 py-2 hover:bg-red-900/20 rounded-xl transition-colors text-sm">
                            Log Out
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;