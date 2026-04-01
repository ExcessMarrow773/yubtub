const chatSocket = new WebSocket("ws://" + window.location.host + "/");

function parseCommands(message, userName) {
	if (message === '/reload') {
		location.reload();
	}
}

chatSocket.onopen = function (e) {
  console.log("The connection was setup successfully !");
};
chatSocket.onclose = function (e) {
  console.log("Something unexpected happened !");
};
document.querySelector("#id_message_send_input").focus();
document.querySelector("#id_message_send_input").onkeyup = function (e) {
  if (e.keyCode == 13) {
	document.querySelector("#id_message_send_button").click();
  }
};
document.querySelector("#id_message_send_button").onclick = function (e) {
  var messageInput = document.querySelector(
	"#id_message_send_input"
  ).value;
  var userName = document.querySelector("#id_message_send_input").dataset.username
  chatSocket.send(JSON.stringify({ message: messageInput, username : userName}));
  window.scrollTo(0, document.body.scrollHeight);
};
chatSocket.onmessage = function (e) {
  const data = JSON.parse(e.data);
  var msg = document.createElement("msg");
  var userName = document.querySelector("#id_message_send_input").dataset.username

  msg.innerHTML = data.username + ": " + data.message;
  if (data.username !== userName) {
	  msg.classList.add('from');
  } else {
	  msg.classList.add('to');
  }

  parseCommands(data.message, userName)

  document.querySelector("#id_message_send_input").value = "";
  document.querySelector("#id_chat_item_container").appendChild(msg);
};