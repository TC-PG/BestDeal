let search = document.querySelector("#search");
let button = document.querySelector("#btn");
let table = document.querySelector("#productTable");
let tbody = document.querySelector("tbody");
let loader = document.querySelector("#loader");

// web crawler query products
if(button){
   button.addEventListener("click", () => {
    loader.classList.add("loader");
    table.style.display = "block";
    let select = document.querySelector(".e-commerce")

    let child = tbody.lastElementChild;
     while (child) {
        tbody.removeChild(child);
        child = tbody.lastElementChild;
     }

    fetch(`/search?product=${search.value}&select=${select.value}`)
    .then(response => {
        if(response.status === 200){
            return response.json();
        }else{
            loader.classList.remove("loader");
            return response.json().then(error => {
                throw new Error(error["message"])
            });
        }
    })
    .then(resp => {
        console.log(resp)
       if(resp !== undefined){
           for(let r of resp){
            let tr = document.createElement("tr");
            let td1 = document.createElement("td");
            let img = document.createElement("img");
            img.setAttribute("src", r["src"]);
            td1.appendChild(img)
            tr.appendChild(td1);

            let td2 = document.createElement("td");
            let anchor = document.createElement("a");
            anchor.setAttribute("href", r["url"]);
            anchor.setAttribute("target", "_blank");
            anchor.innerHTML = r["name"];
            td2.appendChild(anchor)
            tr.appendChild(td2);

            let td3 = document.createElement("td");
            td3.innerHTML = r["price"];
            tr.appendChild(td3);

            let td4 = document.createElement("td");
            let saveBtn = document.createElement("button")
            saveBtn.innerText = "儲存";
            saveBtn.classList.add("btn", "btn-primary", "save");
            td4.appendChild(saveBtn);
            tr.appendChild(td4);

            tbody.appendChild(tr);
         }
       }
        loader.classList.remove("loader");
    })
    .catch(error => {
        alert(error);
        console.log(error);
    });
});

}

// save item to favorite
$("table").on("click", ".save", (e) =>{
    let btn = e.currentTarget;
    let btnParent = btn.parentNode;
    //price
    let priceTd = btnParent.previousSibling;
    let price = priceTd.innerText;
    //description
    let descriptionTd = priceTd.previousSibling;
    let descriptionNode = descriptionTd.firstChild;
    let url = descriptionNode.getAttribute("href");
    let productName = descriptionNode.innerText;
    //image
    let imgNode = descriptionTd.previousSibling.firstChild;
    let src = imgNode.getAttribute("src");

    console.log(src)
    console.log(url)
    console.log(productName)
    console.log(price)

    favorite={
        "productName": productName,
        "src": src,
        "url":url,
        "price":price
    }

    fetch("/save",
        {
          method: 'POST',
          body: JSON.stringify(favorite),
          headers: new Headers({
            'Content-Type': 'application/json'
          })
        }
    ).then(response => {
        if (response.status === 200){
            return response.json();
        }else{
            return response.json().then(error => {
                throw new Error(error["message"]);
            })
        }
    })
    .then(response => alert(`${response['message']}`))
    .catch(error => {
        alert(error);
    });

});

//delete item from favorite
$("#favoriteTable").on("click", ".deleteBtn", (e) => {
    let deleteBtn = e.currentTarget;
    let td = deleteBtn.parentNode;

    let tr = td.parentNode;
    let firstChild = tr.firstChild;
    while(firstChild != null && firstChild.nodeType == 3){ // skip TextNodes
        firstChild = firstChild.nextSibling;
    }
    let id = firstChild.innerText;

    fetch(`/delete`, {
        method: "post",
        body: JSON.stringify(id),
        headers: new Headers(
            {
                'Content-Type': 'application/json'
            })
    })
    .then(response => {
        if (response.status === 200) {
           return response.json();
        }else{
            return response.json().then(error => {
                throw new Error(error["message"]);
            });
        }
    })
    .then(json => {
        tr.remove();
        alert(`${json["message"]}`);
    })
    .catch(err => {
        alert(err);
        console.log(err);
        window.location.href = "/";
    });
});
