// main.js - Define reusable functions or helpers for the application

/**
 * Utility function to display an error message.
 * @param {string} message - The message to display.
 * @param {string} elementId - The ID of the element to display the message in.
 */
function displayError(message, elementId = 'error-message') {
    const errorMessageElement = document.getElementById(elementId);
    if (errorMessageElement) {
        errorMessageElement.innerText = message;
        errorMessageElement.style.display = 'block'; // Show the error message
    } else {
        console.warn(`Element with ID ${elementId} not found.`);
    }
}

/**
 * Utility function to reset a button to its default state.
 * @param {HTMLElement} buttonElement - The button to reset.
 * @param {string} defaultText - The default text to display on the button.
 */
function resetButton(buttonElement, defaultText = 'Complete Order') {
    buttonElement.disabled = false; // Enable the button
    buttonElement.innerText = defaultText; // Reset button text
}
