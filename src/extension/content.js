// Data are send to 'background.js'
// 'background.js' communicates with backend
// 'content.js' <---> 'background.js' <---> Flask

// In the browser, LLM model communicates with the user via a pop-up window in the lower left corner of the page
// Data received from 'background.js' are displayed in a new <div></div> tag on the page
// New <div> tag is prepared on backend in 'templates' folder
// The only task in whole 'content.js' after receiving data is to display it
chrome.runtime.onMessage.addListener((message) => {
    
    if (message.action === "notification"){
        document.querySelector(".new-ai-extension-container")?.remove(); // Delete the existing <div> and create a new one

        const newContainer = document.createElement("div");
        newContainer.className = "new-ai-extension-container";

        newContainer.innerHTML = message.message;
        document.body.appendChild(newContainer);

        const notifContainer = document.querySelector(".new-ai-extension-container");
        notifContainer.addEventListener("click", () => notifContainer.remove());
    }
});

// --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- //

// Checks the URL of the page visited by the user
// If the website has been opened by the link <a href=...></a>
// All the logic for notification management is prepared on the backend side and the decision also depends on the chosen LLM model
// The frontend sends all the data, then the backend selects, analyzes and makes decisions
document.addEventListener("click", (e) => {

    const link = e.target.closest("a[href]");
    const description = document.querySelector('meta[name="description"]');

    chrome.runtime.sendMessage({
        action: "websiteUrl",
        clicked: true,
        link: link?link.getAttribute("href"):"",
        websiteTitle: document.title,
        websiteDescription: description?description.getAttribute("content"):"",
        baseUrl: window.location.hostname,
        fullUrl: window.location.href
    });
});

// --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- //

// https://developer.mozilla.org/en-US/docs/Web/API/Permissions_API
// Check if there has been a change in permission settings by the user on the visited website
// 4 basic permissions of the site - 'camera', 'microphone', 'geolocation', 'notifications'
// You can easily add others that are supported by the API

async function checkPermission(permissionName) {
    try {
        const permissionStatus = await navigator.permissions.query({ name: permissionName });
        const description = document.querySelector('meta[name="description"]');
        permissionStatus.onchange = () => {
            chrome.runtime.sendMessage({
                action: "websitePermissionChange",
                permission: permissionStatus.state,
                websiteTitle: document.title,
                websiteDescription: description?description.getAttribute("content"):"",
                baseUrl: window.location.hostname,
                fullUrl: window.location.href
            });
        };
    } catch (error) {
        console.error(`Error while checking permission: ${permissionName}:`, error);
    }
}
[
    "camera",
    "microphone",
    "geolocation",
    "notifications"
].forEach((permissionName) => { checkPermission(permissionName); });

// --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- //

