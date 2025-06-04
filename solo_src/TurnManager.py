#====================================================================

# 手番の管理、手番違反のチェック

#====================================================================
class TurnManager:
    # ==================================
    # コンストラクタ
    # ==================================
    def __init__(self):
        """
        引数：
            my_turn, 自分の色（whiteかblack）
        """
        # 手番（Trueが白、Falseが黒）
        self.turn = True

    # ==================================
    # メソッド
    # ==================================
    def switch_turn(self):
        """
        手番の切換を行う
        引数；
            なし
        戻り値：
            なし
        """
        if self.turn:
            self.turn = False
        else:
            self.turn = True
        return
        

    def check_valid_turn(self, cell):
        """
        駒の色と手番の一致チェックを行う
        黒手番なのに白を触る、白手番なのに黒を触るのが手番違反
        引数：
            cell, クリックされた駒の種類
        戻り値：
            bool, 手番違反ならFalseを返す
        """
        if self.turn and cell[0] == "b":
            return False
        elif not self.turn and cell[0] == "w":
            return False
        else:
            return True
        
    def reset_turn(self):
        """
        手番を白からに戻す
        引数；
            なし
        戻り値：
            なし
        """
        self.turn = True
        return