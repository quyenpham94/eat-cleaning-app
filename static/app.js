

$(function(){
    $("food-suggestion").on("click", function(event){
        event.preventDefault();
        new_ul = document.createElement("ul");
        ("today-meal").append(new_ul)
        let food = $("card-text").val();
        console.log(food);
        $(new_ul).append(food);
    })
})


