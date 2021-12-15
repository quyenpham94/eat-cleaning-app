

// $(function(){
//     $("food-suggestion").on("click", function(event){
//         event.preventDefault();
//         new_ul = document.createElement("ul");
//         ("today-meal").append(new_ul)
//         let food = $("card-text").val();
//         console.log(food);
//         $(new_ul).append(food);
//     })
// })

const input = document.querySelector("#card-text")
const food = document.querySelector("#food-list")
const form = document.querySelector("#add-food")

form.addEventListener("click", function(event){
    event.preventDefault();
    console.log(input.value);
    const new_ul = document.createElement("ul");
    const new_food = input.value;
    new_ul.appendChild(new_food);
    food.appendChild(new_ul);
})
