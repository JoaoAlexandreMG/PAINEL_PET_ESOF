// Fechar o modal quando o usuário clicar no "x"
document.querySelector(".close-btn-alert").onclick = function () {
  document.getElementById("customAlert").style.display = "none";
};

// Fechar o modal quando o usuário clicar fora do modal
window.onclick = function (event) {
  const modal = document.getElementById("customAlert");
  if (event.target === modal) {
    modal.style.display = "none";
  }
};

function showCustomAlert(message, type) {
  Swal.fire({
    title: "Atenção!",
    text: message,
    icon: type, // Você pode usar 'success', 'error', 'info', 'warning', etc.
    confirmButtonText: "Ok",
    confirmButtonColor: "#007bff", // Cor do botão
  });
}
function showConfirmDialog(message) {
  return new Promise((resolve) => {
    Swal.fire({
      title: "Atenção!",
      text: message,
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Sim",
      cancelButtonText: "Cancelar",
      confirmButtonColor: "#007bff", // Cor do botão
      cancelButtonColor: "#dc3545", // Cor do botão
    }).then((result) => {
      resolve(result.value);
    });
  });
}
