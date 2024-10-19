window.onload = function () {
  fetch("/contar_users")
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("usersCount").innerText = data.count;
    })
    .catch((error) => {
      console.error("Erro ao carregar contagem de usuários:", error);
    });

  fetch("/contar_itens")
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("itensCount").innerText = data.count;
    })
    .catch((error) => {
      console.error("Erro ao carregar contagem de itens:", error);
    });

  fetch("/contar_emprestimos_ativos")
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("emprestimosAtivosCount").innerText = data.count;
    })
    .catch((error) => {
      console.error("Erro ao carregar contagem de empréstimos ativos:", error);
    });

  fetch("/contar_emprestimos_atrasados")
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("emprestimosAtrasadosCount").innerText =
        data.count;
    })
    .catch((error) => {
      console.error(
        "Erro ao carregar contagem de empréstimos atrasados:",
        error
      );
    });
};
