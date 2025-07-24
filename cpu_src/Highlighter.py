import pygame
#====================================================================

# 移動可能セルに色を付ける

#====================================================================
class Highlighter:
    # ==================================
    # クラス変数
    # ==================================

    # ==================================
    # コンストラクタ
    # ==================================
    def __init__(self, screen, piece_size):
        """
        引数：
            screen, スクリーンウィンドウ
            piece_size, # 駒（セル）のサイズ
        """
        self.screen = screen
        self.piece_size = piece_size

    # ==================================
    # メソッド
    # ==================================
    def highlight_mobiles(self, mobiles):
        """
        移動可能セルを色付け表示する
        引数：
            mobiles, 移動可能セルのリスト
        戻り値：
            スクリーンウィンドウ
        """
        # 色のサイズ定義
        scale = 0.4
        highlight_size = int(self.piece_size * scale)

        # ハイライトオブジェクトの生成
        highlight = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
        highlight.fill((0, 0, 255, 120))

        # マスの中央にするためのオフセット計算
        offset = int((self.piece_size - highlight_size) / 2)

        # ハイライトオブジェクトの描画
        for (y, x) in mobiles:
            hl_y = y * self.piece_size + offset
            hl_x = x * self.piece_size + offset
            self.screen.blit(highlight, (hl_x, hl_y))
        
        return self.screen