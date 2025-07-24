document.addEventListener("DOMContentLoaded", (event) => {
    const socket = io.connect("http://127.0.0.1:5000");
    let currentUsername = "";

    socket.on("connect", function () {
        console.log("Connected to the server");
        while (!currentUsername) {
            currentUsername = prompt("Enter your username:");
        }
        socket.emit("set_username", currentUsername);
        updateUserProfile(currentUsername);
    });

    socket.on("message", function (msg) {
        console.log("Message received: " + msg);
        hideWelcomeMessage();

        const messageContainer = document.createElement("div");
        const messageDiv = document.createElement("div");
        const usernameDiv = document.createElement("div");

        const [username, message] = msg.split(": ", 2);

        usernameDiv.textContent = username;
        messageDiv.textContent = message;

        // Clear message styles
        messageDiv.className = "";
        usernameDiv.className = "";
        messageContainer.className = "";

        if (username === "System") {
            messageContainer.classList.add("flex", "justify-center", "mb-3");
            messageDiv.classList.add("message-bubble", "message-system", "p-3", "text-sm");
            usernameDiv.classList.add("sr-only"); // Hide system username
        } else if (username === currentUsername) {
            messageContainer.classList.add("flex", "justify-end", "mb-3");
            messageDiv.classList.add("message-bubble", "message-sent", "p-3", "text-white");
            usernameDiv.classList.add("text-xs", "text-right", "text-blue-200", "mb-1");
        } else {
            messageContainer.classList.add("flex", "flex-col", "items-start", "mb-3");
            messageDiv.classList.add("message-bubble", "message-received", "p-3");
            usernameDiv.classList.add("text-xs", "text-gray-600", "mb-1", "ml-2");
        }

        // Create message wrapper for better styling
        const messageWrapper = document.createElement("div");
        messageWrapper.classList.add("flex", "flex-col", username === currentUsername ? "items-end" : "items-start", "max-w-xs", "md:max-w-md");

        if (username !== "System") {
            messageWrapper.appendChild(usernameDiv);
        }
        messageWrapper.appendChild(messageDiv);
        messageContainer.appendChild(messageWrapper);

        document.getElementById("messages").appendChild(messageContainer);
        scrollToBottom();
    });

    socket.on("update_user_list", function (userList) {
        const userListDiv = document.getElementById("user-list");
        const userCountDiv = document.getElementById("user-count");

        userListDiv.innerHTML = "";
        userCountDiv.textContent = userList.length;

        if (userList.length === 0) {
            userListDiv.innerHTML = '<div class="text-gray-500 text-sm italic">No users online</div>';
        } else {
            userList.forEach(function (user) {
                const userDiv = document.createElement("div");
                userDiv.classList.add("user-badge", "online");
                userDiv.innerHTML = `<i class="fas fa-user text-sm"></i>${user}`;
                userListDiv.appendChild(userDiv);
            });
        }
    });

    window.sendMessage = function () {
        const messageInput = document.getElementById("message-input");
        const message = messageInput.value.trim();

        if (message === "") return;

        socket.send(message);
        messageInput.value = "";
        messageInput.focus();
    };

    // Helper functions
    function updateUserProfile(username) {
        const userProfile = document.getElementById("user-profile");
        userProfile.innerHTML = `<i class="fas fa-user-circle text-2xl mr-2"></i><span class="font-medium">${username}</span>`;
    }

    function hideWelcomeMessage() {
        const messagesDiv = document.getElementById("messages");
        const welcomeMsg = messagesDiv.querySelector('.text-center');
        if (welcomeMsg) {
            welcomeMsg.style.display = 'none';
        }
    }

    function scrollToBottom() {
        const messagesDiv = document.getElementById("messages");
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // Auto-focus on message input
    document.getElementById("message-input").focus();
});
