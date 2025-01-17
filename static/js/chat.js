document.addEventListener("DOMContentLoaded", (event) => {
    const socket = io.connect("http://127.0.0.1:5000");
    let currentUsername = "";

    socket.on("connect", function () {
        console.log("Connected to the server");
        while (!currentUsername) {
            currentUsername = prompt("Enter your username:");
        }
        socket.emit("set_username", currentUsername);
        document.getElementById(
            "user-profile"
        ).textContent = `You are logged in as: ${currentUsername}`;
    });

    socket.on("message", function (msg) {
        console.log("Message received: " + msg);
        const messageContainer = document.createElement("div");
        const messageDiv = document.createElement("div");
        const usernameDiv = document.createElement("div");

        const [username, message] = msg.split(": ", 2); // Split the message to get username and message content

        usernameDiv.textContent = username;
        messageDiv.textContent = message;

        if (username === currentUsername) {
            messageContainer.classList.add(
                "flex",
                "flex-col",
                "items-end",
                "mb-2"
            );
            messageDiv.classList.add(
                "bg-blue-100",
                "p-2",
                "rounded",
                "text-right",
                "inline-block",
                "max-w-xl"
            );
            usernameDiv.classList.add(
                "font-bold",
                "text-right",
                "text-blue-500"
            );
        } else {
            messageContainer.classList.add(
                "flex",
                "flex-col",
                "items-start",
                "mb-2"
            );
            messageDiv.classList.add(
                "bg-gray-100",
                "p-2",
                "rounded",
                "text-left",
                "inline-block",
                "max-w-xl"
            );
            usernameDiv.classList.add(
                "font-bold",
                "text-left",
                "text-green-500"
            );
        }

        messageContainer.appendChild(usernameDiv);
        messageContainer.appendChild(messageDiv);
        document.getElementById("messages").appendChild(messageContainer);
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
