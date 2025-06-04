import pygame
#====================================================================

# 画像の読み込み、リサイズ、描画を行う

#====================================================================
class Renderer:
    # ==================================
    # コンストラクタ
    # ==================================
    def __init__(self, screen, board_size, piece_size):
        """
        引数：
            screen, スクリーンウィンドウの実体
            board_size, 盤のサイズ
            piece_size, 駒のサイズ
        """
        # 引数の受け取り
        self.screen     = screen
        self.board_size = board_size
        self.piece_size = piece_size
        # フレームレート管理用のClockオブジェクト
        self.clock  = pygame.time.Clock()

        # 駒の名称と画像名の辞書
        self.piece_files = {
            "bK": "black-king.png"  , "wK": "white-king.png",
            "bQ": "black-queen.png" , "wQ": "white-queen.png",
            "bN": "black-knight.png", "wN": "white-knight.png",
            "bB": "black-bishop.png", "wB": "white-bishop.png",
            "bR": "black-rook.png"  , "wR": "white-rook.png",
            "bP": "black-pawn.png"  , "wP": "white-pawn.png"
        }

        # 盤画像の読み込み・リサイズ
        self.board_img = pygame.image.load("./image/board.png")
        self.board_img = pygame.transform.scale(self.board_img, (self.board_size, self.board_size))
        # 駒画像の読み込み・リサイズ
        self.pieces = {}
        for key, file_name in self.piece_files.items():
            piece_img = pygame.image.load(f"./image/{file_name}")
            self.pieces[key] = pygame.transform.scale(piece_img, (self.piece_size, self.piece_size))

    # ==================================
    # メソッド
    # ==================================
    def draw_board(self, screen):
        """
        盤面の描画
        引数：
            screen, チェスのウィンドウ
        戻り値：
            screen, 更新したチェスのウィンドウ
        """
        screen.blit(self.board_img, (0,0))
        return screen
    
    
    def draw_pieces(self, screen, curr_board):
        """
        駒の描画
        引数：
            screen, チェスのウィンドウ
            curr_board, 現在の盤状況
        戻り値：
            screen, 更新したチェスのウィンドウ
        """
        for r_idx, row in enumerate(curr_board):
            for c_idx, cell in enumerate(row):
                if cell != 0:
                    location = (c_idx*self.piece_size, r_idx*self.piece_size)
                    screen.blit(self.pieces[cell], location)
        return  screen
    

    def draw_ui(self, screen, screen_width, board_size, restart_btn, turn, multi):
        """
        手番表示やリスタートボタンなどのUI描画
        引数：
            screen, チェスのウィンドウ
            screen_width, ウィンドウの横幅
            board_size, ウィンドウ内のチェス盤のサイズ
            restart_btn, リスタートボタンの実体
            turn, 現在の手番
            multi, マルチプレイかどうかのフラグ
        戻り値：
            screen, 更新したチェスのウィンドウ
        """
        # フォントの初期設定
        turn_font    = pygame.font.Font(None, 30)

        # リスタートボタンのセット
        # マルチプレイ時はボタンをつけない
        if not multi:
            restart_font = pygame.font.Font(None, 30)
            pygame.draw.rect(screen, (100, 230, 100), restart_btn)
            restart_surf = restart_font.render("Restart", True, (255, 255, 255))
            restart_rect = restart_surf.get_rect(center=restart_btn.center)
            screen.blit(restart_surf, restart_rect)

        # 手番の表示
        if turn:
            turn_surf = turn_font.render("TURN : WHITE", True, (255, 255, 255))
        else:
            turn_surf = turn_font.render("TURN : BLACK", True, (0, 0, 0))

        ui_zone_width = screen_width - board_size
        turn_rect = turn_surf.get_rect(center=(board_size + ui_zone_width // 2, 30))
        screen.blit(turn_surf, turn_rect)

        return screen
    
    
    def draw_check(self, screen, screen_width, board_size):
        """
        チェック表示の設定
        引数：
            screen, チェスのスクリーンウィンドウ
            screen_width, スクリーンウィンドウの横幅
            board_size, ウィンドウの内のチェス盤のサイズ
        戻り値：
            screen, 更新したチェスのウィンドウ
        """
        # フォントの初期設定
        check_font = pygame.font.Font(None, 30)

        # 表示位置計算
        check_surf = check_font.render("CHECK", True, (255, 0, 0))
        ui_zone_width = screen_width - board_size
        check_rect  = check_surf.get_rect(center=(board_size + ui_zone_width // 2, 60))
        screen.blit(check_surf, check_rect)

        return screen
    

    def draw_checkmate(self, screen, screen_width, board_size, turn):
        """
        ウィンドウに勝敗の表示をする
        引数：
            screen, チェスのスクリーンウィンドウ
            screen_width, スクリーンウィンドウの横幅
            board_size, ウィンドウの内のチェス盤のサイズ
            turn, 現在の手番
        戻り値：
            screen, 更新したチェスのウィンドウ
        """
        # フォントの初期設定
        checkmate_font = pygame.font.Font(None, 30)

        # 勝敗内容（手番が切り替わってから勝敗判定を行うため、黒手番でチェックメイト判定されたら、白が勝ち）
        if turn:
            checkmate_surf = checkmate_font.render("BLACK WIN", True, (0, 0, 0))
        else:
            checkmate_surf = checkmate_font.render("WHITE WIN", True, (255, 255, 255))

        # 表示位置計算
        ui_zone_width = screen_width - board_size
        checkmate_rect  = checkmate_surf.get_rect(center=(board_size + ui_zone_width // 2, 150))
        screen.blit(checkmate_surf, checkmate_rect)

        return screen
    

    def draw_stalemate(self, screen, screen_width, board_size):
        """
        ウィンドウに引き分けの表示をする
        引数：
            screen, チェスのスクリーンウィンドウ
            screen_width, スクリーンウィンドウの横幅
            board_size, ウィンドウの内のチェス盤のサイズ
        戻り値：
            screen, 更新したチェスのウィンドウ
        """
        # フォントの初期設定
        stalemate_font = pygame.font.Font(None, 50)

        # 表示内容
        stalemate_surf = stalemate_font.render("DRAW", True, (255, 0, 0))
        # 表示位置計算
        ui_zone_width = screen_width - board_size
        stalemate_rect  = stalemate_surf.get_rect(center=(board_size + ui_zone_width // 2, 100))
        screen.blit(stalemate_surf, stalemate_rect)

        return screen
    

    def draw_chess_menu(self, screen, fonts, buttons, screen_width, fps):
        """
        メニュー画面のUIを表示する
        引数：
            screen, メニュー画面のスクリーンウィンドウ
            fonts, メニュー画面に表示するフォントのリスト
            buttons, メニュー画面に表示するボタンのリスト
            screen_width, スクリーンウィンドウの横幅
            fps, フレームレート
        戻り値：
            screen, 更新したメニュー画面のウィンドウ
        """
        # フォント定義受け取り
        title_font  = fonts[0]
        button_font = fonts[1]
        # ボタン定義受け取り
        solo_btn   = buttons[0]
        host_btn   = buttons[1]
        client_btn = buttons[2]

        # 背景色
        screen.fill((50, 50, 70))  
        # タイトル描画
        title_text = title_font.render("Let's Chess!", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen_width // 2, 200))
        screen.blit(title_text, title_rect)
        # SOLOPLAYボタン描画
        pygame.draw.rect(screen, (70, 130, 180), solo_btn)
        pygame.draw.rect(screen, (255, 255, 255), solo_btn, 2)
        solo_text = button_font.render("SOLOPLAY", True, (255, 255, 255))
        solo_text_rect = solo_text.get_rect(center=solo_btn.center)
        screen.blit(solo_text, solo_text_rect)
        # MULTI（HOST）ボタン描画
        pygame.draw.rect(screen, (130, 180, 70), host_btn)
        pygame.draw.rect(screen, (255, 255, 255), host_btn, 2)
        host_text = button_font.render("MULTI (HOST)", True, (255, 255, 255))
        host_text_rect = host_text.get_rect(center=host_btn.center)
        screen.blit(host_text, host_text_rect)
        # MULTI（CLIENT）ボタン描画
        pygame.draw.rect(screen, (180, 130, 70), client_btn)
        pygame.draw.rect(screen, (255, 255, 255), client_btn, 2)
        client_text = button_font.render("MULTI (CLIENT)", True, (255, 255, 255))
        client_text_rect = client_text.get_rect(center=client_btn.center)
        screen.blit(client_text, client_text_rect)

        # 描画更新
        pygame.display.update()
        self.clock.tick(fps)

        return screen