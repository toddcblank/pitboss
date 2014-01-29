function eliminatePlayer(playerId) {

    var form = $('#eliminate-player')
    $('#eliminate-player-playerId').val(playerId)
    form.submit();
}
function playerInterested(playerId) {

    var form = $('#player-interested')
    $('#interested-player-playerId').val(playerId)
    form.submit();
}

function balanceTables() {

    var form = $('#balance-tables')
    $('#balance-collapseTables').val($('#collapse-table-option').is(":checked"))
    form.submit();
}

function reseatPlayers() {
    var form = $('#reseat-players')
    form.submit();
}

function seatPlayer(playerId) {

    var form = $('#seat-player')
    $('#seat-player-playerId').val(playerId)
    form.submit();
}

function unseatPlayer(playerId) {

    var form = $('#unseat-player')
    $('#unseat-player-playerId').val(playerId)
    form.submit();
}

function undoElimination(playerId) {

    var form = $('#undo-eliminate-player')
    $('#undo-eliminate-player-playerId').val(playerId)
    form.submit();
}

function removePlayer(playerId) {

    var confirmation = confirm("This will permanently remove the player from the player list, are you sure?")
    if (confirmation == true) {
        var form = $('#remove-player')
        $('#remove-player-playerId').val(playerId)
        form.submit();
    }
}
