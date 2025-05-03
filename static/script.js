document.getElementById("itemForm").addEventListener("submit", function(event) {
    event.preventDefault()
    // Get the item name from the textarea
    const itemName = document.getElementById("itemInput").value.trim();
});


function addEntry(name, expiry){
    // If input is not empty, add the item to the list
    
    const date = new Date(expiry);

    // Format the date into the desired format
    const options = {
        weekday: "long", // Full name of the day
        year: "numeric", // Full year
        month: "long", // Full month name
        day: "numeric" // Numeric day of the month
    };
    
    // Convert the date into the desired format
    const formattedDate = date.toLocaleDateString("en-US", options);
    
    console.log(formattedDate);


    const table = document.getElementById("item-list");
    // Create a new row
    const newRow = table.insertRow();       
    const nameCell = newRow.insertCell();
    const expiryCell = newRow.insertCell();
    nameCell.textContent = name;
    expiryCell.textContent = formattedDate; 
    document.getElementById("itemInput").value = "";
}

var addBtn = document.getElementById("submitBtn")

addBtn.addEventListener('click', function(){
    const itemData = {
        name: document.getElementById('itemInput').value
    }; 
    fetch('/addItem', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ itemData }), // Correctly format the JSON payload
    })
    .then(response => response.json())
    .then(data => {
        // addEntry(data, 2); 
        
        console.log('Item added:', data.item.expiry);
        console.log('Item Name:', data.item.name);
        addEntry(data.item.name, data.item.expiry); 
    })
    .catch(error => {
        console.error('Error:', error);
    });
    
})


var emailBtn = document.getElementById("emailBtn"); 
emailBtn.addEventListener('click', function(){
    fetch('/emailList', {
        method: 'GET', 
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())

});


var clearBtn = document.getElementById("clearBtn"); 
clearBtn.addEventListener('click', function(){
    fetch('/clearList', {
        method: 'GET', 
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    
})
