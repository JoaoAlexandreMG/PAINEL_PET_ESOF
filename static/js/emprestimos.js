fetch("/get_emprestimos_ativos")
  .then((response) => response.json())
  .then((data) => {
    let html = "";
    data.forEach((item) => {
      html += `<tr>
    <td>${item.usuario_nome}</td>
    <td>${item.item_nome}</td>
    <td>${item.item_qntd}</td>
    <td>${item.data_emprestimo}</td>
    <td>${item.data_prevista_devolucao}</td>
    </tr>`;
    });
    document.getElementById("ActiveEmprestimos").innerHTML = html;
  })
  .catch((error) =>
    console.error("Erro ao carregar emprestimos ativos:", error)
  );

fetch("/get_emprestimos_atrasados")
  .then((response) => response.json())
  .then((data) => {
    let html = "";
    data.forEach((item) => {
      console.log(item);
      html += `<tr>
    <td>${item.usuario_nome}</td>
    <td>${item.item_nome}</td>
    <td>${item.item_qntd}</td>
    <td>${item.data_emprestimo}</td>
    <td>${item.dias_atraso}</td>
    </tr>`;
    });
    document.getElementById("EmprestimosAtrasados").innerHTML = html;
  })
  .catch((error) =>
    console.error("Erro ao carregar emprestimos ativos:", error)
  );
fetch("/get_historico_emprestimos")
  .then((response) => response.json())
  .then((data) => {
    let html = "";
    data.forEach((item) => {
      console.log(item);
      html += `<tr>
    <td>${item.usuario_nome}</td>
    <td>${item.item_nome}</td>
    <td>${item.item_qntd}</td>
    <td>${item.data_emprestimo}</td>
    <td>${item.data_devolucao}</td>
    </tr>`;
    });
    document.getElementById("HistoricoEmprestimos").innerHTML = html;
  })
  .catch((error) =>
    console.error("Erro ao carregar emprestimos ativos:", error)
  );