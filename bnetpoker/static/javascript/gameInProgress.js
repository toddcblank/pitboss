function eliminatePlayer(playerId) {

    var form = $('#eliminate-player')
    $('#eliminate-player-playerId').val(playerId)
    form.submit();
}

function undoElimination(playerId) {

    var form = $('#undo-eliminate-player')
    $('#undo-eliminate-player-playerId').val(playerId)
    form.submit();
}