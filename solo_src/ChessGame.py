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
            click_pos = self.wait_events()
            self.change_state(click_pos)
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
            mobiles = self.move_calculator.calc_pawn_moves(self.board_manager.curr_board, cellY, cellX, self.logger.enpassant_log, self.turn_manager.turn)
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

        # ターン切換して選択情報リセット
        # キャスリングフラグもFalseにする
        self.turn_manager.switch_turn()
        self.reset_state()
        self.move_calculator.castling_flag = False

        # ターンが切り替わってからすぐにチェックメイトの確認
        if self.check_game_end.is_checkmate(self.board_manager.curr_board, self.turn_manager.turn, self.logger.enpassant_log, self.logger.moved_pieces_log):
            self.game_state = "END_GAME"
            self.in_checkmate = True
        # チェックメイトでない場合はステルスメイトの確認も行う
        else:
            if self.check_game_end.is_stalemate(self.board_manager.curr_board, self.turn_manager.turn, self.logger.enpassant_log, self.logger.moved_pieces_log):
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
        self.screen = self.renderer.draw_ui(self.screen, self.SCREEN_WIDTH, self.BOARD_SIZE, self.restart_btn, self.turn_manager.turn)
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

    