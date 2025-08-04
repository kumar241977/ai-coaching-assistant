class CoachingAssistant {
    constructor() {
        this.sessionId = null;
        this.userId = null;
        this.currentStage = 'intake';
        this.isLoading = false;
        this.loadingTimeout = null;
        this.messageQueue = []; // Prevent duplicate messages
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.showWelcomeScreen();
    }
    
    bindEvents() {
        // Topic selection
        document.querySelectorAll('.topic-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (this.isLoading) return; // Prevent clicks during loading
                const topic = e.currentTarget.dataset.topic;
                // Clear any existing messages before starting new topic
                document.getElementById('chat-messages').innerHTML = '';
                this.selectTopic(topic);
            });
        });
        
        // New session button
        document.getElementById('new-session-btn').addEventListener('click', () => {
            if (this.isLoading) return; // Prevent clicks during loading
            // Clear chat and reset to welcome screen
            document.getElementById('chat-messages').innerHTML = '';
            this.showWelcomeScreen();
            this.sessionId = null;
            this.currentStage = 'intake';
            this.updateSessionStatus('Ready to start');
        });
        
        // Send message
        document.getElementById('send-btn').addEventListener('click', () => {
            if (!this.isLoading) { // Only send if not loading
                this.sendMessage();
            }
        });
        
        // Enter key to send message
        document.getElementById('user-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey && !this.isLoading) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
    
    showLoading(show) {
        console.log(`🔍 DEBUG: showLoading called with: ${show}`);
        this.isLoading = show;
        
        // Clear any existing timeout
        if (this.loadingTimeout) {
            clearTimeout(this.loadingTimeout);
            this.loadingTimeout = null;
        }
        
        const loadingDiv = document.getElementById('loading-indicator');
        const sendBtn = document.getElementById('send-btn');
        const userInput = document.getElementById('user-input');
        
        if (show) {
            if (loadingDiv) loadingDiv.style.display = 'block';
            if (sendBtn) {
                sendBtn.disabled = true;
                sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Thinking...';
            }
            if (userInput) userInput.disabled = true;
            
            // Auto-reset loading after 30 seconds to prevent permanent hang
            this.loadingTimeout = setTimeout(() => {
                console.log('⚠️ DEBUG: Auto-resetting loading state after timeout');
                this.showLoading(false);
            }, 30000);
        } else {
            if (loadingDiv) loadingDiv.style.display = 'none';
            if (sendBtn) {
                sendBtn.disabled = false;
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
            }
            if (userInput) userInput.disabled = false;
        }
        
        console.log(`🔍 DEBUG: Send button disabled: ${sendBtn?.disabled}`);
        console.log(`🔍 DEBUG: Loading state set to: ${show} isLoading: ${this.isLoading}`);
    }
    
    async sendMessage() {
        const input = document.getElementById('user-input');
        const message = input.value.trim();
        
        if (!message || this.isLoading) {
            console.log(`🔍 DEBUG: Message blocked - empty: ${!message}, loading: ${this.isLoading}`);
            return;
        }
        
        console.log('🔍 DEBUG: Sending message:', message);
        console.log('🔍 DEBUG: Session ID:', this.sessionId);
        
        // Prevent duplicate messages
        const messageKey = `${this.sessionId}-${message}`;
        if (this.messageQueue.includes(messageKey)) {
            console.log('🔍 DEBUG: Duplicate message blocked');
            return;
        }
        this.messageQueue.push(messageKey);
        
        // Clear input immediately and show user message
        input.value = '';
        this.addMessage('user', message);
        
        this.showLoading(true);
        
        try {
            console.log('🔍 DEBUG: Making API request to /api/send-message');
            const response = await fetch('/api/send-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: message,
                    type: 'text'
                })
            });
            
            console.log('🔍 DEBUG: Response status:', response.status);
            console.log('🔍 DEBUG: Response ok:', response.ok);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('🔍 DEBUG: Response data:', data);
            
            if (data.message) {
                this.addMessage('coach', data.message, data.questions);
                this.updateStageIndicator(data.stage);
                this.currentStage = data.stage;
                
                if (data.emotional_analysis) {
                    try {
                        this.showEmotionalAnalysis(data.emotional_analysis);
                    } catch (error) {
                        console.log('🔍 DEBUG: Skipping emotional analysis display due to missing HTML elements');
                    }
                }
                
                if (data.stage === 'action_planning' && data.action_template) {
                    this.showActionPlanningOption();
                }
                
                if (data.insights && data.insights.length > 0) {
                    this.showInsights(data.insights);
                }
            } else {
                console.warn('🔍 DEBUG: No message in response data');
            }
        } catch (error) {
            console.error('❌ DEBUG: Error sending message:', error);
            console.error('❌ DEBUG: Error details:', {
                name: error.name,
                message: error.message,
                stack: error.stack
            });
            this.showError('Failed to send message. Please try again.');
        } finally {
            // Remove from queue and reset loading
            const messageKey = `${this.sessionId}-${message}`;
            this.messageQueue = this.messageQueue.filter(key => key !== messageKey);
            this.showLoading(false);
        }
    }
    
    addMessage(role, content, questions = null, insights = null) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'coach' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = content;
        messageContent.appendChild(messageText);
        
        if (questions && questions.length > 0) {
            // Filter out generic/confusing questions
            const validQuestions = questions.filter(q => 
                q && 
                q.length > 10 && 
                !q.includes("Thank you for sharing that with me") &&
                !q.includes("Can you tell me more about that?") &&
                !q.includes("What else is important here?") &&
                !q.includes("Tell me more about that") &&
                !q.includes("What's most important here?") &&
                !q.toLowerCase().includes("that's a really insightful perspective") &&
                !q.includes("I'm here to support you through this")
            );
            
            if (validQuestions.length > 0) {
                const questionsDiv = document.createElement('div');
                questionsDiv.className = 'message-questions';
                
                const questionsTitle = document.createElement('h4');
                questionsTitle.textContent = 'Reflection Questions:';
                questionsDiv.appendChild(questionsTitle);
                
                const questionsList = document.createElement('ul');
                validQuestions.forEach(question => {
                    const li = document.createElement('li');
                    li.textContent = question;
                    questionsList.appendChild(li);
                });
                questionsDiv.appendChild(questionsList);
                messageContent.appendChild(questionsDiv);
            }
        }
        
        if (insights && insights.length > 0) {
            const insightsDiv = document.createElement('div');
            insightsDiv.className = 'message-insights';
            
            const insightsTitle = document.createElement('h4');
            insightsTitle.textContent = 'Key Insights:';
            insightsDiv.appendChild(insightsTitle);
            
            const insightsList = document.createElement('ul');
            insights.forEach(insight => {
                const li = document.createElement('li');
                li.textContent = insight;
                insightsList.appendChild(li);
            });
            insightsDiv.appendChild(insightsList);
            messageContent.appendChild(insightsList);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        messagesContainer.appendChild(messageDiv);
        
        // Enhanced scroll behavior with delay
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            console.log('🔍 DEBUG: Scrolled to bottom');
        }, 100);
    }
    
    showError(message) {
        // Show error without affecting loading state
        this.addMessage('coach', `⚠️ ${message}`);
        console.log('UI state reset after error:', message);
    }
    
    // ... rest of the methods remain the same as original app.js
    showWelcomeScreen() {
        document.getElementById('welcome-screen').style.display = 'flex';
        document.getElementById('chat-interface').style.display = 'none';
        this.updateSessionStatus('Ready to start');
    }
    
    showChatInterface() {
        document.getElementById('welcome-screen').style.display = 'none';
        document.getElementById('chat-interface').style.display = 'flex';
        this.updateSessionStatus('Session Active');
    }
    
    async startNewSession() {
        if (this.isLoading) return;
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/start-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId || null
                })
            });
            
            const data = await response.json();
            
            if (data.session_id) {
                this.sessionId = data.session_id;
                this.userId = data.user_id;
                
                this.showChatInterface();
                
                if (data.response && data.response.message) {
                    this.addMessage('coach', data.response.message, data.response.questions);
                    this.updateStageIndicator(data.response.stage);
                    this.currentStage = data.response.stage;
                }
            }
        } catch (error) {
            console.error('Error starting session:', error);
            this.showError('Failed to start session. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }
    
    async selectTopic(topicKey) {
        if (this.isLoading) return;
        
        if (!this.sessionId) {
            await this.startNewSession();
        }
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/send-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: topicKey,
                    type: 'topic_selection'
                })
            });
            
            const data = await response.json();
            
            if (data.message) {
                this.showChatInterface();
                // Clear any existing messages first
                document.getElementById('chat-messages').innerHTML = '';
                
                // Add a single welcome message
                this.addMessage('coach', data.message, data.questions);
                this.updateStageIndicator(data.stage);
                this.currentStage = data.stage;
                
                if (data.emotional_analysis) {
                    try {
                        this.showEmotionalAnalysis(data.emotional_analysis);
                    } catch (error) {
                        console.log('🔍 DEBUG: Skipping emotional analysis display due to missing HTML elements');
                    }
                }
            }
        } catch (error) {
            console.error('Error selecting topic:', error);
            this.showError('Failed to process topic selection.');
        } finally {
            this.showLoading(false);
        }
    }
    
    updateStageIndicator(stage) {
        document.querySelectorAll('.stage').forEach(stageDiv => {
            stageDiv.classList.remove('active', 'completed');
            
            const stageKey = stageDiv.dataset.stage;
            if (stageKey === stage) {
                stageDiv.classList.add('active');
            } else if (this.isStageCompleted(stageKey, stage)) {
                stageDiv.classList.add('completed');
            }
        });
    }
    
    isStageCompleted(stageKey, currentStage) {
        const stageOrder = ['intake', 'exploration', 'reflection', 'action_planning', 'follow_up'];
        const currentIndex = stageOrder.indexOf(currentStage);
        const stageIndex = stageOrder.indexOf(stageKey);
        return stageIndex < currentIndex;
    }
    
    updateSessionStatus(status) {
        document.getElementById('session-status').textContent = status;
    }
    
    showEmotionalAnalysis(analysis) {
        const analysisDiv = document.getElementById('emotional-analysis');
        const sentimentSpan = document.getElementById('sentiment-indicator');
        const emotionSpan = document.getElementById('primary-emotion');
        
        // Skip if elements don't exist in HTML
        if (!analysisDiv || !sentimentSpan || !emotionSpan) {
            console.log('🔍 DEBUG: Emotional analysis elements not found in HTML, skipping display');
            return;
        }
        
        if (analysis) {
            sentimentSpan.textContent = analysis.sentiment || 'neutral';
            emotionSpan.textContent = analysis.primary_emotion || 'engaged';
            analysisDiv.style.display = 'block';
        }
    }
}

// Initialize the coaching assistant when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Enhanced Coaching Assistant...');
    window.coachingAssistant = new CoachingAssistant();
}); 
