#====================================================================

# 手番の履歴保存、アンパッサン用ログ管理

#====================================================================
class Logger:
    # ==================================
    # コンストラクタ
    # ==================================
    def __init__(self):
        """
        引数：
            なし
        """
        # ゲーム全体のログ
        self.game_log = []
        # どの駒が動いたかのログ
        self.moved_pieces_log = []
        # アンパッサン処理用のログ
        self.enpassant_log = {
            "from"    : (0, 0), # 移動元
            "dest"    : (0, 0), # 移動先
            "two_step": False   # ２マス進んだか
        }

    # ==================================
    # メソッド
    # ==================================
    def save_log(self, piece, from_cell, dest_cell):
        """
        移動ログの記録を行う
        引数：
            piece, 駒の種類
            from_cell, 移動開始セル(Y, X)
            dest_cell, 移動先セル(Y, X)
        戻り値：
            なし
        """
        self.game_log.append(f"piece:({piece}), from:{from_cell}, to:{dest_cell}")
        # print(self.game_log)
        self.moved_pieces_log.append(piece) # 駒の移動ログも残す
        return
    
    
    def save_enpassant_log(self, from_cell, dest_cell):
        """
        アンパッサン処理用のログの記録
        引数：
            piece, 駒の種類
            from_cell, 移動開始セル(Y, X)
            dest_cell, 移動先セル(Y, X)
        戻り値：
            なし
        """
        # 出発セルと移動先セルの情報を記録
        self.enpassant_log["from"] = from_cell
        self.enpassant_log["dest"] = dest_cell

        # ポーンがY軸上を２マス進んでいたら、two_stepをTrueにする
        if abs(dest_cell[0] - from_cell[0]) == 2:
            self.enpassant_log["two_step"] = True
        else:
            self.enpassant_log["two_step"] = False
        # print(self.enpassant_log)
        return
    

    def reset_log(self):
        """
        すべてのログの初期化
        引数；
            なし
        戻り値：
            なし
        """
        self.game_log = []
        self.enpassant_log = {
            "from"    : (0, 0),
            "dest"    : (0, 0),
            "two_step": False
        }
        self.moved_pieces_log = []
        
        return