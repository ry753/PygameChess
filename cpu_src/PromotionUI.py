import pygame
#====================================================================

# プロモーション実行時のUI表示

#====================================================================
class PromotionUI:
    # ==================================
    # コンストラクタ
    # ==================================
    def __init__(self, screen, board_size):
        """
        引数：
            screen, チェスのスクリーンウィンドウ
            board_size, スクリーンウィンドウ内のチェス盤のサイズ
        """
        self.screen = screen
        self.board_size = board_size

    # ==================================
    # メソッド
    # ==================================
    def promotion_ui_render(self):
        """
        プロモーション処理の際のUIを描画する
        引数；
            なし
        戻り値：
            ボタン定義のリスト
        """
        # 成る駒を選択するためのUIを表示
        queen_button   = pygame.Rect(675, 100, 100, 50) # ...Rect(X座標、Y座標、ボタン横幅、ボタン立幅)
        knight_button  = pygame.Rect(675, 170, 100, 50) # ...Rect(X座標、Y座標、ボタン横幅、ボタン立幅)
        rook_button    = pygame.Rect(675, 240, 100, 50) # ...Rect(X座標、Y座標、ボタン横幅、ボタン立幅)
        bishop_button  = pygame.Rect(675, 310, 100, 50) # ...Rect(X座標、Y座標、ボタン横幅、ボタン立幅)
        queen_font     = pygame.font.Font(None, 30)
        knight_font    = pygame.font.Font(None, 30)
        rook_font      = pygame.font.Font(None, 30)
        bishop_font    = pygame.font.Font(None, 30)
        
        # クイーンボタン
        pygame.draw.rect(self.screen, (250, 250, 250), queen_button)
        queen_text = queen_font.render("Queen", True, (10, 10, 10))
        queen_text_rect = queen_text.get_rect(center=queen_button.center) # 文字を中心に
        self.screen.blit(queen_text, queen_text_rect)
        # ナイトボタン
        pygame.draw.rect(self.screen, (250, 250, 250), knight_button)
        knight_text = knight_font.render("Knight", True, (10, 10, 10))
        knight_text_rect = knight_text.get_rect(center=knight_button.center) # 文字を中心に
        self.screen.blit(knight_text, knight_text_rect)
        # ルークボタン
        pygame.draw.rect(self.screen, (250, 250, 250), rook_button)
        rook_text = rook_font.render("Rook", True, (10, 10, 10))
        rook_text_rect = rook_text.get_rect(center=rook_button.center) # 文字を中心に
        self.screen.blit(rook_text, rook_text_rect)
        # ビショップボタン
        pygame.draw.rect(self.screen, (250, 250, 250), bishop_button)
        bishop_text = bishop_font.render("Bishop", True, (10, 10, 10))
        bishop_text_rect = bishop_text.get_rect(center=bishop_button.center) # 文字を中心に
        self.screen.blit(bishop_text, bishop_text_rect)

        # ボタン描画
        pygame.display.update()

        # ボタン定義を返す
        buttons = [queen_button, knight_button, rook_button, bishop_button]
        return buttons