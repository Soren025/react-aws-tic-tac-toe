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
            roomName: '',
            history: [{
                squares: Array(9).fill(null),
            }],
            stepNumber: 0,
            xIsNext: true,
        };
    }

    componentDidMount() {
        this.client = null;
        this.connect();
    }

    connect() {
        if (!this.client) {
            this.client = new W3CWebSocketClient('wss://0re9rbthv8.execute-api.us-east-2.amazonaws.com/prod');
            this.client.onerror = this.onClientError.bind(this);
            this.client.onopen = this.onClientOpen.bind(this);
            this.client.onclose = this.onClientClose.bind(this);
            this.client.onmessage = this.onClientMessage.bind(this);
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

    onClientMessage(e) {
        if (typeof e.data === 'string') {
            console.log('Message: ' + e.data);
            const message = JSON.parse(e.data);
            if (message.type === 'state') {
                const state = message.payload;
                const history = [];
                state.history.forEach(squares => {
                    history.push({
                        squares: squares,
                    });
                });
                this.setState({
                    history: history,
                    stepNumber: state.step_number,
                    xIsNext: state.x_is_next,
                });
            }
        }
    }

    sendMessage(message) {
        if (this.client && this.client.readyState === this.client.OPEN) {
            this.client.send(JSON.stringify(message))
        }
    }

    handleClick(i) {
        this.sendMessage({
            type: 'click_square',
            payload: {
                'index': i,
            },
        });
    }

    jumpTo(step) {
        this.sendMessage({
            type: 'jump_to',
            payload: {
                'step': step,
            },
        });
    }

    render() {
        const history = this.state.history;
        const current = history[this.state.stepNumber];
        const winner = calculateWinner(current.squares);

        const moves = history.map((step, move) => {
            let desc = move ?
                'Go to move #' + move :
                'Go to game start';
            if (move === this.state.stepNumber)
                desc += ' ***';
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
            <div>
                <div>
                    <button
                        onClick={() => {
                            if (this.state.roomName === '')
                                return;
                            this.sendMessage({
                                type: 'join_room',
                                payload: {
                                    room_name: this.state.roomName,
                                }
                            })
                        }}
                    >Join Room</button>

                    <form>
                        <input
                            type='text'
                            onChange={e => {
                                this.setState({
                                    roomName: e.target.value,
                                })
                            }}
                        >
                        </input>
                    </form>

                    <button
                        onClick={() => {
                            this.sendMessage({
                                type: 'leave_room',
                            });
                            this.setState({
                                history: [{
                                    squares: Array(9).fill(null),
                                }],
                                stepNumber: 0,
                                xIsNext: true,
                            })
                        }}
                    >Leave Room</button>
                </div>
                <div className="game">
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
