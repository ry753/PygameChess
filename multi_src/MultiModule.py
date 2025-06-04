import socket
import random
import json
import pygame
from pygame.locals import *
import sys
#====================================================================

# マルチプレイに関する処理を行う

#====================================================================
class MultiModule:
    # ==================================
    # コンストラクタ、デストラクタ
    # ==================================
    def __init__(self):
        # サーバーとクライアントのソケット（IPv4、TCP）
        self.server_socket = None
        self.client_socket = None
        # サーバーを建てる際のIPアドレスとポート
        self.host = 'localhost'
        self.port = 8899
        # 取得したクライアントのIP,ポート
        self.client_address = None 
        
    def __del__(self):
        if self.client_socket != None:
            self.client_socket.close()
        if self.server_socket != None:
            self.server_socket.close()

    # ==================================
    # メソッド
    # ==================================
    def multimodule_main(self, mode):
        """
        渡された引数によって、ホストかクライアントに分かれる
        引数：
            mode, 'host'か'client'が渡される、hostならクライアントからの通信を待つclientならホストへの接続を試みる
        戻り値：
            my_color, マルチプレイ時の自分が操作する駒の色の文字列
        """
        if mode == "host":
            my_color = self.start_host()
        else:
            my_color = self.start_client()

        # チェスのゲーム開始
        return my_color


    def start_host(self):
        """
        サーバーとしてクライアントからの接続を待ち受ける
        引数：
            なし
        戻り値：
            my_color, マルチプレイ時の自分が操作する駒の色の文字列
        """       
        # ソケットを作成（IPv4、TCP）
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # サーバーのアドレスとポートをバインド
        self.server_socket.bind((self.host, self.port))
        # 接続待ちを開始（最大1つの接続まで）
        self.server_socket.listen(1)
        print(f"サーバーが {self.host}:{self.port} で待機中です")

        # 何回タイムアウトしたかのカウント
        timeout_cnt = 0
        while True:
            # タイムアウト付きでaccept
            self.server_socket.settimeout(0.1)  # 短めのタイムアウトを設定する
            try:
                self.client_socket, self.client_address = self.server_socket.accept()
                print(f"クライアント {self.client_address} が接続しました")
                break

            except socket.timeout:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                if timeout_cnt > 100:
                    return None
                else:
                    timeout_cnt += 1
                    continue
        
        # 自分の手番を決めて、自分と反対の手番を送信
        # 白なら送信権はこっちスタート、黒なら送信権は相手から
        coin_toss = random.randint(0, 1)
        if coin_toss == 1:
            my_turn    = "white"
            other_turn = "black"
        else:
            my_turn    = "black"
            other_turn = "white"
        self.client_socket.send(other_turn.encode('utf-8'))
        return my_turn
    

    def start_client(self):
        """
        サーバーに対して接続要求を行う
        引数：
            なし
        戻り値：
            my_color, マルチプレイ時の自分が操作する駒の色の文字列
        """
        # ソケットを作成
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # サーバーのIPを入力
        # host = input (f"接続先IPを入力:")
        host = "localhost"
        port = 8899

        # サーバーに接続要求
        try:
            print(f"サーバー {host}:{port} に接続を行っています")
            self.client_socket.settimeout(10) # 10秒でタイムアウト
            self.client_socket.connect((host, port))

            # サーバーからの手番情報をもらう
            my_turn = self.client_socket.recv(1024).decode('utf-8')
            print(f"サーバー {host}:{port} に接続しました")
            return my_turn
            
        except TimeoutError:
            print("タイムアウトしました。サーバーからの応答がありません")
            return None
        except ConnectionRefusedError:
            print("サーバーへの接続が拒否されました。サーバーが起動しているか確認してください。")
            return None

    
    def send_moveinfo(self, curr_board, enpassant_log):
        """
        駒の移動情報（移動元、移動先）を相手に送信する
        引数：
            curr_board, 現在の盤面
            enpassant_log, アンパッサン判定用ログ
        戻り値：
            なし
        """
        # 送信
        json_str = json.dumps({"board": curr_board, "log": enpassant_log})
        self.client_socket.send(json_str.encode('utf-8'))
        return


    def wait_moveinfo(self):
        """
        駒の移動情報（移動元、移動先）が送られてくるのをまつ
        引数：
            なし
        戻り値：
            flipped, 上下反転させた移動後の相手の盤状況
            log, 相手の移動ログ
        """
        # 通信相手のが存在しないときはNoneを返す
        if self.client_socket == None:
            return None
        
        try:
            # 受信待ち処理にタイムアウト（短め）を設定する
            self.client_socket.settimeout(0.01)
            json_str = self.client_socket.recv(1024).decode('utf-8')
            if json_str == None:
                return None
            
            # 受け取ったJSON文字列をdictに戻す
            data_dict = json.loads(json_str)
            
            # 盤面状況とログを抜き出す
            board = data_dict.get("board", None)
            log   = data_dict.get("log", None)

            # ボードは上下反転させて返す
            flipped = [row[::-1] for row in board[::-1]]

            return flipped, log
            
        except socket.timeout:
            return None, None


    def close_connection(self):
        """
        ソケットを閉じる
        引数：
            なし
        戻り値：
            なし
        """
        if self.client_socket != None:
            self.client_socket.close()
        if self.server_socket != None:
            self.server_socket.close()
        return