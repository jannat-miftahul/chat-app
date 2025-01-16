document.addEventListener("DOMContentLoaded", (event) => {
    const socket = io.connect("http://127.0.0.1:5000");

    socket.on("connect", function () {
        console.log("Connected to the server");
        let username = "";
        while (!username) {
            username = prompt("Enter your username:");
        }
        socket.emit("set_username", username);
    });

    socket.on("message", function (msg) {
        console.log("Message received: " + msg);
        const messageDiv = document.createElement("div");
        messageDiv.textContent = msg;
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
        socket.send(message);
        messageInput.value = "";
    };
});
