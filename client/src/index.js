import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

// https://www.npmjs.com/package/websocket
const W3CWebSocketClient = require('websocket').w3cwebsocket

function Square(props) {
    return (
        <button className="square" onClick={() => props.onClick()}>
            {props.value}
        </button>
    )
}

class Board extends React.Component {
    renderSquare(i) {
        return (
            <Square
                value={this.props.squares[i]}
                onClick={() => this.props.onClick(i)}
            />
        );
    }

    render() {
        return (
            <div>
                <div className="board-row">
                    {this.renderSquare(0)}
                    {this.renderSquare(1)}
                    {this.renderSquare(2)}
                </div>
                <div className="board-row">
                    {this.renderSquare(3)}
                    {this.renderSquare(4)}
                    {this.renderSquare(5)}
                </div>
                <div className="board-row">
                    {this.renderSquare(6)}
                    {this.renderSquare(7)}
                    {this.renderSquare(8)}
                </div>
            </div>
        );
    }
}

class Game extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            mySymbol: null,
            ready: false,
            otherReady: false,
            isPlaying: false,
            history: [{
                squares: Array(9).fill(null),
            }],
            stepNumber: 0,
            xIsNext: true,
        };
        this.client = null;
    }

    connect() {
        if (!this.client) {
            this.client = new W3CWebSocketClient('wss://nwsd1x3b66.execute-api.us-east-2.amazonaws.com/prod');
            this.client.onerror = this.onClientError;
            this.client.onopen = this.onClientOpen;
            this.client.onclose = this.onClientClose;
            this.client.onmessage = this.onClientMessage;
        }
    }

    disconnect() {
        if (this.client && this.client.readyState === this.client.OPEN) {
            this.client.close();
            this.client = null;
        }
    }

    onClientError() {
        this.client = null;
        console.log('Connection Error');
    }

    onClientOpen() {
        console.log('WebSocket Client Connected');
    }

    onClientClose() {
        this.client = null;
        console.log('Client Closed');
    }

    onClientMessage(message) {
        if (typeof message.data === 'string') {
            console.log("Received: '" + message.data + "'");
        }
    }

    sendMessage(message) {
        if (this.client && this.client.readyState === this.client.OPEN) {
            this.client.send(JSON.stringify(message))
        }
    }

    handleClick(i) {
        const history = this.state.history.slice(0, this.state.stepNumber + 1);
        const current = history[history.length - 1];
        const squares = current.squares.slice();
        if (calculateWinner(squares) || squares[i]) {
            return;
        }
        squares[i] = this.state.xIsNext ? 'X' : 'O';
        this.setState({
            history: history.concat([{
                squares: squares
            }]),
            stepNumber: history.length,
            xIsNext: !this.state.xIsNext,
        })
    }

    jumpTo(step) {
        this.setState({
            stepNumber: step,
            xIsNext: (step % 2) === 0,
        })
    }

    render() {
        const history = this.state.history;
        const current = history[this.state.stepNumber];
        const winner = calculateWinner(current.squares);

        const moves = history.map((step, move) => {
            const desc = move ?
                'Go to move #' + move :
                'Go to game start';
            return (
                <li key={move}>
                    <button onClick={() => this.jumpTo(move)}>{desc}</button>
                </li>
            )
        });

        let status;
        if (winner) {
            status = 'Winner: ' + winner;
        } else if (this.state.stepNumber === 9) {
            status = 'ITS A DRAW';
        } else {
            status = 'Next player: ' + (this.state.xIsNext ? 'X' : 'O');
        }

        return (
            <div className="game">
                <button onClick={() => this.connect()}>Connect</button>
                <button onClick={() => this.disconnect()}>Disconnect</button>

                <button
                    onClick={() => this.sendMessage({
                        type: 'join_room',
                        payload: {
                            room_name: 'HELLO_ROOM'
                        }
                    })}
                >Join Room</button>

                <button
                    onClick={() => this.sendMessage({
                        type: 'leave_room'
                    })}
                >Leave Room</button>

                <div className="game-board">
                    <Board 
                        squares={current.squares}
                        onClick={i => this.handleClick(i)}
                    />
                </div>
                <div className="game-info">
                    <div>{status}</div>
                    <ol>{moves}</ol>
                </div>
            </div>
        );
    }
}

// ========================================

ReactDOM.render(
    <Game />,
    document.getElementById('root')
);

function calculateWinner(squares) {
    const lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ];
    for (let i = 0; i < lines.length; i++) {
        const [a, b, c] = lines[i];
        if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
            return squares[a];
        }
    }
    return null;
}
