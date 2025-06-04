import pygame
from pygame.locals import *
# クラス
from BoardManager   import BoardManager
from Renderer       import Renderer
from MoveCalculator import MoveCalculator
from MoveExecutor   import MoveExecutor
from TurnManager    import TurnManager
from Logger         import Logger
from CheckGameEnd   import CheckGameEnd
from Highlighter    import Highlighter
from PromotionUI    import PromotionUI
from MultiModule    import MultiModule
#====================================================================

# ゲーム全体の起動、メインループ制御

#====================================================================
class ChessGame:
    # ==================================
    # 定数
    # ==================================
    SCREEN_HEIGHT = 650 # スクリーンの高さ
    SCREEN_WIDTH  = 800 # スクリーンの横幅
    BOARD_SIZE    = 650 # 盤の高さ、横幅
    PIECE_SIZE    = BOARD_SIZE // 8 # 駒のサイズ
    FPS           = 30 # フレームレート
    # メニュー画面のボタンサイズ
    BUTTON_WIDTH = 300
    BUTTON_HEIGHT = 50
    BUTTON_MARGIN = 60

    # ==================================
    # コンストラクタ
    # ==================================
    def __init__(self):
        """
        引数：
            なし
        """
        # pygame初期化
        pygame.init()
        pygame.font.init()
        # ウィンドウ生成
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        # フレームレート管理用のClockオブジェクト
        self.clock  = pygame.time.Clock()
        # マルチプレイ時の自分のターン認識用（文字列のwhiteかblack）
        self.my_color = None
        # マルチプレイかどうかのフラグ（ソロプレイはFalse）
        self.multi_flag = False

        # インスタンス生成
        self.board_manager   = BoardManager()
        self.turn_manager    = TurnManager()
        self.renderer        = Renderer(self.screen, self.BOARD_SIZE, self.PIECE_SIZE)
        self.highlighter     = Highlighter(self.screen, self.PIECE_SIZE)
        self.logger          = Logger()
        self.promotion_ui    = PromotionUI(self.screen, self.BOARD_SIZE)
        self.move_calculator = MoveCalculator()
        self.move_executor   = MoveExecutor(self.promotion_ui)
        self.check_game_end  = CheckGameEnd()
        self.multi_module    = MultiModule()

        # ゲーム制御のフラグ
        self.process_flag = True
        # 選択中の駒情報 (cellY, cellX, piece)かNone
        self.selected_piece = None
        # ハイライトする移動可能セル
        self.highlight_cells = []
        # チェックされているかどうかのフラグ
        self.in_check = False
        # チェックメイトのフラグ
        self.in_checkmate = False
        # ステルスメイトのフラグ
        self.in_stalemate = False

        # ゲームの状況 "SELECT_PIECE"か"SELECT_DSTINATION"か"END_GAME"
        self.game_state = "SELECT_PIECE"
        # リスタートボタンの定義
        self.restart_btn = pygame.Rect(self.BOARD_SIZE+25, 580, 100, 50)

    # ==================================
    # メソッド
    # ==================================
    def chess_menu(self):
        """
        チェスのメニューを表示する]
        引数：
            なし
        戻り値：
            なし
        """
        # ボタンの位置計算（画面中央に配置）
        center_x = self.SCREEN_WIDTH // 2 - self.BUTTON_WIDTH // 2
        start_y  = 350
        # フォント設定
        title_font  = pygame.font.Font(None, 72)
        button_font = pygame.font.Font(None, 36)
        fonts       = [title_font, button_font]
        # メニューのボタン定義
        solo_btn   = pygame.Rect(center_x, start_y+self.BUTTON_MARGIN*0                         , self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        host_btn   = pygame.Rect(center_x, start_y+self.BUTTON_MARGIN*1, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        client_btn = pygame.Rect(center_x, start_y+self.BUTTON_MARGIN*2, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        buttons    = [solo_btn, host_btn, client_btn]

        # イベントループ
        menu_run = True
        while menu_run:
            for event in pygame.event.get():
                # 終了
                if event.type == QUIT:
                    self.process_flag = False
                    return "QUIT"

                if event.type == MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos

                    # SOLOPLAYボタンクリック
                    if solo_btn.collidepoint(mouse_x, mouse_y):
                        return self.chess_run()

                    # MULTI（HOST）ボタンクリック
                    elif host_btn.collidepoint(mouse_x, mouse_y):
                        self.my_color = self.multi_module.multimodule_main("host")
                        # Noneが返ってきていたらcontinue
                        if self.my_color == None:
                            print("接続が失敗しました")
                            continue
                        # マルチプレイのフラグをTrueにして自分の色を手前に描画する
                        self.multi_flag = True
                        self.board_manager.reset_multi_board(self.my_color)
                        return self.chess_run()

                    # MULTI（CLIENT）ボタンクリック
                    elif client_btn.collidepoint(mouse_x, mouse_y):
                        self.my_color = self.multi_module.multimodule_main("client")
                        # Noneが返ってきていたらcontinue
                        if self.my_color == None:
                            continue
                        # マルチプレイのフラグをTrueにして自分の色を手前に描画する
                        self.multi_flag = True
                        self.board_manager.reset_multi_board(self.my_color)
                        return self.chess_run()
                    
            # 画面更新
            self.screen = self.renderer.draw_chess_menu(self.screen, fonts, buttons, self.SCREEN_WIDTH, self.FPS)


    def chess_run(self):
        """
        メインループ制御
        引数；
            なし
        戻り値：
            なし
        """
        while self.process_flag:
            # クリックイベントを待つ
            # マルチプレイ時は、ターンと自分の色が一致しているときのみ駒の選択を許す
            if not self.multi_flag:
                click_pos = self.wait_events()
                self.change_state(click_pos)
            else:
                # マルチプレイの時、どっちのターンか把握する。
                turn_color = "white" if self.turn_manager.turn else "black"
                is_my_turn = self.my_color == turn_color
                # 自分の色とターンが対応するとき（"white"とTrue, "black"と"False"）は駒を操作できる
                if is_my_turn:
                    click_pos = self.wait_events()
                    self.change_state(click_pos)
                else:
                    # 自分の色とターンが対応しないときは相手の操作をまつ
                    recv_board, recv_log = self.multi_module.wait_moveinfo()
                    # 受け取ったら操作を反映してターン切換
                    if recv_board != None or recv_log != None:
                        self.logger.enpassant_log = recv_log
                        self.board_manager.curr_board = recv_board
                        self.turn_manager.switch_turn()
                        #チェックメイトとステルスメイトの確認
                        self.game_end_check()
                    # 終了イベント受け付ける
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            self.process_flag = False

                    
            # 描画更新
            self.render() 
            self.clock.tick(self.FPS)
        
        # pygame終了
        pygame.quit()
        return
    

    def wait_events(self):
        """
        クリックイベントを待ち、クリックされたセルの座標と中身を返す
        引数；
            なし
        戻り値：
            なし
        """
        for event in pygame.event.get():
            # ウィンドウが閉じられたとき
            if event.type == QUIT:
                self.process_flag = False
                
            # スクリーンがクリックされたとき
            if event.type == MOUSEBUTTONDOWN:
                # クリックされた座標を取得
                clickX, clickY = event.pos

                # リスタートボタンがクリックされたとき
                if self.restart_btn.collidepoint(clickX, clickY):
                    self.reset_state()
                    self.board_manager.reset_board()
                    self.logger.reset_log()
                    self.turn_manager.reset_turn()
                    self.in_check = False
                    self.in_checkmate = False
                    self.in_stalemate = False

                # 盤外がクリックされたら再度イベントを待つ
                if (clickY > self.BOARD_SIZE) or (clickX > self.BOARD_SIZE):
                    continue
                # クリックされた座標から盤のセルを特定
                cellY = int(clickY // self.PIECE_SIZE)
                cellX = int(clickX // self.PIECE_SIZE)

                return (cellY, cellX)
            
        return None


    def change_state(self, click_pos):
        """
        ゲームの状態に応じて駒選択処理と移動先選択処理を分岐
        引数：
            click_pos, クリックされたセルの座標
        戻り値：
            なし
        """
        # 引数が空なら終わり
        if click_pos == None:
            return
        
        # クリックされたセルの座標を取得
        cellY, cellX = click_pos
        
        # 状態が"GAME_END"なら処理を行わない
        # 状態が"SELECT_PIECE"なら駒選択処理
        # 状態が"SELECT_DESTINATION"なら移動先選択処理
        if self.game_state == "END_GAME":
            return
        elif self.game_state == "SELECT_PIECE":
            self.select_piece(cellY, cellX)
        elif self.game_state == "SELECT_DESTINATION":
            self.select_destination(cellY, cellX) 

    
    def select_piece(self, cellY, cellX):
        """
        駒の選択を待つ処理
        引数：
            cellY, クリックされたセルのY座標
            cellX, クリックされたセルのX座標
        戻り値：
            なし
        """
        # セルの中身を取得
        cell = self.board_manager.get_piece(cellY, cellX, self.board_manager.curr_board)
        # セルが空の場合何もしない
        if cell == 0:
            return
        # 手番違反でも何もしない
        if not self.turn_manager.check_valid_turn(cell):
            return
        # 駒が選択されたら、そのセルの座標と駒の種類を保存
        self.selected_piece = ((cellY, cellX), cell)
        
        # 移動可能セルの計算（ポーンとポーン以外）
        if cell[1] == "P":
            mobiles = self.move_calculator.calc_pawn_moves(self.board_manager.curr_board, cellY, cellX, self.logger.enpassant_log, self.turn_manager.turn, self.my_color)
        else:
            mobiles = self.move_calculator.calc_common_moves(self.board_manager.curr_board, cellY, cellX, cell, self.turn_manager.turn, self.logger.moved_pieces_log)

        # 移動可能先が無ければそのままリターン
        if len(mobiles) == 0:
            return
        
        # 動かせるすべてのセルから「チェックにならない」「チェックを解除できる手」だけを抽出する
        # 選択された駒の位置と種類を取得
        fromY, fromX = self.selected_piece[0]
        piece        = self.selected_piece[1]
        # チェックを外すことのできる手リスト
        safe_mobiles = []
        # 実際に盤面を動かして、シュミレーションする
        for destY, destX in mobiles:
            tmp_board = [row[:] for row in self.board_manager.curr_board]
            tmp_board[fromY][fromX] = 0
            tmp_board[destY][destX] = piece
            # この一手でチェック状態にならないあるいはチェックを解除できるなら登録
            if not self.check_game_end.is_check(tmp_board, self.turn_manager.turn):
                safe_mobiles.append((destY, destX))

        # 手が無ければ何もしない
        if len(safe_mobiles) == 0:
            return
        
        # mobilesを上書き
        mobiles = safe_mobiles
        # 移動可能セルのハイライト
        self.highlight_cells = mobiles
        self.game_state = "SELECT_DESTINATION"
        return


    def select_destination(self, destY, destX):
        """
        移動先の選択を待ち、移動実行を行う
        引数：
            destY, クリックされた移動先セルのY座標
            destX, クリックされた移動先セルのX座標
        戻り値：
            なし
        """
        # 選択されたセルが移動可能セルのリストにない場合は駒選択に戻る
        if (destY, destX) not in self.highlight_cells:
            self.reset_state()
            return
        
        # 選択した駒情報からスタート地点と駒の種類を得る
        (fromY, fromX), piece = self.selected_piece
        # 移動実行（ポーンとポーン以外で移動処理が違う）
        if piece[1] == "P":
            self.move_executor.move_pawn(self.board_manager.curr_board, (fromY,fromX), (destY,destX), piece, self.turn_manager.turn)
            self.logger.save_enpassant_log((fromY,fromX), (destY,destX)) # ポーンの移動はログを取る
        else:
            self.move_executor.move_common(self.board_manager.curr_board, (fromY,fromX), (destY,destX), piece, self.move_calculator.calc_castling)

        # 移動ログの記録
        self.logger.save_log(piece, (fromY,fromX), (destY,destX))

        # マルチプレイ時の情報交換（駒の移動情報）
        if self.multi_flag:
            # ボードの情報を丸ごと送る
            self.multi_module.send_moveinfo(self.board_manager.curr_board, self.logger.enpassant_log)

        # ターン切換して選択情報リセット
        # キャスリングフラグもFalseにする
        self.turn_manager.switch_turn()
        self.reset_state()
        self.move_calculator.castling_flag = False

        #チェックメイトとステルスメイトの確認
        self.game_end_check()

        return
        
    
    def game_end_check(self):
        """
        チェックメイトとステルスメイトの確認を行う
        引数：
            なし
        戻り値：
            なし
        """
        # ターンが切り替わってからすぐにチェックメイトの確認
        if self.check_game_end.is_checkmate(self.board_manager.curr_board, self.turn_manager.turn, self.logger.enpassant_log, self.my_color, self.logger.moved_pieces_log):
            self.game_state = "END_GAME"
            self.in_checkmate = True
        # チェックメイトでない場合はステルスメイトの確認も行う
        else:
            if self.check_game_end.is_stalemate(self.board_manager.curr_board, self.turn_manager.turn, self.logger.enpassant_log, self.my_color, self.logger.moved_pieces_log):
                self.game_state = "END_GAME"
                self.in_stalemate = True

        return


    def reset_state(self):
        """
        移動先選択状態から駒選択状態に戻るときに保持している情報をリセットする
        引数；
            なし
        戻り値：
            なし
        """
        self.selected_piece = None
        self.highlight_cells = []
        self.game_state = "SELECT_PIECE"

        return
        

    def render(self):
        """
        上で準備したものを反映する（画面クリア → 要素描画 → 更新）
        引数；
            なし
        戻り値：
            なし
        """
        # 画面クリア
        self.screen.fill((170, 170, 170))
        # 盤面描画
        self.screen = self.renderer.draw_board(self.screen)
        # 駒描画
        self.screen = self.renderer.draw_pieces(self.screen, self.board_manager.curr_board)
        # ハイライト描画
        self.highlighter.highlight_mobiles(self.highlight_cells)
        # UI 描画（ターン表示など）
        self.screen = self.renderer.draw_ui(self.screen, self.SCREEN_WIDTH, self.BOARD_SIZE, self.restart_btn, self.turn_manager.turn, self.multi_flag)
        # チェック状態ならCHECKの文字を表示
        if self.check_game_end.is_check(self.board_manager.curr_board, self.turn_manager.turn):
            self.renderer.draw_check(self.screen, self.SCREEN_WIDTH, self.BOARD_SIZE)
            self.in_check = True
        if self.in_checkmate:
            self.renderer.draw_checkmate(self.screen, self.SCREEN_WIDTH, self.BOARD_SIZE, self.turn_manager.turn)
        if self.in_stalemate:
            self.renderer.draw_stalemate(self.screen, self.SCREEN_WIDTH, self.BOARD_SIZE)

        # 画面更新
        pygame.display.update()
        return