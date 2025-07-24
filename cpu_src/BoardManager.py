#====================================================================

# 盤面データの保持、初期化を行う

#====================================================================
class BoardManager:
    # ==================================
    # コンストラクタ
    # ==================================
    def __init__(self):
        """
        引数：
            なし
        """
        # 盤の初期状況
        self.init_board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        # 操作用の盤
        self.curr_board = [row[:] for row in self.init_board]

    # ==================================
    # メソッド
    # ==================================
    def reset_board(self):
        """
        初期配置への盤面リセットを行う
        引数：
            なし
        戻り値：
            なし
        """
        self.curr_board = [row[:] for row in self.init_board]
        return
    

    def get_piece(self, cellY, cellX, curr_board):
        """
        指定セルの駒が何かを返す
        引数：
            cellY, クリックされたセルのY座標
            cellX, クリックされたセルのX座標
            curr_board, 現在の盤状況
        戻り値：
            0か駒（"wK"）
        """
        # ボード範囲内かチェック
        if (0 <= cellY <= 7) and (0 <= cellX <= 7):
            return curr_board[cellY][cellX]
        else:
            return 0