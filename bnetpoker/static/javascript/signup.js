function signup(userId) {

    var form = $('#signup')
    $('#signup-playerId').val(userId)
    form.playerId = userId
    $.post(
        url = form.attr('action'),
        data = form.serialize(),
        callback = reloadInterestTable($('#gameId').val())
    );
}

function unsignup(userId) {

    var form = $('#unsignup')
    $('#unsignup-playerId').val(userId)
    form.playerId = userId
    $.post(
        url = form.attr('action'),
        data = form.serialize(),
        callback = reloadInterestTable($('#gameId').val())
    );
}

function approve(userId) {

    var form = $('#approve')
    $('#approve-playerId').val(userId)
    form.playerId = userId
    $.post(
        url = form.attr('action'),
        data = form.serialize(),
        callback = reloadInterestTable($('#gameId').val())
    );
}

function reloadInterestTable(gameId) {
    $.getJSON(
        '/pokerroom/game/' + gameId + '/signups',
        function (data) {

            var $newTable = $("<table class='table table-hover' id='interestTable'><thead><td colspan='4' style='text-align: center' >Interest List</td></thead></table>");

            jQuery.each(data.interestList, function (i, val) {

                var newRow = "<tr>\n";
                newRow += "<td>" + (i + 1) + "</td>"
                newRow += "<td>" + val.player.nickname + "</td>\n";
                switch(val.state){
                    case "Playing":
                        newRow += "<td>Approved</td>\n";
                        newRow += "<td><a href='javascript:unsignup(" + val.player.id + ")'>Cancel</a></td>\n";
                        newRow += "<td/>\n"
                        break;
                    case "Interested":
                        newRow += "<td>Signed Up</td>"
                        newRow += "<td><a href='javascript:unsignup(" + val.player.id + ")'>Cancel</a></td>"
                        newRow += "<td><a href='javascript:approve(" + val.player.id + ")'>Approve</a></td>"
                        break;
                    default:
                        newRow += "<td>Not Signed Up</td>\n";
                        newRow += "<td><a href='javascript:signup(" + val.player.id + ")'>Signup</a></td>\n";
                        newRow += "<td/>\n"
                        break;
                }

                $newTable.append(newRow)
            });

            $("#interestTableDiv").empty();
            $("#interestTableDiv").append($newTable);

        });
}

function createPlayerAndSignup() {
    var form = $('#create-and-signup')
    $.post(
        form.attr('action'),
        form.serialize()
    )

}

$(document).ready(function () {
    $('#create-and-signup input').keydown(function (e) {
        if (e.keyCode == 13) {
            e.preventDefault()
            createPlayerAndSignup()
            $("#create-and-signup-nickname").val("")
            reloadInterestTable($('#gameId').val())
        }
    });
});