document.addEventListener("DOMContentLoaded", (event) => {
    const socket = io.connect("http://127.0.0.1:5000");
    let currentUsername = "";

    socket.on("connect", function () {
        console.log("Connected to the server");
        while (!currentUsername) {
            currentUsername = prompt("Enter your username:");
        }
        socket.emit("set_username", currentUsername);
    });

    socket.on("message", function (msg) {
        console.log("Message received: " + msg);
        const messageDiv = document.createElement("div");
        const usernameSpan = document.createElement("span");
        const messageContentSpan = document.createElement("span");

        const [username, message] = msg.split(": ", 2); // Split the message to get username and message content

        usernameSpan.textContent = username + ": ";
        messageContentSpan.textContent = message;

        if (username === currentUsername) {
            messageDiv.classList.add("flex", "justify-end", "mb-2");
            messageContentSpan.classList.add(
                "bg-blue-100",
                "p-2",
                "rounded",
                "text-right",
                // "inline-block",
                "max-w-xl"
            );
            usernameSpan.classList.add(
                "font-bold",
                "text-right",
                "text-blue-500"
                // "inline-block"
            );
        } else {
            messageDiv.classList.add("flex", "justify-start", "mb-2");
            messageContentSpan.classList.add(
                "bg-gray-100",
                "p-2",
                "rounded",
                "text-left",
                // "inline-block",
                "max-w-xl"
            );
            usernameSpan.classList.add(
                "font-bold",
                "text-left",
                "text-green-500"
                // "inline-block"
            );
        }

        messageDiv.appendChild(usernameSpan);
        messageDiv.appendChild(messageContentSpan);
        document.getElementById("messages").appendChild(messageDiv);
    });

    socket.on("update_user_list", function (userList) {
        const userListDiv = document.getElementById("user-list");
        userListDiv.innerHTML = "";
        userList.forEach(function (user) {
            const userDiv = document.createElement("div");
            userDiv.textContent = user;
            userListDiv.appendChild(userDiv);
        });
    });

    window.sendMessage = function () {
        const messageInput = document.getElementById("message-input");
        const message = messageInput.value;
        // socket.send(`${currentUsername}: ${message}`);
        socket.send(message);
        messageInput.value = "";
    };
});
