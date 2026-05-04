const board_size = 8;
const block_size = 107;
const theme_config = window.nochess_theme || {};
const block_light = theme_config.block_light || '#D8E3E7';
const block_dark = theme_config.block_dark || '#7699AF';
const select_block = theme_config.select_block || '#FFDF5A';
const block_select_alpha_light = 0.34;
const block_select_alpha_dark = 0.58;
const move_pieces_color = theme_config.move_pieces_color || '#58B4FF';
const block_move_from_alpha = 0.56;
const block_move_to_alpha = 0.62;
const move_highlight_delay_ms = 25;
const result_overlay_duration_ms = 300;
const result_win = theme_config.result_win || '#00BE16';
const result_lose = theme_config.result_lose || '#BE0000';
const result_draw = theme_config.result_draw || '#434343';
const result_overlay_alpha = 0.64;
const arrow_color = theme_config.arrow_color || '#BD3667';
const asset_root = window.nochess_asset_root || 'https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/NoChess';
const noise_src = `${asset_root}/other/noise.png`;
const start_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

const chess_pieces = {
    wP: `${asset_root}/pieces/white-pawn.png`,
    wR: `${asset_root}/pieces/white-rook.png`,
    wN: `${asset_root}/pieces/white-knight.png`,
    wB: `${asset_root}/pieces/white-bishop.png`,
    wQ: `${asset_root}/pieces/white-queen.png`,
    wK: `${asset_root}/pieces/white-king.png`,
    bP: `${asset_root}/pieces/black-pawn.png`,
    bR: `${asset_root}/pieces/black-rook.png`,
    bN: `${asset_root}/pieces/black-knight.png`,
    bB: `${asset_root}/pieces/black-bishop.png`,
    bQ: `${asset_root}/pieces/black-queen.png`,
    bK: `${asset_root}/pieces/black-king.png`
};

const sound_urls = {
    game_start: 'https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/game-start.mp3',
    game_end: 'https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/game-end.mp3',
    capture: 'https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/capture.mp3',
    castle: 'https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/castle.mp3',
    premove: 'https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/premove.mp3',
    move_self: 'https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-self.mp3',
    move_opponent: 'https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-opponent.mp3',
    move_check: 'https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-check.mp3',
    promote: 'https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/promote.mp3'
};

const ui_text = {
    no_history: 'No history',
    unknown_date: 'Unknown date',
    chess_library_not_ready: 'Chess library not ready',
    pgn_empty: 'Paste PGN text first',
    pgn_invalid: 'Invalid PGN format',
    pgn_loaded: 'PGN loaded',
    pgn_copied: 'PGN copied',
    copy_failed: 'Copy failed'
};

const crown_icon_src = `${asset_root}/icons/result-crown.svg`;
const flag_icon_src = `${asset_root}/icons/result-flag.svg`;
const draw_icon_src = `${asset_root}/icons/result-draw.svg`;

const canvas = document.getElementById('chessBoard');
const ctx = canvas.getContext('2d');
canvas.width = board_size * block_size;
canvas.height = board_size * block_size;

const moves_scroll = document.querySelector('.moves_list_mobile');
const pgn_moves_board = document.querySelector('.pgn_moves_board');
const timer_black = document.querySelector('.timer_black');
const timer_white = document.querySelector('.timer_white');
const player_name_white = document.querySelector('.player_name_white');
const player_name_black = document.querySelector('.player_name_black');
const avatar_white = document.querySelector('.avatar_white');
const avatar_black = document.querySelector('.avatar_black');
const history_btn = document.getElementById('history_btn');
const share_btn = document.getElementById('share_btn');
const more_btn = document.getElementById('more_btn');
const app_layout = document.querySelector('.web_chess');
const first_move_icon = document.querySelector('.first_move_btn img');
const submenu_overlay = document.getElementById('submenu_overlay');
const history_panel = document.getElementById('history_panel');
const share_panel = document.getElementById('share_panel');
const history_games = document.getElementById('history_games');
const share_pgn_text = document.getElementById('share_pgn_text');
const load_pgn_btn = document.getElementById('load_pgn_btn');
const copy_pgn_btn = document.getElementById('copy_pgn_btn');
const share_status = document.getElementById('share_status');

let board = [];
let marked_cells = new Set();
let arrows = [];
let piece_images = {};
let noise_image = null;
let right_drag_start = null;
let is_flipped = false;
let parsed_games = [];
let current_game_index = 0;
let current_ply = 0;
let share_status_timeout = null;
let chess_ready = false;
let highlighted_move_cells = null;
let piece_animation = null;
let highlight_delay_timeout = null;
let result_markers = null;
let result_animation = null;
let nochess_profile = window.nochess_profile || null;
const mobile_breakpoint = window.matchMedia('(max-width: 572px)');
let was_mobile_layout = false;
const crown_icon_image = new Image();
const flag_icon_image = new Image();
const draw_icon_image = new Image();
crown_icon_image.src = crown_icon_src;
flag_icon_image.src = flag_icon_src;
draw_icon_image.src = draw_icon_src;

function hexToRgba(hex, alpha) {
    const value = hex.replace('#', '');
    const full = value.length === 3
        ? value.split('').map((c) => c + c).join('')
        : value;
    const int = Number.parseInt(full, 16);
    const r = (int >> 16) & 255;
    const g = (int >> 8) & 255;
    const b = int & 255;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.async = true;
        script.onload = () => resolve(true);
        script.onerror = () => reject(new Error(`failed: ${src}`));
        document.head.appendChild(script);
    });
}

async function loadChessLibrary() {
    if (typeof window.Chess !== 'undefined') {
        return true;
    }

    const classic_sources = [
        'https://cdn.jsdelivr.net/npm/chess.js@0.13.4/chess.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.13.4/chess.min.js'
    ];

    for (const src of classic_sources) {
        try {
            await loadScript(src);
            if (typeof window.Chess !== 'undefined') {
                return true;
            }
        } catch (error) {
        }
    }

    try {
        const module = await import('https://cdn.jsdelivr.net/npm/chess.js@1.4.0/dist/esm/chess.js');
        window.Chess = module.Chess || module.default;
        return typeof window.Chess !== 'undefined';
    } catch (error) {
        return false;
    }
}

function createChess() {
    if (typeof Chess === 'undefined') {
        return null;
    }
    return new Chess();
}

function loadPgnToChess(chess, pgn_text) {
    if (!chess) {
        return false;
    }

    if (typeof chess.load_pgn === 'function') {
        let loaded = chess.load_pgn(pgn_text, { newline_char: '\n', sloppy: true });
        if (!loaded) {
            loaded = chess.load_pgn(pgn_text, { sloppy: true });
        }
        if (!loaded) {
            loaded = chess.load_pgn(pgn_text);
        }
        return loaded;
    }

    if (typeof chess.loadPgn === 'function') {
        try {
            chess.loadPgn(pgn_text, { strict: false });
            return true;
        } catch (error) {
            try {
                chess.loadPgn(pgn_text);
                return true;
            } catch (second_error) {
                return false;
            }
        }
    }

    return false;
}

function moveOnChess(chess, move_text) {
    if (!chess || !move_text) {
        return null;
    }

    try {
        const sloppy_move = chess.move(move_text, { sloppy: true });
        if (sloppy_move) {
            return sloppy_move;
        }
    } catch (error) {
    }

    try {
        return chess.move(move_text);
    } catch (error) {
        return null;
    }
}

const sound_players = Object.fromEntries(Object.entries(sound_urls).map(([name, url]) => {
    const base = new Audio(url);
    base.preload = 'auto';
    return [name, () => {
        const sound = base.cloneNode(true);
        sound.volume = 0.9;
        sound.play().catch(() => {});
    }];
}));

function updateScrollShadow() {
    const at_bottom = moves_scroll.scrollTop + moves_scroll.clientHeight >= moves_scroll.scrollHeight - 5;
    const has_overflow = moves_scroll.scrollHeight > moves_scroll.clientHeight;
    pgn_moves_board.classList.toggle('has_scroll', has_overflow && !at_bottom);
}

function parseHeaders(pgn_text) {
    const headers = {};
    const header_regex = /^\[(\w+)\s+"([^"]*)"\]$/gm;
    let match = header_regex.exec(pgn_text);
    while (match) {
        headers[match[1]] = match[2];
        match = header_regex.exec(pgn_text);
    }
    return headers;
}

function normalizeClock(clock) {
    if (!clock) {
        return null;
    }
    const parts = clock.split(':');
    if (parts.length === 3) {
        const hours = Number(parts[0]);
        const minutes = Number(parts[1]);
        const seconds = Number(parts[2]);
        if (!Number.isNaN(hours) && !Number.isNaN(minutes) && !Number.isNaN(seconds)) {
            if (hours === 0) {
                return `${minutes}:${String(seconds).padStart(2, '0')}`;
            }
            return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }
    }
    if (parts.length === 2) {
        const minutes = Number(parts[0]);
        const seconds = Number(parts[1]);
        if (!Number.isNaN(minutes) && !Number.isNaN(seconds)) {
            return `${minutes}:${String(seconds).padStart(2, '0')}`;
        }
    }
    return clock;
}

function isMoveToken(token) {
    return /^(O-O(-O)?|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](=[QRBN])?[+#]?|[a-h]x[a-h][1-8](=[QRBN])?[+#]?|[a-h][1-8](=[QRBN])?[+#]?)$/.test(token);
}

function extractMoveClocks(pgn_text) {
    const cleaned = pgn_text.replace(/^\[[^\]]*\]\s*$/gm, '');
    const tokens = cleaned.match(/\{[^}]*\}|[^\s]+/g) || [];
    const clocks_by_ply = {};
    let ply = 0;
    let last_move_ply = 0;

    for (const token of tokens) {
        if (!token) {
            continue;
        }

        if (token.startsWith('{')) {
            const clk_match = token.match(/\[%clk\s+([^\]]+)\]/i);
            if (clk_match && last_move_ply > 0) {
                clocks_by_ply[last_move_ply] = normalizeClock(clk_match[1].trim());
            }
            continue;
        }

        if (/^\d+\.{1,3}$/.test(token)) {
            continue;
        }

        if (token === '1-0' || token === '0-1' || token === '1/2-1/2' || token === '*') {
            continue;
        }

        if (isMoveToken(token)) {
            ply += 1;
            last_move_ply = ply;
        }
    }

    return clocks_by_ply;
}

function fenCharToPiece(char) {
    const is_white = char === char.toUpperCase();
    const color = is_white ? 'w' : 'b';
    const type = char.toUpperCase();
    if (!'PRNBQK'.includes(type)) {
        return null;
    }
    return `${color}${type}`;
}

function boardFromFen(fen) {
    const rows = fen.split(' ')[0].split('/');
    return rows.map((row) => {
        const parsed = [];
        for (const char of row) {
            const count = Number(char);
            if (!Number.isNaN(count) && count > 0) {
                for (let i = 0; i < count; i += 1) {
                    parsed.push(null);
                }
            } else {
                parsed.push(fenCharToPiece(char));
            }
        }
        return parsed;
    });
}

function squareToCoords(square) {
    if (!square || square.length < 2) {
        return null;
    }
    const file = square.charCodeAt(0) - 97;
    const rank = Number(square[1]);
    if (file < 0 || file > 7 || Number.isNaN(rank) || rank < 1 || rank > 8) {
        return null;
    }
    return { row: 8 - rank, col: file };
}

function setHighlightedMove(from_square, to_square) {
    const from = squareToCoords(from_square);
    const to = squareToCoords(to_square);
    highlighted_move_cells = from && to ? { from, to } : null;
}

function scheduleHighlightedMove(from_square, to_square) {
    if (highlight_delay_timeout) {
        clearTimeout(highlight_delay_timeout);
        highlight_delay_timeout = null;
    }

    highlighted_move_cells = null;

    if (!from_square || !to_square) {
        return;
    }

    highlight_delay_timeout = setTimeout(() => {
        setHighlightedMove(from_square, to_square);
        highlight_delay_timeout = null;
        render();
    }, move_highlight_delay_ms);
}

window.highlightMoveSquares = function highlightMoveSquares(from_square, to_square) {
    setHighlightedMove(from_square, to_square);
    render();
};

function createAnimationState(from, to, piece_code) {
    return {
        from,
        to,
        piece_code,
        start_time: performance.now(),
        duration: 180
    };
}

function animateMoveTransition(animation_state) {
    piece_animation = animation_state;

    function step() {
        if (!piece_animation) {
            return;
        }

        const elapsed = performance.now() - piece_animation.start_time;
        if (elapsed >= piece_animation.duration) {
            piece_animation = null;
            render();
            return;
        }

        render();
        requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
}

function parsePgnToGameState(pgn_text) {
    if (!chess_ready || typeof Chess === 'undefined') {
        return null;
    }

    const parser = createChess();
    if (!parser) {
        return null;
    }

    const loaded = loadPgnToChess(parser, pgn_text);

    if (!loaded) {
        const fallback = parseMovesWithSloppyParser(pgn_text);
        if (!fallback) {
            return null;
        }
        return fallback;
    }

    const headers = parseHeaders(pgn_text);
    const verbose_moves = parser.history({ verbose: true });
    const clocks_by_ply = extractMoveClocks(pgn_text);
    const simulator = createChess();
    if (!simulator) {
        return null;
    }
    const positions = [boardFromFen(simulator.fen())];

    for (const move of verbose_moves) {
        moveOnChess(simulator, move.san);
        positions.push(boardFromFen(simulator.fen()));
    }

    const moves = verbose_moves.map((move, index) => ({
        ...move,
        clock: clocks_by_ply[index + 1] || null,
        is_capture: move.flags.includes('c') || move.flags.includes('e'),
        is_castle: move.flags.includes('k') || move.flags.includes('q'),
        is_promotion: move.flags.includes('p'),
        is_check: move.san.includes('+'),
        is_mate: move.san.includes('#')
    }));

    return {
        pgn_text,
        headers,
        moves,
        positions
    };
}

function normalizeMoveToken(token) {
    if (!token) {
        return '';
    }

    let value = token.trim();
    value = value.replace(/^\d+\.\.\./, '');
    value = value.replace(/^\d+\./, '');
    value = value.replace(/[!?]+$/g, '');
    value = value.replace(/^0-0-0$/, 'O-O-O');
    value = value.replace(/^0-0$/, 'O-O');
    value = value.replace(/=([qrbn])/g, (_, p1) => `=${p1.toUpperCase()}`);
    return value;
}

function extractSanTokens(movetext) {
    const regex = /(?:O-O-O|O-O|0-0-0|0-0|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBNqrbn])?|[a-h]x[a-h][1-8](?:=[QRBNqrbn])?|[a-h][1-8](?:=[QRBNqrbn])?)(?:[+#])?|1-0|0-1|1\/2-1\/2|\*/g;
    return movetext.match(regex) || [];
}

function tryApplySanMove(game, token) {
    const first_try = moveOnChess(game, token);
    if (first_try) {
        return first_try;
    }

    const without_suffix = token.replace(/[+#]$/, '');
    if (without_suffix !== token) {
        const second_try = moveOnChess(game, without_suffix);
        if (second_try) {
            return second_try;
        }
    }

    return null;
}

function parseMovesWithSloppyParser(pgn_text) {
    if (!chess_ready || typeof Chess === 'undefined') {
        return null;
    }

    const headers = parseHeaders(pgn_text);
    const clocks_by_ply = extractMoveClocks(pgn_text);
    const move_section = pgn_text
        .replace(/^\[[^\]]*\]\s*$/gm, '')
        .replace(/\{[^}]*\}/g, ' ')
        .replace(/\([^)]*\)/g, ' ')
        .replace(/\$\d+/g, ' ')
        .replace(/\r\n/g, '\n')
        .trim();

    const start_index = move_section.search(/\b\d+\./);
    const mandatory_movetext = start_index >= 0 ? move_section.slice(start_index) : move_section;
    const normalized_movetext = mandatory_movetext
        .replace(/\s+/g, ' ')
        .trim();

    const raw_tokens = extractSanTokens(normalized_movetext);
    const game = createChess();
    if (!game) {
        return null;
    }
    const moves = [];
    const positions = [boardFromFen(game.fen())];
    let ply = 0;

    for (const raw of raw_tokens) {
        if (!raw || raw === '1-0' || raw === '0-1' || raw === '1/2-1/2' || raw === '*') {
            continue;
        }

        const split_tokens = raw.includes('.') ? raw.split('.').filter(Boolean) : [raw];
        for (const token of split_tokens) {
            const clean_token = normalizeMoveToken(token);
            if (!clean_token || /^\d+$/.test(clean_token)) {
                continue;
            }

            if (clean_token === '...' || /^\.+$/.test(clean_token)) {
                continue;
            }

            if (clean_token === '1-0' || clean_token === '0-1' || clean_token === '1/2-1/2' || clean_token === '*') {
                continue;
            }

            const move = tryApplySanMove(game, clean_token);
            if (!move) {
                return null;
            }

            ply += 1;
            moves.push({
                ...move,
                clock: clocks_by_ply[ply] || null,
                is_capture: move.flags.includes('c') || move.flags.includes('e'),
                is_castle: move.flags.includes('k') || move.flags.includes('q'),
                is_promotion: move.flags.includes('p'),
                is_check: move.san.includes('+'),
                is_mate: move.san.includes('#')
            });
            positions.push(boardFromFen(game.fen()));
        }
    }

    if (moves.length === 0) {
        return null;
    }

    return {
        pgn_text,
        headers,
        moves,
        positions
    };
}

function sanitizePgnInput(raw_text) {
    if (!raw_text) {
        return '';
    }

    let text = raw_text.replace(/^\uFEFF/, '').trim();
    const fenced = text.match(/^```(?:pgn)?\s*([\s\S]*?)\s*```$/i);
    if (fenced) {
        text = fenced[1].trim();
    }

    return text
        .replace(/\u00A0/g, ' ')
        .replace(/\r\n/g, '\n')
        .replace(/\t/g, ' ')
        .replace(/\n{3,}/g, '\n\n');
}

function autoResizeShareTextarea() {
    share_pgn_text.style.height = 'auto';
    const next_height = Math.min(share_pgn_text.scrollHeight, Math.floor(window.innerHeight * 0.55));
    share_pgn_text.style.height = `${Math.max(next_height, 170)}px`;
}

function setShareStatus(message, is_error) {
    if (share_status_timeout) {
        clearTimeout(share_status_timeout);
        share_status_timeout = null;
    }

    share_status.textContent = message || '';
    share_status.classList.remove('show', 'error');
    if (!message) {
        return;
    }
    if (is_error) {
        share_status.classList.add('error');
    }
    requestAnimationFrame(() => {
        share_status.classList.add('show');
    });

    share_status_timeout = setTimeout(() => {
        share_status.classList.remove('show', 'error');
        share_status.textContent = '';
        share_status_timeout = null;
    }, 2200);
}

function clearResultVisuals() {
    result_markers = null;
    result_animation = null;
}

function isSameResultMarkers(first, second) {
    if (!first && !second) {
        return true;
    }
    if (!first || !second) {
        return false;
    }
    return first.winner.row === second.winner.row
        && first.winner.col === second.winner.col
        && first.loser.row === second.loser.row
        && first.loser.col === second.loser.col;
}

function getResultOverlayProgress() {
    if (!result_animation) {
        return 1;
    }
    return Math.min(1, (performance.now() - result_animation.start_time) / result_animation.duration);
}

function getResultIconScale(progress) {
    const start = 0.52;
    const overshoot = 1.08;
    const ease_out_back = 1 + (2.1 * ((progress - 1) ** 3)) + (1.1 * ((progress - 1) ** 2));

    if (progress < 0.78) {
        return start + ((overshoot - start) * ease_out_back);
    }

    const settle_progress = (progress - 0.78) / 0.22;
    return overshoot + ((1 - overshoot) * settle_progress);
}

function animateResultOverlay() {
    function step() {
        if (!result_animation) {
            return;
        }

        const progress = getResultOverlayProgress();
        render();

        if (progress >= 1) {
            result_animation = null;
            return;
        }

        requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
}

function getWinnerFromResult(result) {
    if (result === '1-0') {
        return 'w';
    }
    if (result === '0-1') {
        return 'b';
    }
    if (result === '1/2-1/2') {
        return 'draw';
    }
    return null;
}

function updateResultVisuals() {
    const previous_markers = result_markers;
    clearResultVisuals();

    const game = getCurrentGame();
    if (!game || current_ply !== game.moves.length) {
        return;
    }

    const winner = getWinnerFromResult(game.headers.Result || '');
    if (!winner) {
        return;
    }

    let winner_king = null;
    let loser_king = null;
    for (let row = 0; row < board_size; row += 1) {
        for (let col = 0; col < board_size; col += 1) {
            const piece = board[row][col];
            if (winner === 'draw') {
                if (piece === 'wK') {
                    winner_king = { row, col };
                } else if (piece === 'bK') {
                    loser_king = { row, col };
                }
            } else {
                if (piece === (winner === 'w' ? 'wK' : 'bK')) {
                    winner_king = { row, col };
                } else if (piece === (winner === 'w' ? 'bK' : 'wK')) {
                    loser_king = { row, col };
                }
            }
        }
    }

    if (winner_king && loser_king) {
        const next_markers = {
            type: winner === 'draw' ? 'draw' : 'winlose',
            winner: winner_king,
            loser: loser_king
        };

        result_markers = next_markers;
        if (!isSameResultMarkers(previous_markers, next_markers)) {
            result_animation = {
                start_time: performance.now(),
                duration: result_overlay_duration_ms
            };
            animateResultOverlay();
        }
    }
}

async function copyTextToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return;
    }

    const helper = document.createElement('textarea');
    helper.value = text;
    helper.setAttribute('readonly', '');
    helper.style.position = 'fixed';
    helper.style.top = '-1000px';
    helper.style.left = '-1000px';
    document.body.appendChild(helper);
    helper.focus();
    helper.select();
    const success = document.execCommand('copy');
    document.body.removeChild(helper);
    if (!success) {
        throw new Error('copy-failed');
    }
}

function getCurrentGame() {
    return parsed_games[current_game_index] || null;
}

function normalizePlayerName(value) {
    return (value || '').toString().trim().toLowerCase();
}

function playerNameMatches(side_name, variants) {
    const side = normalizePlayerName(side_name);
    if (!side) {
        return false;
    }

    return variants.some((name) => {
        const candidate = normalizePlayerName(name);
        if (!candidate) {
            return false;
        }
        return side === candidate || side.includes(candidate) || candidate.includes(side);
    });
}

function detectMyColor(game) {
    if (!game || !nochess_profile || !game.headers) {
        return null;
    }

    const names = [
        nochess_profile.name,
        nochess_profile.username,
        nochess_profile.first_name,
        nochess_profile.last_name
    ];

    const white_match = playerNameMatches(game.headers.White, names);
    const black_match = playerNameMatches(game.headers.Black, names);

    if (white_match && !black_match) {
        return 'w';
    }
    if (black_match && !white_match) {
        return 'b';
    }
    return null;
}

function applyPlayerAvatars() {
    if (!avatar_white || !avatar_black || !nochess_profile) {
        return;
    }

    const me_photo = nochess_profile.photo || '';
    const enemy_photo = nochess_profile.enemy_photo || '';
    if (!me_photo && !enemy_photo) {
        return;
    }

    const game = getCurrentGame();
    const my_color = detectMyColor(game) || 'w';
    const white_photo = my_color === 'b' ? enemy_photo : me_photo;
    const black_photo = my_color === 'b' ? me_photo : enemy_photo;

    if (white_photo) {
        avatar_white.style.backgroundImage = `url('${white_photo}')`;
    }
    if (black_photo) {
        avatar_black.style.backgroundImage = `url('${black_photo}')`;
    }
}

function setNoChessProfile(profile) {
    nochess_profile = profile || null;
    applyPlayerAvatars();
}

window.setNoChessProfile = setNoChessProfile;

function getTimerTextForColor(color) {
    const game = getCurrentGame();
    if (!game) {
        return '--:--';
    }

    let latest = null;
    for (let i = 0; i < current_ply; i += 1) {
        const move = game.moves[i];
        if (move.color === color && move.clock) {
            latest = move.clock;
        }
    }
    return latest || '--:--';
}

function updateTimers() {
    timer_white.textContent = getTimerTextForColor('w');
    timer_black.textContent = getTimerTextForColor('b');
}

function updatePlayers() {
    const game = getCurrentGame();
    if (!game) {
        applyPlayerAvatars();
        return;
    }
    player_name_white.textContent = game.headers.White || 'White';
    player_name_black.textContent = game.headers.Black || 'Black';
    applyPlayerAvatars();
}

function renderMoves() {
    const game = getCurrentGame();
    moves_scroll.innerHTML = '';

    if (!game) {
        updateScrollShadow();
        return;
    }

    for (let i = 0; i < game.moves.length; i += 2) {
        const move_number = Math.floor(i / 2) + 1;
        const white = game.moves[i] || null;
        const black = game.moves[i + 1] || null;
        const row = document.createElement('div');
        row.className = 'move_row';

        const number = document.createElement('div');
        number.className = 'move_number';
        number.textContent = `${move_number}.`;

        const white_cell = document.createElement('div');
        white_cell.className = 'move_white';
        white_cell.textContent = white ? white.san : '';
        if (white) {
            white_cell.dataset.ply = String(i + 1);
        }

        const black_cell = document.createElement('div');
        black_cell.className = 'move_black';
        black_cell.textContent = black ? black.san : '';
        if (black) {
            black_cell.dataset.ply = String(i + 2);
        }

        row.append(number, white_cell, black_cell);
        moves_scroll.appendChild(row);
    }

    moves_scroll.querySelectorAll('.move_white[data-ply], .move_black[data-ply]').forEach((cell) => {
        cell.addEventListener('click', () => {
            const next_ply = Number(cell.dataset.ply || '0');
            if (next_ply > 0) {
                setPly(next_ply, true);
            }
        });
    });

    updateCurrentMoveHighlight();
    updateScrollShadow();
}

function updateCurrentMoveHighlight() {
    moves_scroll.querySelectorAll('.current_move').forEach((cell) => {
        cell.classList.remove('current_move');
    });

    if (current_ply <= 0) {
        return;
    }

    const active = moves_scroll.querySelector(`[data-ply="${current_ply}"]`);
    if (!active) {
        return;
    }

    active.classList.add('current_move');
    active.scrollIntoView({ block: 'nearest' });
}

function playSound(name) {
    const player = sound_players[name];
    if (player) {
        player();
    }
}

function playMoveSound(move) {
    if (!move) {
        return;
    }

    if (move.is_mate) {
        playSound('move_check');
        setTimeout(() => playSound('game_end'), 70);
        return;
    }

    if (move.is_promotion) {
        playSound('promote');
        return;
    }

    if (move.is_castle) {
        playSound('castle');
        return;
    }

    if (move.is_capture) {
        playSound('capture');
        return;
    }

    if (move.is_check) {
        playSound('move_check');
        return;
    }

    playSound(move.color === 'w' ? 'move_self' : 'move_opponent');
}

function setPly(next_ply, with_sound) {
    const game = getCurrentGame();
    if (!game) {
        return;
    }

    const previous_ply = current_ply;
    const previous_board = board.map((row) => [...row]);
    const clamped = Math.max(0, Math.min(next_ply, game.moves.length));
    const delta = clamped - previous_ply;
    const moved_forward_by_one = delta === 1;
    current_ply = clamped;

    if (current_ply > 0) {
        const move = game.moves[current_ply - 1];
        scheduleHighlightedMove(move.from, move.to);
    } else {
        scheduleHighlightedMove(null, null);
    }

    board = game.positions[current_ply].map((row) => [...row]);

    if (Math.abs(delta) === 1) {
        const move_index = delta > 0 ? current_ply - 1 : previous_ply - 1;
        const move = game.moves[move_index];
        if (move) {
            const from_square = delta > 0 ? move.from : move.to;
            const to_square = delta > 0 ? move.to : move.from;
            const from = squareToCoords(from_square);
            const to = squareToCoords(to_square);
            const piece_code = from ? previous_board[from.row][from.col] : null;
            if (from && to && piece_code) {
                animateMoveTransition(createAnimationState(from, to, piece_code));
            } else {
                render();
            }
        } else {
            render();
        }
    } else {
        piece_animation = null;
        render();
    }

    updateCurrentMoveHighlight();
    updateTimers();
    updateResultVisuals();

    if (delta !== 0) {
        marked_cells.clear();
        arrows = [];
    }

    if (!with_sound || delta === 0) {
        return;
    }

    if (moved_forward_by_one && current_ply > 0) {
        playMoveSound(game.moves[current_ply - 1]);
        return;
    }

    playSound('premove');
}

function loadGame(index) {
    if (index < 0 || index >= parsed_games.length) {
        return;
    }
    current_game_index = index;
    current_ply = 0;
    marked_cells.clear();
    arrows = [];
    updatePlayers();
    renderMoves();
    setPly(0, false);
    share_pgn_text.value = parsed_games[current_game_index].pgn_text;
    playSound('game_start');
}

function buildHistoryList() {
    history_games.innerHTML = '';

    if (parsed_games.length === 0) {
        history_games.classList.add('empty');
        const empty = document.createElement('div');
        empty.className = 'history_empty';
        empty.textContent = ui_text.no_history;
        history_games.appendChild(empty);
        return;
    }

    history_games.classList.remove('empty');
    parsed_games.forEach((game, index) => {
        const button = document.createElement('button');
        button.className = 'history_game_btn';
        button.type = 'button';
        const white = game.headers.White || 'White';
        const black = game.headers.Black || 'Black';
        const date = game.headers.Date || ui_text.unknown_date;
        const result = game.headers.Result || '*';
        button.textContent = `${white} vs ${black} • ${result} • ${date}`;
        button.addEventListener('click', () => {
            closePanels();
            loadGame(index);
        });
        history_games.appendChild(button);
    });
}

function openPanel(panel) {
    submenu_overlay.classList.add('open');
    history_panel.classList.remove('open');
    share_panel.classList.remove('open');
    panel.classList.add('open');
}

function closePanels() {
    submenu_overlay.classList.remove('open');
    history_panel.classList.remove('open');
    share_panel.classList.remove('open');
}

function loadPieceImages(on_ready) {
    let loaded = 0;
    const total = Object.keys(chess_pieces).length;

    for (const [piece, src] of Object.entries(chess_pieces)) {
        const img = new Image();
        img.onload = () => {
            piece_images[piece] = img;
            loaded += 1;
            if (loaded === total) {
                on_ready();
            }
        };
        img.onerror = () => {
            loaded += 1;
            if (loaded === total) {
                on_ready();
            }
        };
        img.src = src;
    }
}

function loadNoise(on_ready) {
    const img = new Image();
    img.onload = () => {
        noise_image = img;
        on_ready();
    };
    img.onerror = () => on_ready();
    img.src = noise_src;
}

function toVisual(row, col) {
    if (is_flipped) {
        return { vrow: board_size - 1 - row, vcol: board_size - 1 - col };
    }
    return { vrow: row, vcol: col };
}

function fromVisual(vrow, vcol) {
    if (is_flipped) {
        return { row: board_size - 1 - vrow, col: board_size - 1 - vcol };
    }
    return { row: vrow, col: vcol };
}

function drawBoard() {
    for (let vrow = 0; vrow < board_size; vrow += 1) {
        for (let vcol = 0; vcol < board_size; vcol += 1) {
            const { row, col } = fromVisual(vrow, vcol);
            const is_light = (row + col) % 2 === 0;
            const is_marked = marked_cells.has(`${row},${col}`);
            const is_move_from = highlighted_move_cells
                && highlighted_move_cells.from.row === row
                && highlighted_move_cells.from.col === col;
            const is_move_to = highlighted_move_cells
                && highlighted_move_cells.to.row === row
                && highlighted_move_cells.to.col === col;

            if (is_move_to) {
                ctx.fillStyle = hexToRgba(move_pieces_color, block_move_to_alpha);
            } else if (is_move_from) {
                ctx.fillStyle = hexToRgba(move_pieces_color, block_move_from_alpha);
            } else if (is_marked) {
                const alpha = is_light ? block_select_alpha_light : block_select_alpha_dark;
                ctx.fillStyle = hexToRgba(select_block, alpha);
            } else {
                ctx.fillStyle = is_light ? block_light : block_dark;
            }
            ctx.fillRect(vcol * block_size, vrow * block_size, block_size, block_size);
        }
    }

    if (noise_image) {
        ctx.save();
        ctx.globalCompositeOperation = 'soft-light';
        ctx.drawImage(noise_image, 0, 0, canvas.width, canvas.height);
        ctx.restore();
    }
}

function drawResultOverlays() {
    if (!result_markers) {
        return;
    }

    const progress = getResultOverlayProgress();
    const winner = toVisual(result_markers.winner.row, result_markers.winner.col);
    const loser = toVisual(result_markers.loser.row, result_markers.loser.col);

    if (result_markers.type === 'draw') {
        ctx.fillStyle = hexToRgba(result_draw, result_overlay_alpha * progress);
        ctx.fillRect(winner.vcol * block_size, winner.vrow * block_size, block_size, block_size);
        ctx.fillRect(loser.vcol * block_size, loser.vrow * block_size, block_size, block_size);
        return;
    }

    ctx.fillStyle = hexToRgba(result_win, result_overlay_alpha * progress);
    ctx.fillRect(winner.vcol * block_size, winner.vrow * block_size, block_size, block_size);

    ctx.fillStyle = hexToRgba(result_lose, result_overlay_alpha * progress);
    ctx.fillRect(loser.vcol * block_size, loser.vrow * block_size, block_size, block_size);
}

function drawResultIcons() {
    if (!result_markers) {
        return;
    }

    const progress = getResultOverlayProgress();
    const scale = getResultIconScale(progress);

    const draw_icon = (cell, icon) => {
        if (!cell || !icon || !icon.complete) {
            return;
        }
        const { vrow, vcol } = toVisual(cell.row, cell.col);
        const max_size = 62;
        const icon_ratio = (icon.naturalWidth || 61) / (icon.naturalHeight || 54);
        const base_w = icon_ratio >= 1 ? max_size : max_size * icon_ratio;
        const base_h = icon_ratio >= 1 ? max_size / icon_ratio : max_size;
        const icon_w = base_w * scale;
        const icon_h = base_h * scale;
        const center_x = vcol * block_size + (block_size / 2);
        const center_y = vrow * block_size + (block_size / 2);
        const x = center_x - (icon_w / 2);
        const y = center_y - (icon_h / 2);
        ctx.save();
        ctx.globalAlpha = Math.min(1, progress * 1.15);
        ctx.drawImage(icon, x, y, icon_w, icon_h);
        ctx.restore();
    };

    if (result_markers.type === 'draw') {
        draw_icon(result_markers.winner, draw_icon_image);
        draw_icon(result_markers.loser, draw_icon_image);
        return;
    }

    draw_icon(result_markers.winner, crown_icon_image);
    draw_icon(result_markers.loser, flag_icon_image);
}

function drawPiece(img, vcol, vrow) {
    const max_size = block_size * 0.82;
    const ratio = img.naturalWidth / img.naturalHeight;
    const draw_w = ratio >= 1 ? max_size : max_size * ratio;
    const draw_h = ratio >= 1 ? max_size / ratio : max_size;
    const x = vcol * block_size + (block_size - draw_w) / 2;
    const y = vrow * block_size + (block_size - draw_h) / 2;
    ctx.drawImage(img, x, y, draw_w, draw_h);
}

function drawPieces() {
    const hide_row = piece_animation ? piece_animation.to.row : -1;
    const hide_col = piece_animation ? piece_animation.to.col : -1;

    for (let row = 0; row < board_size; row += 1) {
        for (let col = 0; col < board_size; col += 1) {
            if (row === hide_row && col === hide_col) {
                continue;
            }

            const piece = board[row][col];
            if (!piece || !piece_images[piece]) {
                continue;
            }
            const { vrow, vcol } = toVisual(row, col);
            drawPiece(piece_images[piece], vcol, vrow);
        }
    }
}

function drawAnimatedPiece() {
    if (!piece_animation || !piece_images[piece_animation.piece_code]) {
        return;
    }

    const progress = Math.min(1, (performance.now() - piece_animation.start_time) / piece_animation.duration);
    const eased = 1 - ((1 - progress) * (1 - progress));
    const row = piece_animation.from.row + ((piece_animation.to.row - piece_animation.from.row) * eased);
    const col = piece_animation.from.col + ((piece_animation.to.col - piece_animation.from.col) * eased);
    const visual = toVisual(row, col);
    drawPiece(piece_images[piece_animation.piece_code], visual.vcol, visual.vrow);
}

function drawArrow(from_col, from_row, to_col, to_row) {
    const from = toVisual(from_row, from_col);
    const to = toVisual(to_row, to_col);
    const from_x = from.vcol * block_size + block_size / 2;
    const from_y = from.vrow * block_size + block_size / 2;
    const to_x = to.vcol * block_size + block_size / 2;
    const to_y = to.vrow * block_size + block_size / 2;
    const angle = Math.atan2(to_y - from_y, to_x - from_x);
    const head_size = 28;
    const line_end_x = to_x - Math.cos(angle) * (head_size * 0.6);
    const line_end_y = to_y - Math.sin(angle) * (head_size * 0.6);

    ctx.save();
    ctx.strokeStyle = arrow_color;
    ctx.fillStyle = arrow_color;
    ctx.lineWidth = 10;
    ctx.lineCap = 'round';
    ctx.globalAlpha = 0.85;

    ctx.beginPath();
    ctx.moveTo(from_x, from_y);
    ctx.lineTo(line_end_x, line_end_y);
    ctx.stroke();

    ctx.translate(to_x, to_y);
    ctx.rotate(angle);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(-head_size, -head_size / 2.2);
    ctx.lineTo(-head_size, head_size / 2.2);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
}

function isMobileLayout() {
    return mobile_breakpoint.matches;
}

function setMobileMovesOpen(is_open) {
    if (!app_layout) {
        return;
    }
    app_layout.classList.toggle('mobile_moves_open', is_open);
}

function syncFirstMoveButtonIcon() {
    if (!first_move_icon) {
        return;
    }
    first_move_icon.src = isMobileLayout()
        ? `${asset_root}/icons/pgn_moves.svg`
        : `${asset_root}/icons/first.png`;
}

function setMobileMenuOpen(is_open) {
    if (!app_layout) {
        return;
    }
    app_layout.classList.toggle('mobile_menu_open', is_open);
    if (more_btn) {
        more_btn.classList.toggle('active', is_open);
    }
}

function syncMobileUiState() {
    const is_mobile = isMobileLayout();
    syncFirstMoveButtonIcon();
    if (!is_mobile) {
        setMobileMovesOpen(false);
        setMobileMenuOpen(false);
        was_mobile_layout = false;
        return;
    }

    if (!was_mobile_layout) {
        setMobileMovesOpen(true);
        setMobileMenuOpen(false);
        was_mobile_layout = true;
    }
}

function drawArrows() {
    for (const arrow of arrows) {
        drawArrow(arrow.from_col, arrow.from_row, arrow.to_col, arrow.to_row);
    }
}

function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawBoard();
    drawPieces();
    drawAnimatedPiece();
    drawResultOverlays();
    drawResultIcons();
    drawArrows();
}

function flipBoard() {
    is_flipped = !is_flipped;
    app_layout.classList.toggle('board_flipped', is_flipped);
    applyPlayerAvatars();
    render();
}

function getCellFromEvent(event) {
    const rect = canvas.getBoundingClientRect();
    const scale_x = canvas.width / rect.width;
    const scale_y = canvas.height / rect.height;
    const canvas_x = (event.clientX - rect.left) * scale_x;
    const canvas_y = (event.clientY - rect.top) * scale_y;
    const vcol = Math.floor(canvas_x / block_size);
    const vrow = Math.floor(canvas_y / block_size);
    return fromVisual(vrow, vcol);
}

function setupNavigation() {
    document.querySelector('.first_move_btn').addEventListener('click', () => {
        if (isMobileLayout()) {
            setMobileMovesOpen(!app_layout.classList.contains('mobile_moves_open'));
            return;
        }
        setPly(0, true);
    });
    document.querySelector('.prev_move_btn').addEventListener('click', () => setPly(current_ply - 1, true));
    document.querySelector('.next_move_btn').addEventListener('click', () => setPly(current_ply + 1, true));
    document.querySelector('.last_move_btn').addEventListener('click', () => {
        const game = getCurrentGame();
        if (game) {
            setPly(game.moves.length, true);
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'ArrowLeft') {
            setPly(current_ply - 1, true);
        } else if (event.key === 'ArrowRight') {
            setPly(current_ply + 1, true);
        } else if (event.key === 'Home') {
            setPly(0, true);
        } else if (event.key === 'End') {
            const game = getCurrentGame();
            if (game) {
                setPly(game.moves.length, true);
            }
        }
    });
}

function setupMobileButtons() {
    if (!more_btn) {
        return;
    }

    more_btn.addEventListener('click', () => {
        if (!isMobileLayout()) {
            return;
        }
        setMobileMenuOpen(!app_layout.classList.contains('mobile_menu_open'));
    });

    const mobile_menu_buttons = [
        document.getElementById('flip_board_btn'),
        history_btn,
        share_btn
    ];

    for (const button of mobile_menu_buttons) {
        if (!button) {
            continue;
        }
        button.addEventListener('click', () => {
            if (isMobileLayout()) {
                setMobileMenuOpen(false);
            }
        });
    }

    if (typeof mobile_breakpoint.addEventListener === 'function') {
        mobile_breakpoint.addEventListener('change', syncMobileUiState);
    } else {
        mobile_breakpoint.addListener(syncMobileUiState);
    }

    window.addEventListener('resize', syncMobileUiState);
    syncMobileUiState();
}

function requestFullscreenIfPossible() {
    if (document.fullscreenElement) {
        return;
    }

    const root = document.documentElement;
    const request = root.requestFullscreen
        || root.webkitRequestFullscreen
        || root.msRequestFullscreen;

    if (typeof request === 'function') {
        Promise.resolve(request.call(root)).catch(() => {});
    }
}

function setupAutoFullscreen() {
    requestFullscreenIfPossible();

    const on_first_interaction = () => {
        requestFullscreenIfPossible();
        window.removeEventListener('pointerdown', on_first_interaction);
        window.removeEventListener('touchstart', on_first_interaction);
        window.removeEventListener('click', on_first_interaction);
    };

    window.addEventListener('pointerdown', on_first_interaction, { once: true });
    window.addEventListener('touchstart', on_first_interaction, { once: true });
    window.addEventListener('click', on_first_interaction, { once: true });
}

function setupPanels() {
    history_btn.addEventListener('click', () => openPanel(history_panel));
    share_btn.addEventListener('click', () => {
        const game = getCurrentGame();
        share_pgn_text.value = game ? game.pgn_text : '';
        autoResizeShareTextarea();
        setShareStatus('', false);
        openPanel(share_panel);
    });
    submenu_overlay.addEventListener('click', closePanels);

    load_pgn_btn.addEventListener('click', () => {
        if (!chess_ready) {
            setShareStatus(ui_text.chess_library_not_ready, true);
            return;
        }

        const pgn_text = sanitizePgnInput(share_pgn_text.value);
        if (!pgn_text) {
            setShareStatus(ui_text.pgn_empty, true);
            return;
        }

        const parsed_game = parsePgnToGameState(pgn_text);
        if (!parsed_game) {
            setShareStatus(ui_text.pgn_invalid, true);
            return;
        }

        setShareStatus(ui_text.pgn_loaded, false);
        share_pgn_text.value = pgn_text;
        autoResizeShareTextarea();
        parsed_games.unshift(parsed_game);
        buildHistoryList();
        closePanels();
        loadGame(0);
    });

    share_pgn_text.addEventListener('input', autoResizeShareTextarea);
    window.addEventListener('resize', autoResizeShareTextarea);

    copy_pgn_btn.addEventListener('click', async () => {
        try {
            await copyTextToClipboard(share_pgn_text.value);
            setShareStatus(ui_text.pgn_copied, false);
        } catch (error) {
            setShareStatus(ui_text.copy_failed, true);
        }
    });
}

function initializeGames() {
    parsed_games = [];
    current_game_index = 0;
    current_ply = 0;
    highlighted_move_cells = null;
    piece_animation = null;
    clearResultVisuals();
    buildHistoryList();
    board = boardFromFen(start_fen);
    moves_scroll.innerHTML = '';
    render();
    updateTimers();
    app_layout.classList.remove('board_flipped');
    applyPlayerAvatars();
}

document.getElementById('flip_board_btn').addEventListener('click', flipBoard);
moves_scroll.addEventListener('scroll', updateScrollShadow);
new MutationObserver(updateScrollShadow).observe(moves_scroll, { childList: true, subtree: true });
window.addEventListener('resize', updateScrollShadow);

canvas.addEventListener('contextmenu', (event) => event.preventDefault());

canvas.addEventListener('mousedown', (event) => {
    if (event.button !== 2) {
        return;
    }
    right_drag_start = getCellFromEvent(event);
});

canvas.addEventListener('mouseup', (event) => {
    if (event.button !== 2 || !right_drag_start) {
        return;
    }

    const { row, col } = getCellFromEvent(event);

    if (row === right_drag_start.row && col === right_drag_start.col) {
        const key = `${row},${col}`;
        if (marked_cells.has(key)) {
            marked_cells.delete(key);
        } else {
            marked_cells.add(key);
        }
    } else {
        const existing = arrows.findIndex((arrow) => (
            arrow.from_row === right_drag_start.row
            && arrow.from_col === right_drag_start.col
            && arrow.to_row === row
            && arrow.to_col === col
        ));

        if (existing >= 0) {
            arrows.splice(existing, 1);
        } else {
            arrows.push({
                from_row: right_drag_start.row,
                from_col: right_drag_start.col,
                to_row: row,
                to_col: col
            });
        }
    }

    right_drag_start = null;
    render();
});

canvas.addEventListener('click', () => {
    marked_cells.clear();
    arrows = [];
    render();
});

loadNoise(() => {
    loadPieceImages(async () => {
        chess_ready = await loadChessLibrary();
        setupNavigation();
        setupMobileButtons();
        setupAutoFullscreen();
        setupPanels();
        initializeGames();
        updateScrollShadow();
    });
});
