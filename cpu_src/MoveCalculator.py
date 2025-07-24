#====================================================================

# 駒ごとの移動可能マスの計算を行う
# キャスリングが実行可能かの判定も行う

#====================================================================
class MoveCalculator:
    # ==================================
    # クラス変数
    # ==================================

    # ==================================
    # コンストラクタ
    # ==================================
    def __init__(self):
        """
        引数：
            なし
        """
        # キャスリングができるかどうかの判定
        self.castling_flag = False

    # ==================================
    # メソッド
    # ==================================
    def calc_common_moves(self, curr_board, fromY, fromX, piece, turn, moved_pieces):
        """
        キング・クイーン・ナイト・ビショップ・ルークの移動先計算を行い、
        リストで返す
        引数：
            curr_board, 現在の盤状況
            fromY, クリックされたセルのY座標（移動開始地点）
            fromX, クリックされたセルのX座標（移動開始地点）
            piece, 駒の種類
            trun, 現在の手番
            moved_pieces, 動いた駒のログ
        戻り値：
            mobiles, 移動可能セルのリスト
        """
        # 最終的に返す移動可能セルリスト
        mobiles = []
        # 敵駒と味方駒の取得
        allies, enemies = self.get_allies_enemies(turn)
        # 駒の種類から最大移動数と移動ベクトルを取得
        maxstep, vectors = self.get_maxstep_vectors(piece)

        # 最大移動数分、空のマスを探索し、mobilesにまとめる
        # 敵駒にぶつかるとそのマスを含み、探索を止める。（キングのセルは含めない）
        # vectは移動のベクトルの方向、destは移動先セルの座標を示す
        for vectY, vectX in vectors:
            for step in range(1, maxstep+1):
                # 移動先 = 現在座標 + 方向*進む回数
                destY = fromY + vectY*step
                destX = fromX + vectX*step
                # 盤外にぶつかるとこの方向への移動は終了
                if not (0 <= destY <= 7) or not (0 <= destX <= 7):
                    break
                # セルの中身を取得
                cell = curr_board[destY][destX]
                # 自駒がいたら終了
                if cell in allies:
                    break
                # 敵駒がいたら、そのマスを含めて終了
                # ただし、キングの場合は含めない
                if cell in enemies:
                    if cell[1] != "K":
                        mobiles.append((destY, destX))
                    break
                # 何もないマスはそのままリストへ
                mobiles.append((destY, destX))
            
        # キングの移動であればキャスリングができるかの判定も行う
        # また、キングの移動先セルが敵駒にチェックされてしまうマスの場合、そこには移動できないので排除する
        if (piece[1] == "K"):
            mobiles = self.calc_castling(mobiles, curr_board, turn, moved_pieces)
            mobiles = self.delete_danger_cell(mobiles, curr_board, fromY, fromX, piece, turn)

        return mobiles
    
    
    def get_allies_enemies(self, turn):
        """
        手番に基づいて敵駒と味方駒のリストを返す
        引数：
            turn, 現在の手番
        戻り値：
            allies, 味方駒のリスト
            enemies, 敵駒のリスト
        """
        if turn:
            allies  = ["wK", "wQ", "wN", "wB", "wR", "wP"]
            enemies = ["bK", "bQ", "bN", "bB", "bR", "bP"]
        else:
            allies  = ["bK", "bQ", "bN", "bB", "bR", "bP"]
            enemies = ["wK", "wQ", "wN", "wB", "wR", "wP"]

        return allies, enemies
    
    
    def get_maxstep_vectors(self, piece):
        """
        駒の種類に基づいて最大移動数と移動ベクトルを返す
        引数：
            piece, 駒の種類
        戻り値：
            int, 駒の最大移動可能回数
            vectors, 駒の進行方向リスト
        """
        # 移動ベクトルの定義
        rook_vectors   = [(1, 0), (-1, 0), (0, -1), (0, 1)]
        bishop_vectors = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
        knight_vectors = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
        all_vectors    = rook_vectors + bishop_vectors

        if   piece[1] == "K":
            return 1, all_vectors
        elif piece[1] == "Q":
            return 7, all_vectors
        elif piece[1] == "N":
            return 1, knight_vectors
        elif piece[1] == "B":
            return 7, bishop_vectors
        elif piece[1] == "R":
            return 7, rook_vectors
        
        
    def calc_castling(self, mobiles, curr_board, turn, moved_pieces):
        """
        キャスリングができるかどうかの判定
        引数：
            mobiles, 移動可能セルのリスト
            curr_board, 現在の盤状況
            moved_pieces, 過去に動いた駒のログ
        戻り値；
            mobiles, キャスリングでの移動先を含めた移動可能セルのリスト（含めない場合もある）
        """
        # チェック判定用クラス
        from CheckGameEnd import CheckGameEnd
        check_game_end = CheckGameEnd()
        
        # チェックされていないかの判定
        if check_game_end.is_check(curr_board, turn):
            return mobiles
        
        # キングとルークが初期位置から一度も動いていないか
        # キングとルークの間に駒がないか
        if turn and (not "wK" in moved_pieces):
            if (curr_board[7][0] == "wR") and (curr_board[7][4] == "wK"):
                if (curr_board[7][1] == 0) and (curr_board[7][2] == 0) and (curr_board[7][3] == 0):
                    mobiles.append((7, 2))
                    self.castling_flag = True
            if (curr_board[7][7] == "wR") and (curr_board[7][4] == "wK"):
                if (curr_board[7][5] == 0) and (curr_board[7][6] == 0):
                    mobiles.append((7, 6))
                    self.castling_flag = True
        elif (not turn) and (not "bK" in moved_pieces):
            if (curr_board[0][0] == "bR") and (curr_board[0][4] == "bK"):
                if (curr_board[0][1] == 0) and (curr_board[0][2] == 0) and (curr_board[0][3] == 0):
                    mobiles.append((0, 2))
                    self.castling_flag = True
            if (curr_board[0][7] == "bR") and (curr_board[0][4] == "bK"):
                if (curr_board[0][5] == 0) and (curr_board[0][6] == 0):
                    mobiles.append((0, 6))
                    self.castling_flag = True

        return mobiles
    

    def delete_danger_cell(self, mobiles, curr_board, fromY, fromX, piece, turn):
        """
        移動可能先セルリストのうち、進むとチェックされてしまうセルを省く
        新しいリストを追加し、チェックされないセルを新リストに追加する
        引数：
            mobiles, 移動可能セルのリスト
            curr_board, 現在の盤状況
            fromY, キングのスタート地点Y
            fromX, キングのスタート地点X
            piece, 駒の本体（wKかbK)
            turn, 現在の手番
        戻り値：
            safe_mobiles, 進めないセルを除いた移動可能セルのリスト
        """
        # チェック判定用クラス
        from CheckGameEnd import CheckGameEnd
        check_game_end = CheckGameEnd()

        # 最終的に返す移動可能先リスト
        safe_mobiles = []

        # 移動可能セルに移動した場合をシュミレーションする
        for destY, destX in mobiles:
            # 現在の盤面をコピーして移動
            tmp_board = [row[:] for row in curr_board]
            tmp_board[fromY][fromX] = 0
            tmp_board[destY][destX] = piece

            # 移動先に移動してチェックされるならスキップ
            if check_game_end.is_check(tmp_board, turn):
                continue
            # 移動可能先として改めて追加
            safe_mobiles.append((destY, destX))
        
        return safe_mobiles
        

    def calc_pawn_moves(self, curr_board, fromY, fromX, prev_log, turn):
        """
        ポーンの移動先計算を行い、リストで返す
        引数：
            curr_board, 現在の盤状況
            fromY, クリックされたセルのY座標（移動開始地点）
            fromX, クリックされたセルのX座標（移動開始地点）
            piece, 駒の種類
            prev_log, １手前にどの駒がどこに動いたかのログ（アンパッサン処理用）
            turn, 現在の手番
        戻り値：
            mobiles, ポーンの移動可能セルのリスト
        """
        # 手番で処理を変える
        if turn:
            forword   = -1 # 白ポーンの進行方向は負
            start_row = 6  # 白ポーンの開始行
            enemies   = ["bQ", "bN", "bB", "bR", "bP"]
        else:
            forword   = 1  # 黒ポーンの進行方向は負
            start_row = 1  # 黒ポーンの開始行
            enemies   = ["wQ", "wN", "wB", "wR", "wP"]

        # 最終的に返す移動可能セルのリスト
        mobiles = []
        # １つ先のセルと２つ先のセル
        one_ahead = fromY + forword
        two_ahead = fromY + forword*2

        # １歩先の確認。移動先が盤内かつ空であれば進める
        if (0 <= one_ahead <= 7) and (curr_board[one_ahead][fromX] == 0):
            mobiles.append((one_ahead, fromX))
            # ２歩先の確認（１歩先に進めるうえで開始行にいる必要がある）
            if (fromY == start_row) and (curr_board[two_ahead][fromX] == 0):
                mobiles.append((two_ahead, fromX))

        # 斜め前に敵がいれば進める
        if (0 <= one_ahead <= 7) and (0 <= fromX+1 <= 7):
            if curr_board[one_ahead][fromX+1] in enemies:
                mobiles.append((one_ahead, fromX+1))
        if (0 <= one_ahead <= 7) and (0 <= fromX-1 <= 7):
            if curr_board[one_ahead][fromX-1] in enemies:
                mobiles.append((one_ahead, fromX-1))

        # アンパッサンでの移動先確認
        # 直前に動かされたポーンが、２マス進んでいたかをチェックする
        if prev_log["two_step"]:
            # どのセルに動いたか座標を取得
            prevY, prevX = prev_log["dest"]
            # １つ前に動いた敵ポーンが同じ行にいて、隣接していたらアンパッサン可能
            if (prevY == fromY) and (abs(prevX - fromX) == 1):
                mobiles.append((one_ahead, prevX))

        return mobiles