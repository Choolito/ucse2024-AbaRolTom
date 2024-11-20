document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");
    const chatIdDiv = document.getElementById("chat-partido");
    const chatIdUser = document.getElementById("chat-usuario");
    const chatId = parseInt(chatIdDiv.textContent, 10); // Convierte el contenido en un número entero
    const chatUsuario = parseInt(chatIdUser.textContent, 10); // Convierte el contenido en un número entero
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Cargar mensajes iniciales
    fetch(`/chat/${chatId}/`)
        .then((response) => response.json())
        .then((data) => {
            if (data && Array.isArray(data)) {
                data.forEach((message) => {
                    const messageElement = document.createElement("div");
                    messageElement.textContent = `${message.usuario}: ${message.mensaje}`;
                    messageElement.classList.add("text-start", "my-1");
                    chatMessages.appendChild(messageElement);
                });
            } 
        });

    // Enviar mensaje
    chatForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const message = chatInput.value;

        debugger;
        // Enviar los datos correctamente con la estructura que la API espera
        fetch(`/chat/${chatId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                'X-CSRFToken': csrfToken  // Incluir el token CSRF en el encabezado
            },
            body: JSON.stringify({
                mensaje: message,  // Renombrado de 'text' a 'mensaje'
                partido: chatId,   // Incluir el ID del partido
                usuario: chatUsuario,   // Este es el ID del usuario 
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                const messageElement = document.createElement("div");
                messageElement.textContent = `Tú: ${data.mensaje}`;  // Usar 'mensaje' en lugar de 'text'
                messageElement.classList.add("text-end", "text-primary", "my-1");
                chatMessages.appendChild(messageElement);
                chatInput.value = "";
            });
    });
});

(function () {
    'use strict'
    var forms = document.querySelectorAll('.needs-validation')
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                }
                form.classList.add('was-validated')
            }, false)
        })
})()