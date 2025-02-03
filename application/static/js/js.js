const predefinedData =[
    {
        id :"1",
        network_operator : "GLO",
    },
    {
        id :"2",
        network_operator : "MTN",
    },
    {
        id :"3",
        network_operator : "AIRTEL",
    },
    {
        id :"4",
        network_operator : "9MOBILE",
    },
];
function initializeData() {
    if (!localStorage.getItem("data")) {
        localStorage.setItem("data", JSON.stringify(predefinedData));
    }
}
function getData() {
    const data = localStorage.getItem("data");
    return data ? JSON.parse(data) : [];
}
function renderData() {
    const dataContainer = document.querySelector(".container");
    dataContainer.innerHTML = "";

    const data = getData();
    data.forEach((data) => {
        const dataItem = document.createElement("div");
        dataItem.className = "data";
        
    });
}