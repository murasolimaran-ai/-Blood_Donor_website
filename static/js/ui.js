// ============================================================
// ui.js - Blood Donor Finder
// This file handles SMALL UI effects only.
//
// IMPORTANT RULE: No database logic here!
// All database work is done in Python (model.py).
// JavaScript is only used for:
//   1. Showing a popup message (toast notification)
//   2. Toggle donor availability button (sends request to Python)
//   3. Register form loading state
//   4. Auto-hide flash messages
// ============================================================


// ============================================================
// FUNCTION: showToast(message)
// Creates a small popup notification at the bottom-right.
// It disappears automatically after 3 seconds.
//
// How to use: showToast('Donor updated!')
// ============================================================
function showToast(message) {
    // Create a new div element
    var popup = document.createElement('div');

    // Give it the CSS class for styling
    popup.className = 'toast-popup';

    // Set the message text
    popup.textContent = message;

    // Add it to the page
    document.body.appendChild(popup);

    // Remove it after 3 seconds (3000 milliseconds)
    setTimeout(function() {
        popup.remove();
    }, 3000);
}


// ============================================================
// FUNCTION: toggleDonor(donorId, button)
// Called when admin clicks Activate/Deactivate button.
//
// What happens:
//   1. Sends a POST request to /admin/toggle/ID (in Python)
//   2. Python flips the value in the database
//   3. Python sends back JSON with the new status
//   4. We update the button and status label on the page
//
// Parameters:
//   donorId - the ID number of the donor
//   button  - the HTML button that was clicked
// ============================================================
async function toggleDonor(donorId, button) {
    // Disable button so user can't click twice
    button.disabled = true;
    button.textContent = '...';

    try {
        // Send POST request to Flask route in app.py
        var response = await fetch('/admin/toggle/' + donorId, {
            method: 'POST'
        });

        // Convert the response to a JavaScript object
        var result = await response.json();

        // Check if the operation was successful
        if (result.status !== 'ok') {
            showToast('Something went wrong. Please try again.');
            button.disabled = false;
            return;
        }

        // Update the STATUS LABEL on the page
        var statusLabel = document.getElementById('status-' + donorId);
        var tableRow    = document.getElementById('row-'    + donorId);

        if (result.available === 1) {
            // Donor is now AVAILABLE
            statusLabel.textContent = 'Available';
            statusLabel.className   = 'status-label status-green';
            button.textContent      = 'Deactivate';
            tableRow.classList.remove('faded-row');
            showToast('Donor is now marked as Available.');
        } else {
            // Donor is now UNAVAILABLE
            statusLabel.textContent = 'Unavailable';
            statusLabel.className   = 'status-label status-gray';
            button.textContent      = 'Activate';
            tableRow.classList.add('faded-row');
            showToast('Donor is now marked as Unavailable.');
        }

    } catch (error) {
        // If something goes wrong with the network
        showToast('Network error. Please try again.');
    }

    // Re-enable the button
    button.disabled = false;
}


// ============================================================
// REGISTER FORM: Show loading state when submitted
// Prevents double-clicking the submit button
// ============================================================
var registerForm = document.getElementById('register-form');

if (registerForm) {
    registerForm.addEventListener('submit', function() {
        var submitButton = document.getElementById('submit-btn');
        if (submitButton) {
            submitButton.disabled     = true;
            submitButton.textContent  = 'Registering...';
        }
    });
}


// ============================================================
// AUTO-HIDE FLASH MESSAGES
// The success/error messages at the top disappear after 4.5s
// ============================================================
var allMessages = document.querySelectorAll('.message');

allMessages.forEach(function(messageElement) {
    setTimeout(function() {
        // Fade out smoothly
        messageElement.style.transition = 'opacity 0.4s';
        messageElement.style.opacity    = '0';

        // Remove from page after fade finishes
        setTimeout(function() {
            messageElement.remove();
        }, 400);
    }, 4500);
});