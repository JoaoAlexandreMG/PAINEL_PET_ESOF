function ocultarCPF(cpf) {
  cpf = cpf.replace(/\D/g, "");
  if (cpf.length === 11) {
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.***-**");
  } else {
    return cpf;
  }
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
        <td style="text-align: center;"><button class="btn btn-primary btn-sm">Editar</button></td>
        <tr>
        `;
      });
      userResults.innerHTML = html;
    })
    .catch((error) => {
      console.error("Erro ao carregar usuários:", error);
    });
}

document.getElementById("userSearch").addEventListener("input", searchUsers);

window.onload = searchUsers;
