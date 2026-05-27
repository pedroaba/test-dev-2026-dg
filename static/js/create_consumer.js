async function fillAddressByCep(value) {
  const cep = value.replace(/\D/g, "");
  const loading = document.getElementById("cep_loading");
  const success = document.getElementById("cep_success");
  const error = document.getElementById("cep_error");
  const cityInput = document.getElementById("id_city");
  const stateInput = document.getElementById("id_state");

  if (cep.length !== 8) {
    loading.hidden = true;
    success.hidden = true;
    error.hidden = true;
    return;
  }

  loading.hidden = false;
  success.hidden = true;
  error.hidden = true;
  cityInput.value = "";
  stateInput.value = "";

  try {
    const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
    const data = await response.json();

    if (!response.ok || data.erro) {
      error.hidden = false;
      return;
    }

    cityInput.value = data.localidade;
    stateInput.value = data.uf;
    success.hidden = false;
  } catch {
    error.hidden = false;
  } finally {
    loading.hidden = true;
  }
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

function getFormPayload(form) {
  const payload = {};
  const formData = new FormData(form);

  formData.forEach(function (value, key) {
    if (key !== "csrfmiddlewaretoken") {
      payload[key] = value;
    }
  });

  return payload;
}

function renderApiErrors(errors) {
  const errorContainer = document.getElementById("api_form_errors");

  if (!errorContainer) {
    return;
  }

  const messages = [];

  Object.entries(errors).forEach(function ([field, fieldErrors]) {
    const normalizedErrors = Array.isArray(fieldErrors) ? fieldErrors : [fieldErrors];

    normalizedErrors.forEach(function (message) {
      messages.push(`${field}: ${message}`);
    });
  });

  errorContainer.innerHTML = messages.join("<br>");
  errorContainer.hidden = messages.length === 0;
}

async function submitConsumerApiForm(form) {
  const submitButton = form.querySelector("button[type='submit']");
  const originalLabel = submitButton?.textContent;

  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = "Salvando...";
  }

  renderApiErrors({});

  try {
    const response = await fetch(form.dataset.apiUrl, {
      method: form.dataset.apiMethod || "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify(getFormPayload(form)),
    });

    if (response.ok) {
      window.location.href = "/consumers/";
      return;
    }

    const errors = await response.json();
    renderApiErrors(errors);
  } catch {
    renderApiErrors({
      detail: "Nao foi possivel salvar o consumidor. Tente novamente.",
    });
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = originalLabel;
    }
  }
}

registerEventBeforeInput("id_document", allowDigitsOnly);
registerEventBeforeInput("id_zip_code", allowDigitsOnly);
registerEventBeforeInput("id_distributor_tax", allowDecimalInput);

const zipCodeInput = document.getElementById("id_zip_code");

if (zipCodeInput) {
  zipCodeInput.onblur = function () {
    fillAddressByCep(this.value);
  };
}

const consumerForm = document.querySelector("form[data-api-url]");

if (consumerForm) {
  consumerForm.addEventListener("submit", function (event) {
    event.preventDefault();
    submitConsumerApiForm(consumerForm);
  });
}
