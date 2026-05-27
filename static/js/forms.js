function allowDecimalInput(event) {
  if (event.inputType !== "insertText") {
    return;
  }

  const nextValue =
    event.target.value.slice(0, event.target.selectionStart) +
    event.data +
    event.target.value.slice(event.target.selectionEnd);

  if (
    !/^[0-9.,]$/.test(event.data) ||
    (nextValue.match(/[.,]/g) || []).length > 1
  ) {
    event.preventDefault();
  }
}

function allowDigitsOnly(event) {
  if (event.inputType === "insertText" && !/^[0-9]$/.test(event.data)) {
    event.preventDefault();
  }
}

function registerEventBeforeInput(id, handler) {
  const element = document.getElementById(id);

  if (element) {
    element.onbeforeinput = handler;
  }
}
