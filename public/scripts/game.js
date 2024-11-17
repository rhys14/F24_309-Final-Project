
async function getInfo() {
    request = new Request("/images", {
        method: "GET",
        headers: {
            'Content-Type': "application/json"
        }
    });

    response = await fetch(request);
     // Check if the response status is OK (status code 200-299)
     if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    const newImg = document.createElement("img")
    newImg.src = "gameImages/" +data["file"]
    const div = document.getElementById("images")
    if(div.childElementCount > 0) {
        div.removeChild(div.firstChild)
    }
    div.appendChild(newImg)
}

document.getElementById("submit").addEventListener("click", function(event){
    getInfo()
});