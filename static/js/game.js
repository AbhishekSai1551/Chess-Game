var board = null
var game = new Chess()
var $status = $('#status')
var $pgn = $('#pgn')

function onDragStart (source, piece, position, orientation) {
  if (game.game_over()) return false
  if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
      (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
    return false
  }
}

function onDrop (source, target) {
  var move = game.move({
    from: source,
    to: target,
    promotion: 'q' // NOTE: always promote to a queen for simplicity
  })
  if (move === null) return 'snapback'

  updateStatus()
  makeAIMove()
}

function makeAIMove() {
    $status.html("Thinking...")
    
    $.ajax({
        url: '/move',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            fen: game.fen(),
            move: game.history({ verbose: true }).pop().san
        }),
        success: function(response) {
            if(response.game_over) {
                alert("Game Over!");
            } else {
                game.move(response.ai_move, {sloppy: true});
                board.position(game.fen());
                updateStatus();
            }
        },
        error: function(error) {
            console.log("Error:", error);
            $status.html("Error connecting to engine");
        }
    });
}

function onSnapEnd () {
  board.position(game.fen())
}

function updateStatus () {
  var status = ''
  var moveColor = 'White'
  if (game.turn() === 'b') {
    moveColor = 'Black'
  }
  if (game.in_checkmate()) {
    status = 'Game over, ' + moveColor + ' is in checkmate.'
  }
  else if (game.in_draw()) {
    status = 'Game over, drawn position'
  }
  else {
    status = moveColor + ' to move'
    if (game.in_check()) {
      status += ', ' + moveColor + ' is in check'
    }
  }

  $status.html(status)
  $pgn.html(game.pgn())
}

var config = {
  draggable: true,
  position: 'start',
  onDragStart: onDragStart,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd
}
board = Chessboard('myBoard', config)

updateStatus()
