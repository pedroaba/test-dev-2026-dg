registerEventBeforeInput("id_month_1", allowDecimalInput);
registerEventBeforeInput("id_month_2", allowDecimalInput);
registerEventBeforeInput("id_month_3", allowDecimalInput);
registerEventBeforeInput("id_distributor_tax", allowDecimalInput);

const excelFileInput = document.getElementById("excel_file");
const consumerDeleteModal = document.getElementById("consumer_delete_modal");
const consumerDeleteCancel = consumerDeleteModal?.querySelector("[data-modal-cancel]");
const consumerDeleteConfirm = consumerDeleteModal?.querySelector("[data-modal-confirm]");
let pendingDeleteButton = null;

if (excelFileInput) {
  excelFileInput.onchange = function () {
    this.form.submit();
  };
}

function getCookie(name) {
  const cookies = document.cookie ? document.cookie.split(";") : [];

  for (const cookie of cookies) {
    const [cookieName, ...cookieValueParts] = cookie.trim().split("=");

    if (cookieName === name) {
      return decodeURIComponent(cookieValueParts.join("="));
    }
  }

  return "";
}

async function deleteConsumer(button) {
  button.disabled = true;
  button.textContent = "Excluindo...";

  try {
    const response = await fetch(button.dataset.url, {
      method: button.dataset.method || "DELETE",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    });

    if (!response.ok) {
      throw new Error("Erro ao excluir consumidor.");
    }

    window.location.reload();
  } catch {
    button.disabled = false;
    button.textContent = "Excluir";
    window.alert("Nao foi possivel excluir o consumidor. Tente novamente.");
  }
}

function openDeleteModal(button) {
  pendingDeleteButton = button;

  if (!consumerDeleteModal) {
    deleteConsumer(button);
    return;
  }

  consumerDeleteModal.hidden = false;
  consumerDeleteConfirm?.focus();
}

function closeDeleteModal() {
  if (consumerDeleteModal) {
    consumerDeleteModal.hidden = true;
  }

  pendingDeleteButton = null;
}

consumerDeleteCancel?.addEventListener("click", closeDeleteModal);

consumerDeleteModal?.addEventListener("click", function (event) {
  if (event.target === consumerDeleteModal) {
    closeDeleteModal();
  }
});

consumerDeleteConfirm?.addEventListener("click", function () {
  if (pendingDeleteButton) {
    const button = pendingDeleteButton;
    closeDeleteModal();
    deleteConsumer(button);
  }
});

document.addEventListener("keydown", function (event) {
  if (event.key === "Escape" && consumerDeleteModal && !consumerDeleteModal.hidden) {
    closeDeleteModal();
  }
});

document.addEventListener("click", function (event) {
  const actionButton = event.target.closest("[data-action]");

  if (!actionButton) {
    return;
  }

  if (actionButton.dataset.action === "consumer_delete") {
    openDeleteModal(actionButton);
  }

  if (actionButton.dataset.action === "consumer_update" && actionButton.dataset.page) {
    window.location.href = actionButton.dataset.page;
  }
});
