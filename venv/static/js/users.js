window.onload = searchUsers;
function closePopup(id) {
  document.getElementById(id).style.display = "none";
}
function showPopup(id) {
  document.getElementById(id).style.display = "flex";
}

function ocultarCPF(cpf) {
  cpf = cpf.replace(/\D/g, "");
  if (cpf.length === 11) {
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.***-**");
  } else {
    return cpf;
  }
}

function CPF(v) {
  v = v.replace(/\D/g, ""); //Remove tudo o que não é dígito
  v = v.replace(/(\d{3})(\d)/, "$1.$2"); //Coloca um ponto entre o terceiro e o quarto dígitos
  v = v.replace(/(\d{3})(\d)/, "$1.$2"); //Coloca um ponto entre o terceiro e o quarto dígitos
  //de novo (para o segundo bloco de números)
  v = v.replace(/(\d{3})(\d{1,2})$/, "$1-$2"); //Coloca um hífen entre o terceiro e o quarto dígitos
  return v;
}

function phoneMask(value) {
  if (!value) return "";
  value = value.replace(/\D/g, "");
  value = value.replace(/(\d{2})(\d)/, "($1) $2");
  value = value.replace(/(\d)(\d{4})$/, "$1-$2");
  return value;
}

function searchUsers() {
  const search = document.getElementById("userSearch").value;

  fetch(`/get_users?search=${search}`)
    .then((response) => response.json())
    .then((users) => {
      // Ordenar usuários por ID (menor para maior)
      users.sort((a, b) => a[0] - b[0]);

      const userResults = document.getElementById("userResults");
      let html = "";

      users.forEach((user) => {
        html += `
        <tr>
        
        <th>${user[0]}</th>
        <td>${user[2]}</td>
        <td style="text-align: center;">${ocultarCPF(user[1])}</td>
        <td style="text-align: center;"><button onclick="openEditUserPopup(${
          user[0]
        }, '${user[2]}', '${user[1]}', '${user[3]}', '${user[4]}', '${
          user[5]
        }')" class="btn btn-primary btn-sm">Editar</button></td>
        <td><button onclick="deleteUser(${
          user[0]
        })" class="btn btn-danger btn-sm">Excluir</button></td>
        <tr>
        `;
      });
      userResults.innerHTML = html;
    })
    .catch((error) => {
      console.error("Erro ao carregar usuários:", error);
    });
}
function addUser() {
  const cpf = document.getElementById("cpf").value.replace(/\D+/g, "");
  const nome = document.getElementById("nome").value;
  const curso = document.getElementById("curso").value;
  const telefone = document
    .getElementById("telefone")
    .value.replace(/\D+/g, "");
  const email = document.getElementById("email").value;
  if (cpf === "" || nome === "" || curso === "" || email === "") {
    showCustomAlert(
      "Por favor, preencha todos os campos obrigatórios.",
      "warning"
    );
    return;
  }

  fetch("/add_user", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      cpf: cpf,
      nome: nome,
      curso: curso,
      email: email,
      telefone: telefone,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "error") {
        showCustomAlert(data.message, "error");
        closePopup("addUserPopup");
        document.getElementById("userSearch").value = cpf;
        searchUsers();
      } else if (data.status === "success") {
        showCustomAlert("Usuário adicionado com sucesso!", "success");
        closePopup("addUserPopup");
        searchUsers();
      }
      document.getElementById("nome").value = "";
      document.getElementById("cpf").value = "";
      document.getElementById("telefone").value = "";
      document.getElementById("email").value = "";
      document.getElementById("curso").value = "";
    });
}
function deleteUser(userId) {
  if (confirm("Tem certeza que deseja deletar o usuário?")) {
    fetch("/delete_user", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        user_id: userId,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          showCustomAlert("Usuário deletado com sucesso!", "success");
          searchUsers();
        } else {
          showCustomAlert(data.message, "error");
        }
      });
  }
}
document.getElementById("userSearch").addEventListener("input", searchUsers);

function openEditUserPopup(userId, nome, cpf, telefone, curso, email) {
  document.getElementById("editUserPopup").style.display = "flex";
  document.getElementById("editUserId").value = userId;
  document.getElementById("editUserCPF").value = CPF(cpf);
  document.getElementById("editUserName").value = nome;
  document.getElementById("editUserCourse").value = curso;
  document.getElementById("editUserEmail").value = email;
  document.getElementById("editUserPhone").value = phoneMask(telefone);
}
// Submeter Edição de Usuário
document
  .getElementById("editUserForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const userId = document.getElementById("editUserId").value;
    const cpf = document.getElementById("editUserCPF").value;
    const nome = document.getElementById("editUserName").value;
    const curso = document.getElementById("editUserCourse").value;
    const email = document.getElementById("editUserEmail").value;
    const telefone = document.getElementById("editUserPhone").value;

    fetch("/edit_user", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        user_id: userId,
        cpf: cpf,
        nome: nome,
        curso: curso,
        email: email,
        telefone: telefone,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          closePopup("editUserPopup");
          searchUsers(); // Atualiza a lista de usuários após a edição
        } else {
          showCustomAlert("Erro ao editar o usuário: " + data.message, "error");
        }
      })
      .catch((error) => {
        showCustomAlert("Erro ao editar o usuário: " + error, "error");
      });
  });

document
  .getElementById("editUserCPF")
  .addEventListener("input", function (event) {
    event.target.value = CPF(event.target.value);
  });
document.getElementById("cpf").addEventListener("input", function (event) {
  event.target.value = CPF(event.target.value);
});
document
  .getElementById("editUserPhone")
  .addEventListener("input", function (event) {
    event.target.value = phoneMask(event.target.value);
  });
document.getElementById("telefone").addEventListener("input", function (event) {
  event.target.value = phoneMask(event.target.value);
});
