import sys
import pygame
from MoveCalculator import MoveCalculator
#====================================================================

# 駒の移動実行、アンパッサンなどの特殊ルール実行

#====================================================================
class MoveExecutor:
    # ==================================
    # コンストラクタ
    # ==================================
    def __init__(self, promotion_ui):
        """
        引数：
            promotion_ui, プロモーション処理のUIを表示するクラス
        """
        # プロモーション処理のUIを表示するクラス
        self.promotion_ui = promotion_ui
        # 移動の実行を行うクラス（キャスリングフラグを参照する用）
        self.move_calculator = MoveCalculator()

    # ==================================
    # メソッド
    # ==================================
    def move_common(self, curr_board, from_cell, dest_cell, piece, castling_flag):
        """
        ポーン以外の移動処理を行う
        引数：
            curr_board, 現在の盤状況
            from_cell, 駒の移動元セル(Y, X)
            dest_cell, 駒の移動先セル(Y, X)
            piece, 駒本体
            castling_flag, キャスリングができるかどうかのフラグ（Bool）
        戻り値：
            なし
        """
        # 出発セルと移動先セルの座標を取得
        fromY, fromX = from_cell
        destY, destX = dest_cell

        # キャスリングができる状態でキングが特定のセルに移動していたら
        # キャスリングを実行して終了する
        if (castling_flag) and piece == "wK":
            if ((destY, destX) == (7, 6)) or ((destY, destX) == (7, 2)):
                self.castling_exe(curr_board, destY, destX, piece)
                return
        elif (castling_flag) and piece == "bK":
            if ((destY, destX) == (0, 6)) or ((destY, destX) == (0, 2)):
                self.castling_exe(curr_board, destY, destX, piece)
                return
        
        # 出発セルを空にして移動先セルに移動
        curr_board[fromY][fromX] = 0
        curr_board[destY][destX] = piece

        return
    
    def move_pawn(self, curr_board, from_cell, dest_cell, piece, turn):
        """
        ポーンの移動処理を行う
        引数：
            curr_board, 現在の盤状況
            from_cell, 駒の移動元セル(Y, X)
            dest_cell, 駒の移動先セル(Y, X)
            piece, 駒本体
            turn, 現在の手番
        戻り値：
            なし
        """
        # 出発セルと移動先セルの座標を取得
        fromY, fromX = from_cell
        destY, destX = dest_cell
        
        # ポーンが横方向に移動し、移動先が空の場合、アンパッサン処理を行う
        if (fromX != destX) and (curr_board[destY][destX] == 0):
            self.enpassan_exe(curr_board, fromY, destX)

        # 移動先が最終行（０か７）であればプロモーション処理を行う
        if (destY == 0) or (destY == 7):
            piece = self.promotion_exe(turn)

        # 出発セルを空にして移動先セルに移動
        curr_board[fromY][fromX] = 0
        curr_board[destY][destX] = piece

        return


    def enpassan_exe(self, curr_board, fromY, destX):
        """
        アンパッサン処理
        アンパッサンによる移動が行われた後に、後ろの駒をとる
        引数：
            curr_board, 現在の盤状況
            fromY, 移動開始セルの行
            destX, 移動先セルの列
        戻り値：
            なし
        """
        curr_board[fromY][destX] = 0
        return
    

    def castling_exe(self, curr_board, destY, destX, piece):
        """
        キャスリング処理
        引数：
            curr_board, 現在の盤状況
            destY, 移動先セルの行
            destX, 移動先セルの列
            piece, 駒の本体（wKかwB）
        戻り値：
            なし
        """
        # 白のキャスリング処理
        if piece == "wK":
            if (destY, destX) == (7, 6):
                curr_board[7][4] = 0
                curr_board[7][7] = 0
                curr_board[7][6] = "wK"
                curr_board[7][5] = "wR"
                return
            if (destY, destX) == (7, 2):
                curr_board[7][4] = 0
                curr_board[7][0] = 0
                curr_board[7][2] = "wK"
                curr_board[7][3] = "wR"
                return
        # 黒のキャスリング処理
        else:
            if (destY, destX) == (0, 6):
                curr_board[0][4] = 0
                curr_board[0][7] = 0
                curr_board[0][6] = "bK"
                curr_board[0][5] = "bR"
                return
            if (destY, destX) == (0, 2):
                curr_board[0][4] = 0
                curr_board[0][0] = 0
                curr_board[0][2] = "bK"
                curr_board[0][3] = "bR"
                return            
    

    def promotion_exe(self, turn):
        """
        プロモーション処理の実行
        引数；
            turn, 現在の手番
        戻り値：
            str, 駒の種類（"wK"）
        """
        # UIの描画
        buttons = self.promotion_ui.promotion_ui_render()

        # 返されたボタン定義を取得
        queen_button  = buttons[0]
        knight_button = buttons[1]
        rook_button   = buttons[2]
        bishop_button = buttons[3]

        # 選択を待つ
        while True:
            for event in pygame.event.get():
                # 強制終了
                if event.type == pygame.QUIT:
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if queen_button.collidepoint(event.pos):
                        if turn:return "wQ"
                        else:   return "bQ"
                    if knight_button.collidepoint(event.pos):
                        if turn:return "wN"
                        else:   return "bN"
                    if rook_button.collidepoint(event.pos):
                        if turn:return "wR"
                        else:   return "bR"
                    if bishop_button.collidepoint(event.pos):
                        if turn:return "wB"
                        else:   return "bB"