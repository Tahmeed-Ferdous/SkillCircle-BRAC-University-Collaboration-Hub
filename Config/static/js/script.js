const body = document.querySelector('body'),
    sidebar = body.querySelector('.sidebar'),
    toggle = body.querySelector('.toggle'),
    modeSwitch = body.querySelector('.toggle-switch'),
    modeText = body.querySelector('.mode-text');

// Sidebar toggle functionality
toggle.addEventListener("click", () => {
    sidebar.classList.toggle('close');
});

// Mode switch functionality
modeSwitch.addEventListener("click", () => {
    body.classList.toggle('dark');

    // Update mode text
    if (body.classList.contains("dark")) {
        modeText.innerText = "Light Mode";
    } else {
        modeText.innerText = "Dark Mode";
    }
});


