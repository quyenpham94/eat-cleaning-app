




$(document).ready(function(){
	const mealInfo = $('.meal-info')
	const addLikeBtn = $('.fav')
   

	mealInfo.on('click', '.fav', async function(event){
        event.preventDefault();
		const id = $(event.target).parent().data('id')
		console.log(id)
	
		if (event.target.classList.contains('fas')) {
			await axios.remove(`/api/meal/${id}`)
			$(event.target).toggleClass('fas fa-heart')
			$(event.target).toggleClass('far fa-heart')
			console.log('Delete Ingredient From Meal')
		} else {
			try {
				await axios.post(`/api/meal/${id}`, (data = { id: id }))
				$(event.target).toggleClass('fas fa-heart')
				$(event.target).toggleClass('far fa-heart')
				console.log('Add Ingredient To Meal')
			} catch (err) {
				console.log('Login Required', err)
			}
		}
	})
    
})
$(document).ready(function(){
    const removeMeal = $('.flex')
    removeMeal.on('click', function(e){
        e.preventDefault();
        $(".card-body").parent().remove();
        console.log("delete your meal")
    })
})