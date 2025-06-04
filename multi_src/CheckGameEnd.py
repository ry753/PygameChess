#====================================================================

# チェック、チェックメイト、ステルスメイトの判定

#====================================================================
class CheckGameEnd:
    # ==================================
    # メソッド
    # ==================================
    def is_check(self, curr_board, turn):
        """
        チェックされていないかのチェックを行う
        チェックされていたらTrue, されていなかったらFalseを返す
        引数；
            curr_board, 現在の盤状況
            turn, 現在の手番
        戻り値：
            bool
        """
        # 手番で処理が変わる
        if turn:
            ally  = "w"
            enemy = "b"
        else:
            ally  = "b"
            enemy = "w"

        # キングの位置を取得
        found = False
        for y in range(0, 8):
            for x in range(0, 8):
                if (ally == "w") and (curr_board[y][x] == "wK"):
                    kingY, kingX = y, x
                    found = True
                    break
                elif (ally == "b") and (curr_board[y][x] == "bK"):
                    kingY, kingX = y, x
                    found = True
                    break

            if found:
                break

        # チェックされていると１になるフラグ
        is_check_flag = 0

        # キングを攻撃可能な敵駒がないか１種類ずつチェックする
        # ポーンからの攻撃
        if ally == "w": pawn_attack = [(-1, 1), (-1, -1)]
        else:           pawn_attack = [(1, 1), (1, -1)]
        # 敵ポーンが移動できるセルにキングがないかをチェックする
        for atkY, atkX in pawn_attack:
            tmpY = kingY + atkY
            tmpX = kingX + atkX
            if (0 <= tmpY <= 7) and (0 <= tmpX <= 7):
                if curr_board[tmpY][tmpX] == enemy + "P":
                    is_check_flag = 1
        
        # ナイトからの攻撃
        knight_attack = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
        for atkY, atkX in knight_attack:
            tmpY = kingY + atkY
            tmpX = kingX + atkX
            if (0 <= tmpY <= 7) and (0 <= tmpX <= 7):
                if curr_board[tmpY][tmpX] == enemy + "N":
                    is_check_flag = 1
                
        # クイーン、ルークからの直線攻撃
        rook_attack = [(1, 0), (-1, 0), (0, -1), (0, 1)]
        for atkY, atkX in rook_attack:
            tmpY = kingY + atkY
            tmpX = kingX + atkX
            while (0 <= tmpY <= 7) and (0 <= tmpX <= 7):
                cell = curr_board[tmpY][tmpX]
                if cell != 0:
                    if (cell[0] == enemy) and (cell[1] in("R", "Q")):
                        is_check_flag = 1
                    else:
                        break
                tmpY += atkY
                tmpX += atkX
        
        # クイーン、ビショップからの斜め攻撃
        bishop_attack = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
        for atkY, atkX in bishop_attack:
            tmpY = kingY + atkY
            tmpX = kingX + atkX
            while (0 <= tmpY <= 7) and (0 <= tmpX <= 7):
                cell = curr_board[tmpY][tmpX]
                if cell != 0:
                    if (cell[0] == enemy) and (cell[1] in("B", "Q")):
                        is_check_flag = 1
                    else:
                        break
                tmpY += atkY
                tmpX += atkX

        if is_check_flag == 1:
            return True
        else:
            return False
    

    def is_checkmate(self, curr_board, turn, prev_log, my_color, moved_pieces):
        """
        チェックメイトの判定を行う
        チェックメイトならTrueを返す
        引数；
            curr_board, 現在の盤状況
            turn, 現在の手番
            prev_log, アンパッサン処理用の一手前の移動ログ
            my_color, マルチプレイ時の自分の色
            moved_pieces, 動いた駒のログ
        戻り値：
            bool
        """
        # まずはキングがチェックされているか
        if not self.is_check(curr_board, turn):
            return
        # 合法手を計算する
        # 自分の駒のすべての移動パターンを試し、チェックが外れるかを試す
        ret, _ = self.check_legal_moves(curr_board, turn, prev_log, my_color, moved_pieces)
        if ret:
            return False

        return True
    

    def check_legal_moves(self, curr_board, turn, prev_log, my_color, moved_pieces):
        """
        合法手をがあるかどうかを確認する
        合法手が存在すればTrueを返す
        引数；
            curr_board, 現在の盤状況
            turn, 現在の手番
            prev_log, アンパッサン処理用の一手前の移動ログ
            my_color, マルチプレイ時の自分の色
            moved_pieces, 動いた駒のログ
        戻り値：
            bool
            legal_mobiles, 合法手のリスト
        """
        # 移動先計算用クラス
        from MoveCalculator import MoveCalculator
        move_calculator = MoveCalculator()

        # 合法手となる移動先リスト
        legal_mobiles = []

        # まずは味方駒の把握
        if turn: allies = "w"
        else:    allies = "b"
        # 味方駒の探索
        for r_idx, row in enumerate(curr_board):
            for c_idx, cell in enumerate(row):
                # 味方駒を発見したら、その駒の移動先をすべて試して
                # チェックが外れるかを確認する
                if (cell != 0) and (cell[0] == allies):
                    if (cell[1] == "P"):
                        mobiles = move_calculator.calc_pawn_moves(curr_board, r_idx, c_idx, prev_log, turn, my_color)
                    else:
                        mobiles = move_calculator.calc_common_moves(curr_board, r_idx, c_idx, cell, turn, moved_pieces) 
                    # 移動先が得られなければスキップ
                    if len(mobiles) == 0:
                        continue
                    # 計算用の盤を生成して１手先をシュミレーションする
                    for destY, destX in mobiles:
                        tmp_board = [row[:] for row in curr_board]
                        tmp_board[r_idx][c_idx] = 0
                        tmp_board[destY][destX] = cell
                        # チェックが外れればその移動先座標を保存
                        if not self.is_check(tmp_board, turn):
                            legal_mobiles.append((destY, destX))

        # 合法手があればTrue
        if len(legal_mobiles) > 0:
            return True, legal_mobiles
        else:
            return False, None


    def is_stalemate(self, curr_board, turn, prev_log, my_color, moved_pieces):
        """
        ステルスメイトのチェックを行う
        ステルスメイトであればTrueを返す
        my_color, マルチプレイ時の自分の色
        引数；
            curr_board, 現在の盤状況
            turn, 現在の手番
            prev_log, アンパッサン処理用の一手前の移動ログ
            my_color, マルチプレイ時の自分の色
            moved_pieces, 動いた駒のログ
        戻り値：
            bool
        """
        # 移動先計算用クラス
        from MoveCalculator import MoveCalculator
        move_calculator = MoveCalculator()

        # 自分のキングがチェックされていないことを確認
        if self.is_check(curr_board, turn):
            return False
        
        # 味方駒が動かせるかを確認。
        # また、後の処理で使うため、敵味方関係なく存在する駒のリストも取っておく。
        exist_pieces   = [] # 存在する駒のリスト
        stalemate_flag = 1  # ステルスメイトのフラグ。ステルスメイトだと１になる
        # 味方駒の把握
        if turn: allies = "w"
        else:    allies = "b"
        # 味方駒の探索
        for r_idx, row in enumerate(curr_board):
            for c_idx, cell in enumerate(row):
                # 敵味方関係なく駒を発見したら、リストへ
                if cell != 0:
                    exist_pieces.append(cell)
                    # 味方駒を発見したら、移動先を計算
                    if cell[0] == allies:
                        if (cell[1] == "P"):
                            mobiles = move_calculator.calc_pawn_moves(curr_board, r_idx, c_idx, prev_log, turn, my_color)
                        else:
                            mobiles = move_calculator.calc_common_moves(curr_board, r_idx, c_idx, cell, turn, moved_pieces) 
                        # 移動先がある駒を発見したら、フラグを0に
                        if len(mobiles) > 0:
                            stalemate_flag = 0
        
        # 駒不足によるステルスメイト１
        # 両陣営キングだけ
        if len(exist_pieces) == 2:
            stalemate_flag = 1

        # 駒不足によるステルスメイト２
        # キング：キング＋ナイト
        if len(exist_pieces) == 3:
            if set(exist_pieces) == {"wK", "bK", "wN"}: 
                stalemate_flag = 1

        # 駒不足によるステルスメイト３
        # キング：キング＋ビショップ
        if len(exist_pieces) == 3:
            if set(exist_pieces) == {"wK", "bK", "wB"}: 
                stalemate_flag = 1

        # 駒不足によるステルスメイト４
        # キング＋ビショップ：キング＋ビショップ
        if len(exist_pieces) == 4:
            if set(exist_pieces) == {"wK", "wB", "bK", "bB"}: 
                stalemate_flag = 1

        # 最終判定
        if stalemate_flag == 1:
            return True
        else:
            return False