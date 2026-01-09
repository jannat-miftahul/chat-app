/**
 * QuikTalk - Cute Chat Application
 * Enhanced JavaScript with rooms, private messaging, and modern UI
 */

document.addEventListener("DOMContentLoaded", () => {
    // ============================================
    // Configuration & State
    // ============================================
    const socket = io.connect(window.location.origin);

    let state = {
        currentUsername: "",
        currentRoom: "general",
        isEncryptionEnabled: false,
        dmTarget: null,
        rooms: [],
        users: [],
    };

    // ============================================
    // DOM Elements
    // ============================================
    const elements = {
        // Modals
        usernameModal: document.getElementById("username-modal"),
        usernameInput: document.getElementById("username-input"),
        joinChatBtn: document.getElementById("join-chat-btn"),
        createRoomModal: document.getElementById("create-room-modal"),

        // Sidebar
        sidebar: document.getElementById("sidebar"),
        mobileMenuBtn: document.getElementById("mobile-menu-btn"),
        userProfile: document.getElementById("user-profile"),
        roomsList: document.getElementById("rooms-list"),
        userList: document.getElementById("user-list"),
        userCount: document.getElementById("user-count"),
        createRoomBtn: document.getElementById("create-room-btn"),

        // Chat Area
        currentRoomName: document.getElementById("current-room-name"),
        typingStatus: document.getElementById("typing-status"),
        messagesContainer: document.getElementById("messages"),
        messageInput: document.getElementById("message-input"),
        sendBtn: document.getElementById("send-btn"),
        emojiBtn: document.getElementById("emoji-btn"),
        emojiPicker: document.getElementById("emoji-picker"),
        toggleEncryption: document.getElementById("toggle-encryption"),

        // DM Panel
        dmPanel: document.getElementById("dm-panel"),
        closeDm: document.getElementById("close-dm"),
        dmUsername: document.getElementById("dm-username"),
        dmMessages: document.getElementById("dm-messages"),
        dmInput: document.getElementById("dm-input"),
        dmSendBtn: document.getElementById("dm-send-btn"),

        // Room Creation
        roomNameInput: document.getElementById("room-name-input"),
        roomDescInput: document.getElementById("room-desc-input"),
        roomPrivate: document.getElementById("room-private"),
        confirmCreateRoom: document.getElementById("confirm-create-room"),
    };

    // ============================================
    // Emoji Avatars for Users
    // ============================================
    const avatarEmojis = [
        "😊",
        "😎",
        "🥳",
        "😇",
        "🤗",
        "🦊",
        "🐱",
        "🐶",
        "🐰",
        "🐻",
        "🦋",
        "🌸",
        "⭐",
        "🌟",
        "💖",
    ];

    function getRandomAvatar() {
        return avatarEmojis[Math.floor(Math.random() * avatarEmojis.length)];
    }

    // ============================================
    // Socket Event Handlers
    // ============================================

    // Connection established
    socket.on("connect", () => {
        console.log("🐱 Connected to QuikTalk server!");
    });

    // Username confirmation
    socket.on("username_set", (data) => {
        state.currentUsername = data.username;
        updateUserProfile(data.username);
        elements.usernameModal.classList.remove("active");
        showNotification("Welcome to QuikTalk! 🎉", "success");
    });

    // Receive room messages
    socket.on("receive_message", (data) => {
        displayMessage(data);
    });

    // Legacy message format support
    socket.on("message", (msg) => {
        if (typeof msg === "string") {
            const [sender, ...contentParts] = msg.split(": ");
            const content = contentParts.join(": ");
            displayMessage({
                sender: sender,
                content: content,
                timestamp: new Date().toISOString(),
            });
        }
    });

    // Update user list
    socket.on("update_user_list", (userList) => {
        state.users = userList;
        renderUserList(userList);
    });

    // Room list received
    socket.on("room_list", (data) => {
        if (data.success) {
            state.rooms = data.rooms;
            renderRoomList(data.rooms);
        }
    });

    // Room created
    socket.on("room_created", (data) => {
        if (data.success) {
            showNotification(`Room "${data.room.name}" created! 🏠`, "success");
            closeModal(elements.createRoomModal);
            socket.emit("get_rooms");
        } else {
            showNotification(data.error, "error");
        }
    });

    // Joined room
    socket.on("joined_room", (data) => {
        if (data.success) {
            state.currentRoom = data.room.id;
            elements.currentRoomName.textContent = data.room.name;

            // Clear messages and load history
            clearMessages();
            if (data.history && data.history.length > 0) {
                data.history.forEach((msg) => displayMessage(msg, false));
            }

            showNotification(`Joined ${data.room.name}! ✨`, "success");
        }
    });

    // User joined room notification
    socket.on("user_joined_room", (data) => {
        if (data.username !== state.currentUsername) {
            displaySystemMessage(`${data.username} joined the room 👋`);
        }
    });

    // User left room notification
    socket.on("user_left_room", (data) => {
        displaySystemMessage(`${data.username} left the room 👋`);
    });

    // Private message received
    socket.on("private_message", (data) => {
        if (state.dmTarget === data.sender) {
            displayDmMessage(data, false);
        } else {
            showNotification(`💌 New message from ${data.sender}`, "info");
        }
    });

    // Private message sent confirmation
    socket.on("private_message_sent", (data) => {
        displayDmMessage(data, true);
    });

    // Conversation history
    socket.on("conversation_history", (data) => {
        elements.dmMessages.innerHTML = "";
        data.messages.forEach((msg) => {
            displayDmMessage(msg, msg.sender === state.currentUsername);
        });
    });

    // Error handling
    socket.on("error", (data) => {
        showNotification(data.message, "error");
    });

    // ============================================
    // UI Rendering Functions
    // ============================================

    function updateUserProfile(username) {
        const avatar = getRandomAvatar();
        elements.userProfile.innerHTML = `
            <div class="profile-avatar">
                <span class="avatar-emoji">${avatar}</span>
                <span class="status-dot"></span>
            </div>
            <div class="profile-info">
                <span class="profile-name">${username}</span>
                <span class="profile-status">Online</span>
            </div>
        `;
    }

    function renderUserList(users) {
        elements.userCount.textContent = users.length;

        if (users.length === 0) {
            elements.userList.innerHTML = `
                <div class="empty-state">
                    <span>🔍</span>
                    <span>No friends online</span>
                </div>
            `;
            return;
        }

        elements.userList.innerHTML = users
            .map((user) => {
                const avatar = getRandomAvatar();
                const isCurrentUser = user === state.currentUsername;
                return `
                <div class="user-item ${isCurrentUser ? "current-user" : ""}" 
                     data-username="${user}" 
                     ${!isCurrentUser
                        ? "onclick=\"openDm('" + user + "')\""
                        : ""
                    }>
                    <div class="user-avatar">${avatar}</div>
                    <span class="user-name">${user}${isCurrentUser ? " (You)" : ""
                    }</span>
                    <span class="user-status-indicator"></span>
                </div>
            `;
            })
            .join("");
    }

    function renderRoomList(rooms) {
        elements.roomsList.innerHTML = rooms
            .map((room) => {
                const isActive = room.id === state.currentRoom;
                const icons = ["🌟", "🎮", "🎵", "📚", "☕", "🌸", "🎨", "💬"];
                const icon =
                    room.id === "general"
                        ? "🌟"
                        : icons[Math.floor(Math.random() * icons.length)];

                return `
                <div class="room-item ${isActive ? "active" : ""}" 
                     data-room="${room.id}" 
                     onclick="joinRoom('${room.id}')">
                    <span class="room-icon">${icon}</span>
                    <span class="room-name">${room.name}</span>
                    <span class="room-badge">${room.member_count || 0}</span>
                </div>
            `;
            })
            .join("");
    }

    function displayMessage(data, animate = true) {
        hideWelcomeMessage();

        const isOwn = data.sender === state.currentUsername;
        const isSystem = data.sender === "System";

        const wrapper = document.createElement("div");
        wrapper.className = `message-wrapper ${isOwn ? "sent" : isSystem ? "system" : "received"
            }`;
        if (animate) wrapper.style.animation = "fadeInUp 0.3s ease";

        const time = data.timestamp
            ? formatTime(data.timestamp)
            : formatTime(new Date().toISOString());

        if (isSystem) {
            wrapper.innerHTML = `
                <div class="message-bubble">
                    ${data.content}
                </div>
            `;
        } else {
            const encryptedBadge = data.encrypted
                ? '<span class="encrypted-badge">🔐</span>'
                : "";
            wrapper.innerHTML = `
                ${!isOwn
                    ? `<span class="message-sender">${data.sender}</span>`
                    : ""
                }
                <div class="message-bubble">
                    ${data.content}${encryptedBadge}
                </div>
                <span class="message-time">${time}</span>
            `;
        }

        elements.messagesContainer.appendChild(wrapper);
        scrollToBottom();
    }

    function displaySystemMessage(message) {
        displayMessage({
            sender: "System",
            content: message,
            timestamp: new Date().toISOString(),
        });
    }

    function displayDmMessage(data, isSent) {
        const wrapper = document.createElement("div");
        wrapper.className = `message-wrapper ${isSent ? "sent" : "received"}`;

        const time = formatTime(data.timestamp);
        const encryptedBadge = data.encrypted
            ? '<span class="encrypted-badge">🔐</span>'
            : "";

        wrapper.innerHTML = `
            <div class="message-bubble">
                ${data.content}${encryptedBadge}
            </div>
            <span class="message-time">${time}</span>
        `;

        elements.dmMessages.appendChild(wrapper);
        elements.dmMessages.scrollTop = elements.dmMessages.scrollHeight;
    }

    function clearMessages() {
        elements.messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">🎉</div>
                <h2>Welcome to QuikTalk!</h2>
                <p>Start chatting with your friends ✨</p>
                <div class="welcome-features">
                    <span>💬 Real-time messaging</span>
                    <span>🔐 Encrypted chats</span>
                    <span>🏠 Multiple rooms</span>
                </div>
            </div>
        `;
    }

    function hideWelcomeMessage() {
        const welcome =
            elements.messagesContainer.querySelector(".welcome-message");
        if (welcome) welcome.remove();
    }

    function scrollToBottom() {
        elements.messagesContainer.scrollTop =
            elements.messagesContainer.scrollHeight;
    }

    // ============================================
    // Action Functions
    // ============================================

    window.sendMessage = function () {
        const message = elements.messageInput.value.trim();
        if (!message) return;

        socket.emit("message", {
            message: message,
            room: state.currentRoom,
            encrypt: state.isEncryptionEnabled,
        });

        elements.messageInput.value = "";
        elements.messageInput.focus();
    };

    window.joinRoom = function (roomId) {
        if (roomId === state.currentRoom) return;

        // Update UI immediately
        document.querySelectorAll(".room-item").forEach((item) => {
            item.classList.toggle("active", item.dataset.room === roomId);
        });

        socket.emit("join_room", { room_id: roomId });
    };

    window.openDm = function (username) {
        if (username === state.currentUsername) return;

        state.dmTarget = username;
        elements.dmUsername.textContent = username;
        elements.dmMessages.innerHTML = "";
        elements.dmPanel.classList.add("active");

        // Load conversation history
        socket.emit("get_conversation", { with_user: username });

        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            elements.sidebar.classList.remove("active");
        }
    };

    function sendDm() {
        const message = elements.dmInput.value.trim();
        if (!message || !state.dmTarget) return;

        socket.emit("private_message", {
            receiver: state.dmTarget,
            message: message,
            encrypt: true,
        });

        elements.dmInput.value = "";
    }

    function createRoom() {
        const name = elements.roomNameInput.value.trim();
        if (!name) {
            showNotification("Please enter a room name", "error");
            return;
        }

        socket.emit("create_room", {
            room_id: name.toLowerCase().replace(/\s+/g, "-"),
            name: name,
            description: elements.roomDescInput.value.trim(),
            is_private: elements.roomPrivate.checked,
        });
    }

    // ============================================
    // Event Listeners
    // ============================================

    // Join chat button
    elements.joinChatBtn.addEventListener("click", () => {
        const username = elements.usernameInput.value.trim();
        if (username) {
            socket.emit("set_username", username);
        } else {
            showNotification("Please enter a nickname! 🐱", "error");
        }
    });

    elements.usernameInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") elements.joinChatBtn.click();
    });

    // Send message
    elements.sendBtn.addEventListener("click", sendMessage);
    elements.messageInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    // DM sending
    elements.dmSendBtn.addEventListener("click", sendDm);
    elements.dmInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendDm();
    });

    // Close DM panel
    elements.closeDm.addEventListener("click", () => {
        elements.dmPanel.classList.remove("active");
        state.dmTarget = null;
    });

    // Create room
    elements.createRoomBtn.addEventListener("click", () => {
        elements.createRoomModal.classList.add("active");
    });

    elements.confirmCreateRoom.addEventListener("click", createRoom);

    // Modal close buttons
    document.querySelectorAll(".modal-close").forEach((btn) => {
        btn.addEventListener("click", () => {
            closeModal(btn.closest(".modal"));
        });
    });

    // Close modal on backdrop click
    document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
        backdrop.addEventListener("click", () => {
            const modal = backdrop.closest(".modal");
            if (modal.id !== "username-modal") {
                closeModal(modal);
            }
        });
    });

    // Mobile menu toggle
    elements.mobileMenuBtn.addEventListener("click", () => {
        elements.sidebar.classList.toggle("active");
    });

    // Emoji picker toggle
    elements.emojiBtn.addEventListener("click", () => {
        elements.emojiPicker.classList.toggle("active");
    });

    // Emoji selection
    elements.emojiPicker.querySelectorAll("span").forEach((emoji) => {
        emoji.addEventListener("click", () => {
            elements.messageInput.value += emoji.textContent;
            elements.emojiPicker.classList.remove("active");
            elements.messageInput.focus();
        });
    });

    // Close emoji picker when clicking outside
    document.addEventListener("click", (e) => {
        if (
            !elements.emojiBtn.contains(e.target) &&
            !elements.emojiPicker.contains(e.target)
        ) {
            elements.emojiPicker.classList.remove("active");
        }
    });

    // Toggle encryption
    elements.toggleEncryption.addEventListener("click", () => {
        state.isEncryptionEnabled = !state.isEncryptionEnabled;
        elements.toggleEncryption.innerHTML = state.isEncryptionEnabled
            ? '<i class="fas fa-lock"></i>'
            : '<i class="fas fa-lock-open"></i>';
        elements.toggleEncryption.style.color = state.isEncryptionEnabled
            ? "#ff6b9d"
            : "";
        showNotification(
            state.isEncryptionEnabled
                ? "Encryption enabled 🔐"
                : "Encryption disabled 🔓",
            "info"
        );
    });

    // ============================================
    // Utility Functions
    // ============================================

    function closeModal(modal) {
        modal.classList.remove("active");
    }

    function formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    function showNotification(message, type = "info") {
        // Create toast notification
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.innerHTML = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === "error"
                ? "#FF6FB5"
                : type === "success"
                    ? "#5CE1E6"
                    : "#9B7EDE"
            };
            color: ${type === "success" ? "#3D2C8D" : "white"};
            border-radius: 12px;
            font-weight: 600;
            box-shadow: 0 4px 20px rgba(61, 44, 141, 0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = "fadeOut 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Add toast animations to document
    const style = document.createElement("style");
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
    `;
    document.head.appendChild(style);

    // Focus username input on load
    elements.usernameInput.focus();
});
