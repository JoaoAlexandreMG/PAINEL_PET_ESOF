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
function closePopup(id) {
  document.getElementById(id).style.display = "none";
}
function openEditItemPopup(itemId, itemName, itemQuantity, itemLocation) {
  document.getElementById("editItemId").value = itemId;
  document.getElementById("editItemName").value = itemName;
  document.getElementById("editItemQuantity").value = itemQuantity;
  document.getElementById("editItemLocation").value = itemLocation;
  document.getElementById("editItemPopup").style.display = "flex";
}
document.getElementById("itemSearch").addEventListener("input", searchItems);

window.onload = searchItems;

// Submeter Edição de Item
document
  .getElementById("editItemForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const itemId = document.getElementById("editItemId").value;
    const itemName = document.getElementById("editItemName").value;
    const itemQuantity = document.getElementById("editItemQuantity").value;
    const itemLocation = document.getElementById("editItemLocation").value;

    fetch("/edit_item", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `item_id=${itemId}&item_name=${itemName}&item_quantity=${itemQuantity}&item_location=${itemLocation}`,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          closePopup("editItemPopup");
          searchItems();
        } else {
          alert("Erro ao editar o item: " + data.message);
        }
      })
      .catch((error) => {
        alert("Erro ao editar o item: " + error);
      });
  });
