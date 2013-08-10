function signup(userId, gameId){
	
	var form = $('#signup')
	$('#signup-playerId').val(userId)
	form.playerId = userId
	$.post(
		form.attr('action'),
		form.serialize()
	);
}

function unsignup(userId, gameId){

	var form = $('#unsignup')
	$('#unsignup-playerId').val(userId)
	form.playerId = userId
	$.post(
		form.attr('action'),
		form.serialize()
	);
}

function reloadInterestTable(gameId){
    var data = $.get('/pokerroom/game/' + gameId + '/signups')
    alert(data)
}