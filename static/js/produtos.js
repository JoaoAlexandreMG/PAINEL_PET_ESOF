function searchItems() {
  const search = document.getElementById("itemSearch").value.toLowerCase(); // Pega o valor da barra de pesquisa e converte para minúsculas

  fetch(`/get_items?search=${search}`) // Passa o termo de pesquisa para o backend
    .then((response) => response.json())
    .then((items) => {
      const itemResults = document.getElementById("itemResults");

      // Limpa os resultados anteriores
      itemResults.innerHTML = "";

      // Filtrar itens com base no termo de pesquisa
      const filteredItems = items.filter((item) =>
        item[1].toLowerCase().includes(search)
      );

      // Ordena os itens por ID em ordem crescente
      filteredItems.sort((a, b) => a[0] - b[0]);

      // Verifica se há itens filtrados
      if (filteredItems.length > 0) {
        filteredItems.forEach((item) => {
          const row = `
            <tr>
              <th >${item[0]}</th>
              <td>${item[1]}</td>
              <td style="text-align: center;">${item[2]}</td>
              <td style="text-align: center;">${item[3]}</td>
              <td style="text-align: center;">
                <button class="btn btn-primary btn-sm" onclick="openEditItemPopup(${item[0]}, '${item[1]}', ${item[3]}, '${item[2]}')">Editar</button>
              </td>
            </tr>
          `;
          itemResults.insertAdjacentHTML("beforeend", row);
        });
      } else {
        itemResults.innerHTML = `<tr><td colspan="5">Nenhum item encontrado.</td></tr>`;
      }
    })
    .catch((error) => {
      console.error("Erro ao carregar itens:", error);
    });
}
document.getElementById("itemSearch").addEventListener("input", searchItems);

window.onload = searchItems;
