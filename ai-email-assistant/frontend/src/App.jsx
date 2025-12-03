import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
    Send, Mail, Settings, LogOut, Bot, Loader2, X, RefreshCw, User
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_URL = 'http://localhost:8000';

function App() {
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
    const [selectedModel, setSelectedModel] = useState('gemini-2.0-flash-exp');
    const chatEndRef = useRef(null);

    // Login State
    const [loginEmail, setLoginEmail] = useState('');
    const [loginPassword, setLoginPassword] = useState('');
    const [isLoggingIn, setIsLoggingIn] = useState(false);

    useEffect(() => {
        checkAuthStatus();
    }, []);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatHistory]);

    const checkAuthStatus = async () => {
        try {
            const res = await axios.get(`${API_URL}/api/status`);
            setIsAuthenticated(res.data.authenticated);
            setHasGeminiKey(res.data.has_gemini_key);
            if (res.data.authenticated) {
                setUserEmail(res.data.email);
                fetchEmails();
            }
        } catch (err) {
            console.error("Auth check failed", err);
        }
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLoggingIn(true);
        try {
            await axios.post(`${API_URL}/auth/login`, {
                email: loginEmail,
                password: loginPassword
            });
            setIsAuthenticated(true);
            setUserEmail(loginEmail);
            fetchEmails();
        } catch (err) {
            alert("Login failed! Check your App Password.");
        } finally {
            setIsLoggingIn(false);
        }
    };

    const handleSaveKey = async () => {
        if (!geminiKeyInput.trim()) {
            alert("Please enter an API key");
            return;
        }
        try {
            await axios.post(`${API_URL}/api/settings/gemini`, { key: geminiKeyInput });
            setHasGeminiKey(true);
            setShowSettings(false);
            addChatMessage('assistant', `✅ Settings saved! Using ${selectedModel}`);
        } catch (err) {
            alert("Failed to save key");
        }
    };

    const fetchEmails = async () => {
        try {
            const res = await axios.get(`${API_URL}/api/emails`);
            setEmails(res.data.emails);
        } catch (err) {
            console.error("Failed to fetch emails", err);
        }
    };

    const addChatMessage = (role, content) => {
        setChatHistory(prev => [...prev, { role, content }]);
    };

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!chatInput.trim()) return;

        const userMsg = chatInput;
        setChatInput('');
        addChatMessage('user', userMsg);
        setIsProcessing(true);

        try {
            const res = await axios.post(`${API_URL}/api/agent`, {
                command: userMsg,
                model: selectedModel
            });

            if (res.data.type === 'error') {
                addChatMessage('assistant', `❌ ${res.data.message}`);
            } else {
                addChatMessage('assistant', res.data.message);
                if (userMsg.toLowerCase().includes('check') || userMsg.toLowerCase().includes('refresh')) {
                    fetchEmails();
                }
            }
        } catch (err) {
            addChatMessage('assistant', '❌ Error. Check your API Key.');
        } finally {
            setIsProcessing(false);
        }
    };

    const formatEmailSender = (sender) => {
        if (!sender) return 'Unknown';
        const nameMatch = sender.match(/^(.+?)\s*</);
        if (nameMatch) return nameMatch[1].trim();
        const emailMatch = sender.match(/<(.+?)>/);
        if (emailMatch) return emailMatch[1];
        return sender;
    };

    if (!isAuthenticated) {
        return (
            <div className="min-h-screen bg-white flex items-center justify-center p-4">
                <div className="bg-white border-2 border-blue-200 rounded-3xl shadow-xl p-10 w-full max-w-md">
                    <div className="text-center mb-8">
                        <div className="w-20 h-20 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                            <Mail size={40} className="text-white" />
                        </div>
                        <h1 className="text-4xl font-bold text-gray-900 mb-3">AI Email Agent</h1>
                        <p className="text-gray-600 text-lg">Sign in to continue</p>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-5">
                        <div>
                            <label className="block text-base font-semibold text-gray-800 mb-2">Email</label>
                            <input
                                type="email"
                                required
                                value={loginEmail}
                                onChange={(e) => setLoginEmail(e.target.value)}
                                className="w-full px-5 py-4 text-base border-2 border-gray-300 rounded-xl focus:outline-none focus:border-blue-600 text-gray-900"
                                placeholder="your@gmail.com"
                            />
                        </div>
                        <div>
                            <label className="block text-base font-semibold text-gray-800 mb-2">App Password</label>
                            <input
                                type="password"
                                required
                                value={loginPassword}
                                onChange={(e) => setLoginPassword(e.target.value)}
                                className="w-full px-5 py-4 text-base border-2 border-gray-300 rounded-xl focus:outline-none focus:border-blue-600 text-gray-900"
                                placeholder="16 characters"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={isLoggingIn}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white text-lg font-bold py-4 rounded-xl transition-all shadow-lg"
                        >
                            {isLoggingIn ? <Loader2 size={24} className="animate-spin mx-auto" /> : 'Sign In'}
                        </button>
                    </form>
                </div>
            </div>
        );
    }

    return (
        <div className="h-screen bg-white flex flex-col">
            {/* Top Header */}
            <div className="bg-blue-600 text-white px-6 py-4 shadow-lg">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center">
                            <Mail size={28} className="text-blue-600" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold">AI Email Agent</h1>
                            <p className="text-sm text-blue-100">{userEmail}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        {!hasGeminiKey && (
                            <button
                                onClick={() => setShowSettings(true)}
                                className="bg-yellow-400 text-gray-900 px-4 py-2 rounded-lg font-bold text-sm"
                            >
                                ⚠️ Set API Key
                            </button>
                        )}
                        <button
                            onClick={fetchEmails}
                            className="bg-blue-700 hover:bg-blue-800 p-3 rounded-lg transition-colors"
                            title="Refresh"
                        >
                            <RefreshCw size={20} />
                        </button>
                        <button
                            onClick={() => setShowSettings(true)}
                            className="bg-blue-700 hover:bg-blue-800 p-3 rounded-lg transition-colors"
                            title="Settings"
                        >
                            <Settings size={20} />
                        </button>
                        <button
                            onClick={async () => { await axios.post(`${API_URL}/auth/logout`); window.location.reload(); }}
                            className="bg-red-600 hover:bg-red-700 p-3 rounded-lg transition-colors"
                            title="Logout"
                        >
                            <LogOut size={20} />
                        </button>
                    </div>
                </div>
            </div>

            {/* Chat Section - TOP HALF */}
            <div className="h-1/2 border-b-4 border-blue-600 flex flex-col bg-gray-50">
                <div className="bg-white border-b-2 border-blue-200 px-6 py-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                            <Bot size={24} className="text-white" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-gray-900">AI Assistant</h2>
                            <p className="text-sm text-gray-600">{selectedModel}</p>
                        </div>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-6">
                    {chatHistory.length === 0 ? (
                        <div className="h-full flex items-center justify-center">
                            <div className="text-center">
                                <div className="w-20 h-20 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                    <Bot size={40} className="text-blue-600" />
                                </div>
                                <h3 className="text-2xl font-bold text-gray-900 mb-2">Ask me anything!</h3>
                                <p className="text-gray-600 text-lg">I can help you manage your emails</p>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-4 max-w-4xl mx-auto">
                            {chatHistory.map((msg, idx) => (
                                <div
                                    key={idx}
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div className={`max-w-[75%] rounded-2xl px-5 py-4 ${msg.role === 'user'
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-white border-2 border-blue-200 text-gray-900'
                                        }`}>
                                        {msg.role === 'assistant' ? (
                                            <div className="prose prose-lg max-w-none text-gray-900">
                                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                    {msg.content}
                                                </ReactMarkdown>
                                            </div>
                                        ) : (
                                            <p className="text-base font-medium">{msg.content}</p>
                                        )}
                                    </div>
                                </div>
                            ))}
                            {isProcessing && (
                                <div className="flex justify-start">
                                    <div className="bg-white border-2 border-blue-200 rounded-2xl px-5 py-4">
                                        <div className="flex gap-2">
                                            <span className="w-3 h-3 bg-blue-600 rounded-full animate-bounce"></span>
                                            <span className="w-3 h-3 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                                            <span className="w-3 h-3 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={chatEndRef} />
                        </div>
                    )}
                </div>

                <div className="p-6 bg-white border-t-2 border-blue-200">
                    <form onSubmit={handleSendMessage} className="flex gap-3 max-w-4xl mx-auto">
                        <input
                            type="text"
                            value={chatInput}
                            onChange={(e) => setChatInput(e.target.value)}
                            placeholder="Type your message here..."
                            className="flex-1 px-5 py-4 text-base border-2 border-gray-300 rounded-xl focus:outline-none focus:border-blue-600 text-gray-900 font-medium"
                            disabled={isProcessing}
                        />
                        <button
                            type="submit"
                            disabled={!chatInput.trim() || isProcessing}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-bold text-base transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                        >
                            <Send size={20} />
                        </button>
                    </form>
                </div>
            </div>

            {/* Inbox Section - BOTTOM HALF */}
            <div className="h-1/2 flex flex-col bg-white">
                <div className="bg-blue-600 text-white px-6 py-4">
                    <h2 className="text-2xl font-bold">📧 Inbox ({emails.length})</h2>
                </div>

                <div className="flex-1 overflow-y-auto p-4">
                    {emails.length === 0 ? (
                        <div className="h-full flex items-center justify-center">
                            <p className="text-gray-500 text-xl">No emails found</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-7xl mx-auto">
                            {emails.map((email) => (
                                <div
                                    key={email.id}
                                    className="bg-white border-2 border-blue-200 rounded-xl p-5 hover:border-blue-600 hover:shadow-lg transition-all cursor-pointer"
                                >
                                    <div className="flex items-start gap-3 mb-3">
                                        <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
                                            {formatEmailSender(email.sender)[0]?.toUpperCase()}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="font-bold text-gray-900 text-base truncate">
                                                {formatEmailSender(email.sender)}
                                            </p>
                                            <p className="text-sm text-gray-600">Just now</p>
                                        </div>
                                    </div>
                                    <h3 className="font-bold text-gray-900 text-base mb-2 line-clamp-1">
                                        {email.subject || '(No Subject)'}
                                    </h3>
                                    <p className="text-gray-700 text-sm line-clamp-3 leading-relaxed">
                                        {email.body_snippet || 'No preview available'}
                                    </p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Settings Modal */}
            <AnimatePresence>
                {showSettings && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
                        onClick={() => setShowSettings(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0.9 }}
                            className="bg-white rounded-2xl w-full max-w-md p-8 shadow-2xl"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-2xl font-bold text-gray-900">⚙️ Settings</h3>
                                <button
                                    onClick={() => setShowSettings(false)}
                                    className="text-gray-500 hover:text-gray-900"
                                >
                                    <X size={28} />
                                </button>
                            </div>

                            <div className="space-y-5">
                                <div>
                                    <label className="block text-base font-bold text-gray-900 mb-2">
                                        Gemini API Key
                                    </label>
                                    <input
                                        type="text"
                                        value={geminiKeyInput}
                                        onChange={(e) => setGeminiKeyInput(e.target.value)}
                                        className="w-full px-4 py-3 text-base border-2 border-gray-300 rounded-xl focus:outline-none focus:border-blue-600 text-gray-900"
                                        placeholder="Enter your API key..."
                                    />
                                    <p className="mt-2 text-sm text-gray-600">
                                        Get from <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-blue-600 font-bold hover:underline">Google AI Studio</a>
                                    </p>
                                </div>

                                <div>
                                    <label className="block text-base font-bold text-gray-900 mb-2">
                                        AI Model
                                    </label>
                                    <select
                                        value={selectedModel}
                                        onChange={(e) => setSelectedModel(e.target.value)}
                                        className="w-full px-4 py-3 text-base border-2 border-gray-300 rounded-xl focus:outline-none focus:border-blue-600 text-gray-900 font-medium cursor-pointer"
                                    >
                                        <option value="gemini-2.0-flash-exp">Gemini 2.0 Flash (Recommended)</option>
                                        <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                                        <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                                        <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                                    </select>
                                </div>

                                <button
                                    onClick={handleSaveKey}
                                    className="w-full bg-blue-600 hover:bg-blue-700 text-white text-lg font-bold py-4 rounded-xl transition-all shadow-lg"
                                >
                                    Save Settings
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

export default App;
