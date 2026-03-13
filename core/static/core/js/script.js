/* Care & Cure Interactive Logic v2 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Care & Cure Premium JS Loaded');

    // Header scroll effect
    const header = document.querySelector('header');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 20) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Risk bar animation with intersection observer
    const riskFill = document.querySelector('.risk-fill');
    if (riskFill) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const risk = riskFill.getAttribute('data-risk');
                    setTimeout(() => {
                        riskFill.style.width = risk + '%';
                    }, 400);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        observer.observe(riskFill);
    }

    // Form validation feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            requiredFields.forEach(field => {
                if (!field.value) {
                    field.classList.add('is-invalid');
                    valid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!valid) {
                e.preventDefault();
                form.classList.add('shake');
                setTimeout(() => form.classList.remove('shake'), 500);
            }
        });
    });

    // Prescription Scanning Enhancements
    const imageInput = document.querySelector('input[type="file"][name="prescription_image"]');
    const imagePreview = document.getElementById('image-preview');
    const previewContainer = document.getElementById('image-preview-container');
    const prescriptionForm = document.getElementById('prescription-form');
    const scanningOverlay = document.getElementById('scanning-overlay');

    if (imageInput) {
        imageInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    if (imagePreview) {
                        imagePreview.src = e.target.result;
                        previewContainer.style.display = 'block';
                        previewContainer.style.animation = 'slideUp 0.5s ease-out';
                    }
                }
                reader.readAsDataURL(file);
            }
        });
    }

    if (prescriptionForm && scanningOverlay) {
        prescriptionForm.addEventListener('submit', function (e) {
            const file = imageInput ? imageInput.files[0] : null;
            if (file) {
                e.preventDefault();
                scanningOverlay.style.display = 'flex';
                // Premium "Wait" sequence
                const statusText = scanningOverlay.querySelector('p');
                setTimeout(() => { if(statusText) statusText.innerText = "Analyzing Vitals..."; }, 1200);
                setTimeout(() => { if(statusText) statusText.innerText = "Checking Drug Interactions..."; }, 2500);
                setTimeout(() => {
                    prescriptionForm.submit();
                }, 3800);
            }
        });
    }

    /* --- Advanced AI Chat Widget --- */
    const chatHTML = `
    <div id="ai-chat-widget" style="position: fixed; bottom: 30px; right: 30px; z-index: 10000;">
        <button id="chat-toggle" class="btn btn-primary rounded-circle shadow-lg" style="width: 65px; height: 65px; border-radius: 50% !important;">
            <i class="fas fa-comment-dots fa-2x"></i>
        </button>

        <div id="chat-window" class="card shadow-lg border-0 d-none" style="position: absolute; bottom: 85px; right: 0; width: 380px; height: 550px; border-radius: 24px; overflow: hidden; display: flex; flex-direction: column; opacity: 0; transform: translateY(20px); transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);">
            <div class="card-header bg-primary text-white p-4 d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-0 fw-800"><i class="fas fa-shield-virus me-2"></i>CareAI</h6>
                    <small class="opacity-75">Your Clinical Assistant</small>
                </div>
                <button id="chat-close" class="btn btn-sm text-white opacity-50"><i class="fas fa-times"></i></button>
            </div>
            <div id="chat-messages" class="card-body bg-white overflow-auto p-4" style="flex: 1;">
                <div class="msg ai mb-3">
                    <div class="p-3 rounded-4 bg-light small shadow-sm" style="max-width: 85%; border-bottom-left-radius: 4px;">
                        Welcome to the premium Care & Cure experience. How can I assist with your health data today?
                    </div>
                </div>
            </div>
            <div class="card-footer bg-white p-3 border-0">
                <div class="input-group bg-light rounded-pill px-3 py-1">
                    <input type="text" id="chat-input" class="form-control border-0 bg-transparent" placeholder="Ask about your vitals..." style="box-shadow: none;">
                    <button id="chat-send" class="btn btn-link text-primary"><i class="fas fa-paper-plane fa-lg"></i></button>
                </div>
            </div>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', chatHTML);

    const chatToggle = document.getElementById('chat-toggle');
    const chatWindow = document.getElementById('chat-window');
    const chatClose = document.getElementById('chat-close');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const chatMessages = document.getElementById('chat-messages');

    let isOpen = false;

    function toggleChat() {
        isOpen = !isOpen;
        if (isOpen) {
            chatWindow.classList.remove('d-none');
            setTimeout(() => {
                chatWindow.style.opacity = '1';
                chatWindow.style.transform = 'translateY(0)';
            }, 10);
        } else {
            chatWindow.style.opacity = '0';
            chatWindow.style.transform = 'translateY(20px)';
            setTimeout(() => chatWindow.classList.add('d-none'), 400);
        }
    }

    function addMessage(text, sender) {
        const isUser = sender === 'user';
        const html = `
        <div class="d-flex ${isUser ? 'justify-content-end' : 'justify-content-start'} mb-3">
            <div class="p-3 rounded-4 small ${isUser ? 'bg-primary text-white shadow-md' : 'bg-light text-dark shadow-sm'}" 
                 style="max-width: 85%; ${isUser ? 'border-bottom-right-radius: 4px;' : 'border-bottom-left-radius: 4px;'} animation: slideUp 0.3s ease-out;">
                ${text}
            </div>
        </div>`;
        chatMessages.insertAdjacentHTML('beforeend', html);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        chatInput.value = '';

        // Typing indicator
        const loadingId = 'typing-' + Date.now();
        const loadingHtml = `
            <div id="${loadingId}" class="d-flex justify-content-start mb-3 animate-pulse">
                <div class="bg-light p-3 rounded-4 small"><i class="fas fa-circle-notch fa-spin me-2"></i>CareAI is thinking...</div>
            </div>`;
        chatMessages.insertAdjacentHTML('beforeend', loadingHtml);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json', 
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' 
                },
                body: JSON.stringify({ message: text, url: window.location.href })
            });
            const data = await response.json();
            document.getElementById(loadingId).remove();
            addMessage(data.reply || "I'm having trouble connecting to medical databases.", 'ai');
        } catch (e) {
            document.getElementById(loadingId).remove();
            addMessage("Network error detected. Please check your connection.", 'ai');
        }
    }

    chatToggle.addEventListener('click', toggleChat);
    chatClose.addEventListener('click', toggleChat);
    chatSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

    // --- Patient Registry Filtering (Real-time) ---
    const patientSearch = document.getElementById('patient-search');
    const patientTable = document.getElementById('patient-table');
    if (patientSearch && patientTable) {
        patientSearch.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            const rows = patientTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const name = row.querySelector('.patient-name')?.innerText.toLowerCase() || '';
                if (name.includes(query)) {
                    row.style.display = '';
                    row.style.animation = 'fadeIn 0.3s ease-out';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // --- AI Chat Quick Commands & UI Feedback ---
    function addQuickCommands() {
        if (isPatient) { // Note: We should pass role context to JS
            const commands = [
                { text: "My Health Summary", msg: "Can you provide a summary of my current health status?" },
                { text: "Check Vitals", msg: "Analyze my recent blood pressure and sugar readings." },
                { text: "Safety Check", msg: "Run a drug safety check on my profile." }
            ];
            const cmdContainer = document.createElement('div');
            cmdContainer.className = 'px-3 pb-3 d-flex flex-wrap gap-2';
            commands.forEach(cmd => {
                const btn = document.createElement('button');
                btn.className = 'btn btn-xs btn-outline-primary rounded-pill extra-small fw-800 py-1 px-3';
                btn.innerText = cmd.text;
                btn.onclick = () => {
                    chatInput.value = cmd.msg;
                    sendMessage();
                };
                cmdContainer.appendChild(btn);
            });
            chatWindow.insertBefore(cmdContainer, chatWindow.querySelector('.card-footer'));
        }
    }

    // Simple role detection for JS
    const isPatient = document.querySelector('.fa-hand-holding-heart') !== null;
    if (isPatient) {
        addQuickCommands();
    }

    // --- Visual Feedback for Appointments ---
    const handleButtons = document.querySelectorAll('.btn-group a[href*="handle_appointment"]');
    handleButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            this.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i>';
            this.classList.add('disabled');
        });
    });
});
