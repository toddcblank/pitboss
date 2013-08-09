function signup(userId, gameId){
	
	var form = $('#signup')
	$('#signup-playerId').val(userId)
	form.playerId = userId
	$.post(
		form.attr('action'),
		form.serialize()
	);
}

//def reloadInterestTable(){}
//def removeSignup(userId){}