const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.msg === "user_created") {
    const user = data.user;
    document.getElementById("display").innerText =
      `Nom : ${user.name}\nÂge : ${user.age}`;
    document.getElementById("userForm").style.display = "none";
    document.getElementById("userInfo").style.display = "block";
  } else if (data.msg === "status") {
    document.getElementById("status").innerText =
      data.contaminated ? "😷 Tu as le Covid !" : "✅ Tu es sain.";
  }
};

function sendUser() {
  const name = document.getElementById("name").value;
  const age = document.getElementById("age").value;
  ws.send(JSON.stringify({
    action: "create_user",
    name,
    age
  }));
}

document.getElementById("checkBtn").addEventListener("click", () => {
  ws.send(JSON.stringify({ action: "check_status" }));
});
