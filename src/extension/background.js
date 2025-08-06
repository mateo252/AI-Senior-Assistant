// In order to manage user activity in the browser, one special endpoint was prepared.
API_URL = "http://127.0.0.1:5000/browser/activity"

// One function that sends data to fronted ('content.js') as an immediate response from the backend
function sendDataToContent(jsonData){
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => chrome.tabs.sendMessage(tabs[0].id, jsonData));
}

// --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- //

// Listener of incoming messages from the frontend ('content.js')
// Data are sent immediately to the backend, then returned and immediately sent back to the frontend as a message to be displayed
chrome.runtime.onMessage.addListener((message) => {
    fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(message)
    })
    .then((res) => res.json().then((data) => sendDataToContent(data)))
    .catch((error) => console.error("Error sending URL after starting download:", error));
});

// --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- //

// File download activity is divided into the stages: start and complete (more options may be added in the future)
// Check if the download has started and send the data to the backend
chrome.downloads.onCreated.addListener((downloadItem) => {
    fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            action: "downloadStart",
            isSafe: downloadItem.danger,
            fileName: downloadItem.filename,
            referrer: downloadItem.referrer,
            url: downloadItem.url
        })
    })
    .then((res) => res.json().then((data) => sendDataToContent(data)))
    .catch((error) => console.error("Error sending URL after starting download:", error));
});

// Second function checks if the download is completed and send the data to the backend
chrome.downloads.onChanged.addListener((downloadItem) => {
    // Get only for status 'complete'
    if (downloadItem.state && downloadItem.state.current === "complete"){
        // Get first downloaded file
        chrome.downloads.search({ id: downloadItem.id }, (item) => {
            const file = item[0];
            fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    action: "downloadEnd",
                    isSafe: file.danger,
                    fileName: file.filename,
                    referrer: file.referrer,
                    url: file.url
                })
            })
            .then((res) => res.json().then((data) => sendDataToContent(data)))
            .catch((error) => console.error("Error sending URL after download completes:", error));
        });
    }
});

// --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- //