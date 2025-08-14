class CoachingAssistant {
    constructor() {
        this.sessionId = null;
        this.userId = null;
        this.currentStage = 'intake';
        this.isLoading = false;
        this.loadingTimeout = null; // Add timeout tracking
        
        this.init();
    }
    
    init() {
        console.log('🚀 DEBUG: CoachingAssistant initializing...');
        this.bindEvents();
        this.showWelcomeScreen();
        // Load sessions list on landing
        const storedUserId = window.localStorage.getItem('coaching_user_id');
        this.userId = storedUserId || this.generateUserId();
        if (!storedUserId) {
            try { window.localStorage.setItem('coaching_user_id', this.userId); } catch (_) {}
        }
        this.fetchAndRenderSessions();
        console.log('✅ DEBUG: CoachingAssistant initialized');
    }
    
    bindEvents() {
        // Topic selection
        document.querySelectorAll('.topic-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (this.isLoading) return; // Prevent clicks during loading
                const topic = e.currentTarget.dataset.topic;
                console.log('🎯 DEBUG: Topic card clicked:', topic);
                console.log('🎯 DEBUG: Event target:', e.currentTarget);
                
                // Clear any existing messages before starting new topic
                document.getElementById('chat-messages').innerHTML = '';
                
                console.log('🚀 DEBUG: Calling selectTopic...');
                this.selectTopic(topic);
            });
        });
        
        // New session button (header)
        document.getElementById('new-session-btn').addEventListener('click', () => {
            // Clear chat and reset to welcome screen
            document.getElementById('chat-messages').innerHTML = '';
            this.showWelcomeScreen();
            this.sessionId = null;
            this.currentStage = 'intake';
            this.updateSessionStatus('Ready to start');
        });

        // Pause current session
        const pauseBtn = document.getElementById('pause-session-btn');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', async () => {
                if (!this.sessionId) {
                    alert('No active session to pause.');
                    return;
                }
                try {
                    await fetch('/api/pause-session', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ session_id: this.sessionId })
                    });
                    this.updateSessionStatus('Paused');
                    await this.fetchAndRenderSessions();
                    this.showWelcomeScreen();
                } catch (e) {
                    console.error('❌ DEBUG: Failed to pause session', e);
                    alert('Failed to pause session');
                }
            });
        }

        // Start New Session (landing sessions panel)
        const startNewLanding = document.getElementById('start-new-session-btn');
        if (startNewLanding) {
            startNewLanding.addEventListener('click', async () => {
                await this.startNewSession();
                this.showChatInterface();
            });
        }

        // Refresh sessions list
        const refreshBtn = document.getElementById('refresh-sessions-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.fetchAndRenderSessions());
        }
        
        // Send message
        document.getElementById('send-btn').addEventListener('click', () => {
            if (!this.isLoading) { // Only send if not loading
                this.sendMessage();
            }
        });
        
        // Enter key to send message
        document.getElementById('user-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey && !this.isLoading) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Action form
        document.getElementById('action-commitment-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitActionCommitment();
        });
        
        // Back to chat button
        document.getElementById('back-to-chat').addEventListener('click', () => {
            this.showChatInterface();
        });
    }

    // ---------- Sessions List UI ----------
    async fetchAndRenderSessions() {
        try {
            const url = `/api/sessions?user_id=${encodeURIComponent(this.userId)}`;
            const res = await fetch(url);
            const data = await res.json();
            const sessions = Array.isArray(data.sessions) ? data.sessions : [];
            this.renderSessionsList(sessions);
        } catch (e) {
            console.error('❌ DEBUG: Failed to fetch sessions', e);
        }
    }

    renderSessionsList(sessions) {
        const list = document.getElementById('sessions-list');
        if (!list) return;
        list.innerHTML = '';

        if (!sessions.length) {
            const empty = document.createElement('div');
            empty.className = 'empty-state';
            empty.innerHTML = '<i class="fas fa-comments"></i><p>No prior sessions yet. Start a new session to begin.</p>';
            list.appendChild(empty);
            return;
        }

        sessions.forEach(s => {
            const item = document.createElement('div');
            item.className = 'session-item';

            const meta = document.createElement('div');
            meta.className = 'session-meta';
            const topic = document.createElement('div');
            topic.className = 'session-topic';
            topic.textContent = (s.topic || 'No topic yet').replaceAll('_', ' ');
            const dates = document.createElement('div');
            dates.className = 'session-dates';
            dates.textContent = `Updated: ${new Date(s.updated_at).toLocaleString()} • Created: ${new Date(s.created_at).toLocaleString()}`;
            meta.appendChild(topic);
            meta.appendChild(dates);

            const status = document.createElement('span');
            status.className = `badge ${s.status || 'active'}`;
            status.textContent = s.status || 'active';

            const actions = document.createElement('div');

            const resumeBtn = document.createElement('button');
            resumeBtn.className = 'btn btn-secondary';
            const isPaused = (s.status || '').toLowerCase() === 'paused';
            resumeBtn.innerHTML = '<i class="fas fa-play"></i> ' + (isPaused ? 'Resume' : 'Open');
            resumeBtn.onclick = () => this.resumeSessionAndOpen(s.session_id);

            actions.appendChild(resumeBtn);

            item.appendChild(meta);
            item.appendChild(status);
            item.appendChild(actions);
            list.appendChild(item);
        });
    }

    async resumeSessionAndOpen(sessionId) {
        try {
            // Mark session active
            await fetch('/api/resume-session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });

            // Load session details including history
            const res = await fetch(`/api/session/${encodeURIComponent(sessionId)}`);
            const session = await res.json();
            if (session && session.session_id) {
                this.sessionId = session.session_id;
                this.userId = session.user_id || this.userId || this.generateUserId();
                try { window.localStorage.setItem('coaching_user_id', this.userId); } catch (_) {}
                this.currentStage = session.stage || 'exploration';
                this.updateSessionStatus('Session Active');

                // Render chat interface and history
                this.showChatInterface();
                const container = document.getElementById('chat-messages');
                container.innerHTML = '';
                const history = Array.isArray(session.conversation_history) ? session.conversation_history : [];
                history.forEach(entry => {
                    const role = entry.role === 'coach' ? 'coach' : 'user';
                    this.addMessage(role, entry.content);
                });

                this.updateStageIndicator(this.currentStage);
                await this.fetchAndRenderSessions();
            }
        } catch (e) {
            console.error('❌ DEBUG: Failed to resume session', e);
            alert('Failed to resume session.');
        }
    }
    
    async startNewSession() {
        console.log('🔄 DEBUG: Starting new session...');
        this.showLoading(true);
        
        try {
            console.log('🌐 DEBUG: Making API call to /api/start-session');
            const response = await fetch('/api/start-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId || this.generateUserId()
                })
            });
            
            console.log('📡 DEBUG: Start session response status:', response.status);
            console.log('📡 DEBUG: Start session response ok:', response.ok);
            
            let data;
            try {
                data = await response.json();
                console.log('📝 DEBUG: Start session response data:', data);
            } catch (jsonError) {
                console.error('❌ DEBUG: Failed to parse JSON response:', jsonError);
                throw new Error(`Server error (${response.status}): Failed to parse response`);
            }
            
            if (!response.ok) {
                // Server returned an error, but we got JSON data
                const errorMsg = data.error || `HTTP error! status: ${response.status}`;
                console.error('❌ DEBUG: Server returned error:', errorMsg);
                throw new Error(errorMsg);
            }
            
            if (data.session_id) {
                this.sessionId = data.session_id;
                this.userId = data.user_id;
                try { window.localStorage.setItem('coaching_user_id', this.userId); } catch (_) {}
                this.currentStage = 'intake';
                
                console.log('✅ DEBUG: Session started successfully:', this.sessionId);
                this.updateSessionStatus('Session Active');
                // Don't show chat interface or add messages here
                // Let topic selection handle the first message
            } else {
                console.error('❌ DEBUG: No session_id in response');
                throw new Error('Invalid response from server');
            }
        } catch (error) {
            console.error('❌ DEBUG: Error starting session:', error);
            this.showError('Failed to start session. Please try again.');
        } finally {
            this.showLoading(false);
            // Refresh sessions panel
            this.fetchAndRenderSessions();
        }
    }
    
    async selectTopic(topicKey) {
        console.log('🎯 DEBUG: Topic selected:', topicKey);
        
        if (!this.sessionId) {
            console.log('🔍 DEBUG: No session ID, starting new session...');
            await this.startNewSession();
            console.log('🔍 DEBUG: New session started with ID:', this.sessionId);
        }
        
        this.showLoading(true);
        
        try {
            console.log('🌐 DEBUG: Making API call to /api/send-message');
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
            
            console.log('📡 DEBUG: Response status:', response.status);
            console.log('📡 DEBUG: Response ok:', response.ok);
            
            let data;
            try {
                data = await response.json();
                console.log('📝 DEBUG: Response data:', data);
            } catch (jsonError) {
                console.error('❌ DEBUG: Failed to parse JSON response:', jsonError);
                throw new Error(`Server error (${response.status}): Failed to parse response`);
            }
            
            if (!response.ok) {
                const errorMsg = data.error || `HTTP error! status: ${response.status}`;
                console.error('❌ DEBUG: Server returned error:', errorMsg);
                throw new Error(errorMsg);
            }
            
            if (data.message) {
                console.log('✅ DEBUG: Got message, showing chat interface...');
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
                console.log('🎉 DEBUG: Topic selection completed successfully');
            } else {
                console.error('❌ DEBUG: No message in response data');
                this.showError('Invalid response from server.');
            }
        } catch (error) {
            console.error('❌ DEBUG: Error selecting topic:', error);
            this.showError('Failed to process topic selection. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }
    
    async sendMessage() {
        const input = document.getElementById('user-input');
        const message = input.value.trim();
        
        if (!message || this.isLoading) return;
        
        console.log('🔍 DEBUG: Sending message:', message);
        console.log('🔍 DEBUG: Session ID:', this.sessionId);
        
        // Add user message to chat
        this.addMessage('user', message);
        input.value = '';
        
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
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (data.message) {
                this.addMessage('coach', data.message, data.questions);
                
                if (data.personalized_message) {
                    this.addMessage('coach', data.personalized_message);
                }
                
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
            this.showLoading(false);
            
            // Double-check that input is enabled (safety fallback)
            setTimeout(() => {
                const inputEl = document.getElementById('user-input');
                const sendBtn = document.getElementById('send-btn');
                
                if (inputEl) {
                    inputEl.disabled = false;
                    inputEl.removeAttribute('disabled');
                    inputEl.style.pointerEvents = 'auto';
                    inputEl.style.opacity = '1';
                    console.log('🔒 DEBUG: Safety check - input field re-enabled');
                }
                
                if (sendBtn) {
                    sendBtn.disabled = false;
                    console.log('🔒 DEBUG: Safety check - send button re-enabled');
                }
                
                this.isLoading = false;
            }, 500);
        }
    }
    
    async submitActionCommitment() {
        const formData = {
            action: document.getElementById('action-input').value,
            by_when: document.getElementById('deadline-input').value,
            success_criteria: document.getElementById('success-criteria').value,
            potential_obstacles: document.getElementById('obstacles').value,
            support_needed: document.getElementById('support-needed').value
        };
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/send-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: JSON.stringify(formData),
                    type: 'action_commitment'
                })
            });
            
            const data = await response.json();
            
            if (data.message) {
                this.showChatInterface();
                this.addMessage('coach', data.message);
                this.showActionSummary(data.action_summary);
                this.updateSessionStatus('Session Complete - ' + new Date().toLocaleDateString());
            }
        } catch (error) {
            console.error('Error submitting action commitment:', error);
            this.showError('Failed to submit action commitment.');
        } finally {
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
            messageContent.appendChild(insightsDiv);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Ensure input remains enabled after adding messages
        this.ensureInputEnabled();
        
        console.log('🔍 DEBUG: Scrolled to bottom');
    }
    
    ensureInputEnabled() {
        // Safety function to ensure input is always available
        const inputEl = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');
        
        if (inputEl && !this.isLoading) {
            inputEl.disabled = false;
            inputEl.removeAttribute('disabled');
            inputEl.style.pointerEvents = 'auto';
            inputEl.style.opacity = '1';
        }
        
        if (sendBtn && !this.isLoading) {
            sendBtn.disabled = false;
        }
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
        
        sentimentSpan.textContent = analysis.sentiment;
        sentimentSpan.className = `sentiment ${analysis.sentiment}`;
        
        const primaryEmotion = this.getPrimaryEmotion(analysis.emotions);
        emotionSpan.textContent = primaryEmotion || 'neutral';
        
        analysisDiv.style.display = 'block';
        
        // Hide after 5 seconds
        setTimeout(() => {
            analysisDiv.style.display = 'none';
        }, 5000);
    }
    
    getPrimaryEmotion(emotions) {
        if (!emotions) return null;
        
        let maxEmotion = '';
        let maxScore = 0;
        
        Object.entries(emotions).forEach(([emotion, score]) => {
            if (score > maxScore && score > 0.3) {
                maxScore = score;
                maxEmotion = emotion;
            }
        });
        
        return maxEmotion;
    }
    
    showActionPlanningOption() {
        const input = document.getElementById('user-input');
        input.placeholder = "Ready to create an action plan? Type 'yes' or continue sharing your thoughts...";
        
        // Add action planning button
        const actionBtn = document.createElement('button');
        actionBtn.className = 'btn btn-primary';
        actionBtn.innerHTML = '<i class="fas fa-tasks"></i> Create Action Plan';
        actionBtn.style.marginTop = '1rem';
        actionBtn.onclick = () => this.showActionForm();
        
        const inputArea = document.querySelector('.input-area');
        if (!inputArea.querySelector('.action-planning-btn')) {
            actionBtn.className += ' action-planning-btn';
            inputArea.appendChild(actionBtn);
        }
    }
    
    showActionSummary(actionSummary) {
        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'action-summary';
        summaryDiv.innerHTML = `
            <h4><i class="fas fa-check-circle"></i> Action Commitment</h4>
            <div class="summary-content">
                <p><strong>Action:</strong> ${actionSummary.action}</p>
                <p><strong>Deadline:</strong> ${actionSummary.by_when}</p>
                <p><strong>Success Criteria:</strong> ${actionSummary.success_criteria}</p>
                <p><strong>Potential Obstacles:</strong> ${actionSummary.potential_obstacles}</p>
                <p><strong>Support Needed:</strong> ${actionSummary.support_needed}</p>
            </div>
        `;
        
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.appendChild(summaryDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    showInsights(insights) {
        insights.forEach(insight => {
            this.addMessage('coach', `💡 Insight: ${insight}`);
        });
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
    
    showWelcomeScreen() {
        document.getElementById('welcome-screen').style.display = 'flex';
        document.getElementById('chat-interface').style.display = 'none';
        document.getElementById('action-form').style.display = 'none';
    }
    
    showChatInterface() {
        console.log('🔄 DEBUG: showChatInterface() called');
        
        const welcomeScreen = document.getElementById('welcome-screen');
        const chatInterface = document.getElementById('chat-interface');
        const actionForm = document.getElementById('action-form');
        
        console.log('🔍 DEBUG: Elements found - welcome:', !!welcomeScreen, 'chat:', !!chatInterface, 'action:', !!actionForm);
        
        if (welcomeScreen) welcomeScreen.style.display = 'none';
        if (chatInterface) chatInterface.style.display = 'flex';
        if (actionForm) actionForm.style.display = 'none';
        
        console.log('🔄 DEBUG: Display styles updated');
        
        // Ensure input is fully enabled and ready
        setTimeout(() => {
            const inputEl = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');
            
            console.log('🔍 DEBUG: Input elements found - input:', !!inputEl, 'button:', !!sendBtn);
            
            if (inputEl) {
                // Force enable the input field
                inputEl.disabled = false;
                inputEl.removeAttribute('disabled');
                inputEl.style.pointerEvents = 'auto';
                inputEl.style.opacity = '1';
                inputEl.readOnly = false;
                
                // Focus on input
                inputEl.focus();
                console.log('✅ DEBUG: Chat interface shown, input field enabled and focused');
            }
            
            if (sendBtn) {
                sendBtn.disabled = false;
                console.log('✅ DEBUG: Send button enabled');
            }
            
            // Reset loading state
            this.isLoading = false;
        }, 100);
    }
    
    showActionForm() {
        document.getElementById('welcome-screen').style.display = 'none';
        document.getElementById('chat-interface').style.display = 'none';
        document.getElementById('action-form').style.display = 'block';
        
        // Focus on first input
        setTimeout(() => {
            document.getElementById('action-input').focus();
        }, 100);
    }
    
    showLoading(show) {
        console.log('🔍 DEBUG: showLoading called with:', show);
        this.isLoading = show;
        
        // Clear any existing timeout
        if (this.loadingTimeout) {
            clearTimeout(this.loadingTimeout);
            this.loadingTimeout = null;
        }
        
        const loadingEl = document.getElementById('loading');
        if (loadingEl) {
            loadingEl.style.display = show ? 'flex' : 'none';
        }
        
        if (show) {
            // Set a timeout to automatically clear loading after 15 seconds
            this.loadingTimeout = setTimeout(() => {
                console.log('⚠️ DEBUG: Loading timeout reached, forcing clear');
                this.showLoading(false);
                this.showError('Request timed out. Please try again.');
            }, 15000);
        }
        
        // Handle send button state
        const sendBtn = document.getElementById('send-btn');
        if (sendBtn) {
            sendBtn.disabled = show;
            console.log('🔍 DEBUG: Send button disabled:', show);
        }
        
        // Handle input field state
        const inputEl = document.getElementById('user-input');
        if (inputEl) {
            inputEl.disabled = show;
            console.log('🔍 DEBUG: Loading state set to:', show, 'isLoading:', this.isLoading);
            
            if (!show) {
                // Force re-enable input and make it focusable
                setTimeout(() => {
                    inputEl.disabled = false;
                    inputEl.removeAttribute('disabled');
                    inputEl.style.pointerEvents = 'auto';
                    inputEl.style.opacity = '1';
                    
                    // Try to focus the input
                    try {
                        inputEl.focus();
                        console.log('✅ DEBUG: Input field re-enabled and focused');
                    } catch (e) {
                        console.log('⚠️ DEBUG: Could not focus input:', e);
                    }
                }, 200);
            } else {
                // When loading, ensure input is clearly disabled
                inputEl.style.opacity = '0.5';
                inputEl.blur(); // Remove focus
            }
        }
        
        console.log('🔍 DEBUG: Loading state changed to:', show);
    }
    
    showError(message) {
        console.log('🚨 DEBUG: showError() called with message:', message);
        
        // Better error display with UI recovery
        alert(message);
        
        // Reset UI state to allow user to try again
        this.isLoading = false;
        this.showLoading(false);
        
        // Enable send button and clear any stuck states
        const sendBtn = document.getElementById('send-btn');
        if (sendBtn) sendBtn.disabled = false;
        
        // Focus back on input for retry
        const input = document.getElementById('user-input');
        if (input) {
            setTimeout(() => input.focus(), 100);
        }
        
        // If this is a session-related error, offer to restart
        if (message.includes('session') || message.includes('Session')) {
            console.log('🔄 DEBUG: Session error detected, might need session restart');
            if (confirm('There seems to be a session issue. Would you like to restart the session?')) {
                console.log('🔄 DEBUG: User confirmed session restart');
                this.restartSession();
            } else {
                console.log('🔄 DEBUG: User cancelled session restart');
            }
        }
        
        console.log('✅ DEBUG: UI state reset after error:', message);
    }
    
    async restartSession() {
        console.log('🔄 DEBUG: Restarting session...');
        this.sessionId = null;
        this.currentStage = 'intake';
        
        // Clear chat messages
        document.getElementById('chat-messages').innerHTML = '';
        
        // Start a new session
        await this.startNewSession();
        
        console.log('✅ DEBUG: Session restarted successfully');
    }
    
    generateUserId() {
        return 'user_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CoachingAssistant();
});

// Add some utility functions for enhanced UX
function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Auto-resize textareas
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('input', () => adjustTextareaHeight(textarea));
    });
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + / to focus on input
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        const input = document.getElementById('user-input');
        if (input) input.focus();
    }
    
    // Escape to clear input
    if (e.key === 'Escape') {
        const input = document.getElementById('user-input');
        if (input && document.activeElement === input) {
            input.value = '';
        }
    }
}); 
