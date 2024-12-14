const socket = io();

function sendMessage() {
    const messageInput = document.getElementById("message-input");
    const message = messageInput.value;
    socket.send(message);
    messageInput.value = '';
}

socket.on('message', function(msg) {
    const messageDiv = document.createElement("div");
    messageDiv.textContent = msg;
    document.getElementById("messages").appendChild(messageDiv);
});
