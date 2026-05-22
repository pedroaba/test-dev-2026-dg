document.addEventListener('DOMContentLoaded', function() {
    const inputs = [
        document.getElementById('id_month_1'),
        document.getElementById('id_month_2'),
        document.getElementById('id_month_3'),
        document.getElementById('id_distributor_tax'),
    ]

    for (const input of inputs) {
        input.addEventListener('beforeinput', (event) => {
            const allowedChars = /^[0-9.,]$/;

            // Allows control actions like backspace, delete, paste, etc.
            if (event.inputType !== "insertText") {
              return;
            }
        
            if (!allowedChars.test(event.data)) {
              event.preventDefault();
              return;
            }

            const currentValue = input.value;
            const nextValue =
              currentValue.slice(0, input.selectionStart) +
              event.data +
              currentValue.slice(input.selectionEnd);

            // Prevents more than one decimal separator
            const separators = nextValue.match(/[.,]/g) ?? [];

            if (separators.length > 1) {
              event.preventDefault();
            }
        })
    }
})