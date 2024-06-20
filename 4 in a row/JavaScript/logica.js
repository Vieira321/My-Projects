export const boardRows = 6;
export const boardCols = 7;
export const board = [];
for (let i = 0; i < boardCols; i++) {
    board[i] = new Array(boardRows).fill(null);
}

let currentPlayer = 1;

export function checkWin(column, row, player) {
    return checkDirection(column, row, player, 1, 0) + checkDirection(column, row, player, -1, 0) > 2 ||
        checkDirection(column, row, player, 0, 1) + checkDirection(column, row, player, 0, -1) > 2 ||
        checkDirection(column, row, player, 1, 1) + checkDirection(column, row, player, -1, -1) > 2 ||
        checkDirection(column, row, player, 1, -1) + checkDirection(column, row, player, -1, 1) > 2;
}

function checkDirection(column, row, player, deltaX, deltaY) {
    let count = 0;
    for (let i = 1; i < 4; i++) {
        const newCol = column + i * deltaX;
        const newRow = row + i * deltaY;
        if (newCol >= 0 && newCol < boardCols && newRow >= 0 && newRow < boardRows && board[newCol][newRow] === player) {
            count++;
        } else {
            break;
        }
    }
    return count;
}

export function play(column) {
    for (let row = boardRows - 1; row >= 0; row--) {
        if (board[column][row] === null) {
            board[column][row] = currentPlayer;
            const win = checkWin(column, row, currentPlayer);
            if (win) {
                window.showPopup(`Player ${currentPlayer} wins!`);
                return;
            }
            currentPlayer = currentPlayer === 1 ? 2 : 1;
            break;
        }
    }
}

export function resetGame() {
    for (let column = 0; column < boardCols; column++) {
        for (let row = 0; row < boardRows; row++) {
            board[column][row] = null;
        }
    }
    currentPlayer = 1;
}

window.closePopup = function() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('winner-popup').style.display = 'none';
    resetGame();
    window.location.reload(); // Reload the page to reset the game state
}
