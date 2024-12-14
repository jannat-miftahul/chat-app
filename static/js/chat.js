const socket = io.connect("http://127.0.0.1:5000");

socket.on("connect", function () {
    console.log("Connected to the server");
});

socket.on("message", function (msg) {
    console.log("Message received: " + msg);
    const messageDiv = document.createElement("div");
    messageDiv.textContent = msg;
    document.getElementById("messages").appendChild(messageDiv);
});

function sendMessage() {
    const messageInput = document.getElementById("message-input");
    const message = messageInput.value;
    socket.send(message);
    messageInput.value = "";
}
