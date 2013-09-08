function eliminatePlayer(playerId) {

    var form = $('#eliminate-player')
    $('#eliminate-player-playerId').val(playerId)
    form.submit();
}