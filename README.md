# Liaro-homework

設計書の書き方もよくわかってないので、添削してもらえると嬉しいです…！
*ディレクトリ構成
*要求仕様
*設計

*ディレクトリ構成

chat
|
|- __pycache__
|- alembic.ini  #migrateするときのconfigファイル
|- migrations
|    |
|    |- README
|    |- __pycache__
|    |    |-env.cpython-36.pyc
|    |- env.py  #migrateを実行するモジュール
|    |- script.py.maco
|    |- versions
|        |-__pycache__
|        |- 0f5fa580f321_add_content_table.py   #実際にテーブルを作る機能を持つファイル（automigrateで自動生成)
|
|- models.py    #RDSのテーブルをクラス管理するモジュール
|- settings.py  #DBとのセッションを作成するモジュール
|- server.py	 #webサーバとなるファイル
|- static
|    |-style.css
|
|- templates
    |- chat.html         #チャット画面
    |- login.html         #ログイン画面
    |- select_partner.html #チャット相手選択画面
    |- create_user.html   #ユーザ作成画面

*要求仕様

①WebフレームワークはTornado
②インフラはAWSEC2(Amazon Linux),RDS(MySQL)
③DBのORMはsqlalchemy,マイグレーションはalembic
④コーディング規約はpep8
⑤LINEなどによく見られる、二者間のみが閲覧できるチャットアプリ、内容はサーバ側に保存

*設計

BaseHandlerに①nameを引数にidを出力②idを引数にUserクエリを出力③2つのidを引数に二者間のContentクエリを出力④Cookieにnameを保存する　を用意
各メソッド内で都度sessionを作成し、closeする。DBにクエリ(データ）を追加したりする時は別に処理を各Handlerに追加。←このDBの追加処理は一般化できないか考えます。

①ログイン画面でユーザ名を打ち込みログイン。毎回ログインする必要がないようにログイン情報はcookieに保存。
  Userテーブル(id,name)をnameをキーに探索して、該当すればログイン完了、なければユーザ作成ページにリダイレクト。
②ユーザ作成ページでは、名前をboxに入力。Userテーブルに新しいデータを追加する。登録できたらログインページにリダイレクト。
③ログインの後、チャット相手をボタン選択。そのユーザとのchatページにリダイレクト。
④idをキーにContentテーブルからチャット履歴を参照し表示。随時チャット内容はContentテーブルに保存。リロードで更新が反映される。
④テーブルはmodelモジュール(自作)でclass管理し、サーバにimportして使用。テーブルの仕様変更(migration)もmodelで行う。

server.pyがメインとなるファイルで、一番ごちゃごちゃしてるところなので、これだけでも見ていただけると嬉しいです…
