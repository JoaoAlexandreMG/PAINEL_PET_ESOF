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
    <td><button id="devolver_button" onclick="returnItem(${item.emprestimo_id})">Devolver</button></td>
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
function returnItem(emprestimo_id) {
  fetch("/return_item", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      emprestimo_id: emprestimo_id,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        alert("Devolução feita com sucesso!");
        location.reload();
      } else {
        alert(data.message);
      }
    });
}
let itens = [];
function borrowItemList() {
  const userId = document.getElementById("userSelect").value;
  const item_id = document.getElementById("itemSelect").value;
  const quantity = document.getElementById("itemQuantityInput").value;
  const content = document.getElementById("lista_de_itens");
  for (let item of itens) {
    if (item[0] === item_id) {
      alert("Item já adicionado à lista!");
      return;
    }
  }
  fetch(
    `/get_item_qtd?userId=${userId}&item_id=${item_id}&quantity=${quantity}`
  )
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        itens.push([item_id, quantity]);
        content.style.display = "flex";
        fetch(`/get_item?item_id=${item_id}`)
          .then((response) => response.json())
          .then((data) => {
            content.innerHTML += `<li>${quantity} x ${data.nome}<button class="btn btn-primary btn-sm" onClick="deleteItemInList(${item_id})" id="deleteItemList"> 🗑️</button></li>`;
          })
          .catch((error) => {
            console.error("Erro ao adicionar item:", error);
          });
      } else {
        alert(data.message);
      }
    })
    .catch((error) => {
      console.error("Erro ao adicionar item:", error);
    });
}
function deleteItemInList(item_id) {
  // Converte o item_id para um número
  const itemIdNumber = Number(item_id);

  // Encontra o índice do item na lista 'itens'
  const itemIndex = itens.findIndex((item) => Number(item[0]) === itemIdNumber);

  // Remove o item da lista 'itens'
  itens.splice(itemIndex, 1);

  // Atualiza a lista na interface do usuário
  const itemList = document.getElementById("lista_de_itens");
  itemList.innerHTML = ""; // Limpa a lista atual

  // Reconstroi a lista atualizada buscando os nomes dos itens
  itens.forEach((item) => {
    const item_id = item[0];
    const quantity = item[1];

    // Busca o nome do item antes de adicioná-lo à lista
    fetch(`/get_item?item_id=${item_id}`)
      .then((response) => response.json())
      .then((data) => {
        // Adiciona o item com o nome correto na lista
        itemList.innerHTML += `<li>${quantity} x ${data.nome}<button class="btn btn-primary btn-sm" onClick="deleteItemInList(${item_id})" id="deleteItemList"> 🗑️</button></li>`;
      })
      .catch((error) => {
        console.error("Erro ao buscar o item:", error);
      });
  });
}
function limparLista() {
  itens = [];
  document.getElementById("lista_de_itens").innerHTML = "";
}
function borrowItem() {
  if (!itens || itens.length === 0) {
    alert("Não há itens na lista!");
    return;
  }
  const userId = document.getElementById("userSelect").value;
  const DevolucaoPrevista = document.getElementById(
    "DevolucaoPrevistaInput"
  ).value;

  // Verificar se todos os campos foram preenchidos
  if (!DevolucaoPrevista) {
    alert("Por favor, coloque a data prevista para devolução.");
    return;
  }

  fetch("/borrow_item", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      user_id: userId,
      items_id: itens,
      DevolucaoPrevista: DevolucaoPrevista,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        alert("Item emprestado com sucesso!");
        closePopup("borrowItemPopup");
        const loanDate = new Date().toLocaleDateString();
        const expectedReturnDate = new Date(
          DevolucaoPrevista
        ).toLocaleDateString();
        // generateLoanPDF(userId, itens, loanDate, expectedReturnDate);
        location.reload();

        itens = [];
      } else {
        alert(data.message);
      }
    })
    .catch((error) => {
      console.error("Erro ao emprestar item:", error);
    });
}

function closePopup(id) {
  document.getElementById(id).style.display = "none";
}
function showBorrowItemPopup() {
  fetch("/get_items")
    .then((response) => response.json())
    .then((items) => {
      const itemSelect = document.getElementById("itemSelect");
      itemSelect.innerHTML = items
        .map(
          (item) =>
            `<option value="${item[0]}">${item[1]} (ID: ${item[0]})</option>`
        )
        .join("");

      // Resetar o valor da data prevista de devolução
      document.getElementById("borrowItemPopup").style.display = "flex";
      document.getElementById("DevolucaoPrevistaInput").value = "";
      document.getElementById("searchItemInput").value = "";
      GetEstoque();
      GetUsers();
    });
}
function searchItemsInPopup() {
  const search = document.getElementById("searchItemInput").value.toLowerCase();
  const itemSelect = document.getElementById("itemSelect");

  fetch(`/get_items?search=${search}`)
    .then((response) => response.json())
    .then((items) => {
      // Gerar o HTML das opções ordenadas
      itemSelect.innerHTML = items
        .map(
          (item) =>
            `<option value="${item[0]}">${item[1]} (ID: ${item[0]})</option>`
        )
        .join("");
    });
}
document.getElementById("itemSelect").addEventListener("change", function () {
  GetEstoque();
});
function GetEstoque() {
  const content = document.getElementById("itemQuantityInput"); // Pegando o elemento da lista de opções
  const itemId = document.getElementById("itemSelect").value; // Pegando o ID do item selecionado

  let html = ""; // Variável para armazenar o HTML das opções
  if (itemId) {
    // Fazendo a requisição para buscar o estoque do item
    fetch(`/get_estoque?item_id=${itemId}`)
      .then((response) => response.json())
      .then((data) => {
        // Iterar de 1 até o valor de 'data', criando opções
        for (let i = 1; i <= data; i++) {
          html += `<option>${i}</option>`;
        }
        // Atualizando o conteúdo do select com as novas opções
        content.innerHTML = html;
      })
      .catch((error) => {
        console.error("Erro ao carregar estoque:", error);
      });
  }
}
function GetUsers() {
  const content = document.getElementById("userSelect"); // Pegando o elemento da lista de opções

  let html = ""; // Variável para armazenar o HTML das opções

  // Fazendo a requisição para buscar os usuários
  fetch(`/get_users`)
    .then((response) => response.json())
    .then((users) => {
      // Iterar sobre a lista de usuários, criando opções
      users.forEach((user) => {
        html += `<option value="${user[0]}">${user[2]}</option>`;
      });

      // Atualizando o conteúdo do select com as novas opções
      content.innerHTML = html;
    })
    .catch((error) => {
      console.error("Erro ao carregar usuários:", error);
    });
}
