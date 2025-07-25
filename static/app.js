class CoachingAssistant {
    constructor() {
        this.sessionId = null;
        this.userId = null;
        this.currentStage = 'intake';
        this.isLoading = false;
        
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
                const topic = e.currentTarget.dataset.topic;
                this.selectTopic(topic);
            });
        });
        
        // New session button
        document.getElementById('new-session-btn').addEventListener('click', () => {
            this.startNewSession();
        });
        
        // Send message
        document.getElementById('send-btn').addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Enter key to send message
        document.getElementById('user-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
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
    
    async startNewSession() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/start-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId || this.generateUserId()
                })
            });
            
            const data = await response.json();
            
            if (data.session_id) {
                this.sessionId = data.session_id;
                this.userId = data.user_id;
                this.currentStage = 'intake';
                
                this.updateSessionStatus('Session Active');
                this.showChatInterface();
                this.addMessage('coach', data.response.message, data.response.questions);
                this.updateStageIndicator('intake');
            }
        } catch (error) {
            console.error('Error starting session:', error);
            this.showError('Failed to start session. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }
    
    async selectTopic(topicKey) {
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
                this.addMessage('coach', data.message, data.questions);
                this.updateStageIndicator(data.stage);
                this.currentStage = data.stage;
                
                if (data.emotional_analysis) {
                    this.showEmotionalAnalysis(data.emotional_analysis);
                }
            }
        } catch (error) {
            console.error('Error selecting topic:', error);
            this.showError('Failed to process topic selection.');
        } finally {
            this.showLoading(false);
        }
    }
    
    async sendMessage() {
        const input = document.getElementById('user-input');
        const message = input.value.trim();
        
        if (!message || this.isLoading) return;
        
        // Add user message to chat
        this.addMessage('user', message);
        input.value = '';
        
        this.showLoading(true);
        
        try {
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
            
            const data = await response.json();
            
            if (data.message) {
                this.addMessage('coach', data.message, data.questions);
                
                if (data.personalized_message) {
                    this.addMessage('coach', data.personalized_message);
                }
                
                this.updateStageIndicator(data.stage);
                this.currentStage = data.stage;
                
                if (data.emotional_analysis) {
                    this.showEmotionalAnalysis(data.emotional_analysis);
                }
                
                if (data.stage === 'action_planning' && data.action_template) {
                    this.showActionPlanningOption();
                }
                
                if (data.insights && data.insights.length > 0) {
                    this.showInsights(data.insights);
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.showError('Failed to send message. Please try again.');
        } finally {
            this.showLoading(false);
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
            const questionsDiv = document.createElement('div');
            questionsDiv.className = 'message-questions';
            
            const questionsTitle = document.createElement('h4');
            questionsTitle.textContent = 'Reflection Questions:';
            questionsDiv.appendChild(questionsTitle);
            
            const questionsList = document.createElement('ul');
            questions.forEach(question => {
                const li = document.createElement('li');
                li.textContent = question;
                questionsList.appendChild(li);
            });
            questionsDiv.appendChild(questionsList);
            messageContent.appendChild(questionsDiv);
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
    }
    
    showEmotionalAnalysis(analysis) {
        const analysisDiv = document.getElementById('emotional-analysis');
        const sentimentSpan = document.getElementById('sentiment-indicator');
        const emotionSpan = document.getElementById('primary-emotion');
        
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
        document.getElementById('welcome-screen').style.display = 'none';
        document.getElementById('chat-interface').style.display = 'flex';
        document.getElementById('action-form').style.display = 'none';
        
        // Focus on input
        setTimeout(() => {
            document.getElementById('user-input').focus();
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
        this.isLoading = show;
        document.getElementById('loading').style.display = show ? 'flex' : 'none';
        
        // Disable/enable send button
        const sendBtn = document.getElementById('send-btn');
        sendBtn.disabled = show;
    }
    
    showError(message) {
        // Simple error display - could be enhanced with a toast or modal
        alert(message);
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
