## 動かし方

```
git clone git@github.com:TM82/Liaro-homework.git
cd chat
python server.py
```

## 条件

①WebフレームワークはTornado

②インフラはAWSEC2(Amazon Linux),RDS(MySQL)

③DBのORMはsqlalchemy,マイグレーションはalembic

④コーディング規約はpep8

⑤LINEなどによく見られる、二者間のみが閲覧できるチャットアプリ、内容はサーバ側に保存

## 仕様

### ログイン画面

- Send

```
GET /login
```
- Received ログインページ(HTML)

### ログイン

- Send

```
POST /login
```
```
{
    "name":"{ユーザ名}"
}
```
- Received
  DBのUserテーブルを参照して、

  nameが存在すればCookieにnameを保存し、/select にリダイレクト

  nameが存在しなければ/create_user/{ユーザ名} にリダイレクト

### ログアウト

- Send

```
GET /logout
```

- Received Cookieを削除

### ユーザ作成画面

- Send

```
GET /create_user/{ユーザ名}
```
  {ユーザ名}は、ログインページで存在しないユーザでログインしようとした時にその値を保存して、ユー>ザ作成画面に表示させるために用意。

- Received ユーザ作成画面(HTML)

### ユーザ作成

- Send

```
POST /create_user/
```
```
{
    "username":"{ユーザ名}"
}
```
- Received

Userテーブルにhtmlから受け取ったユーザを追加して、/login にリダイレクト。
```
{
    "id":"{usersのid}",
    "username":"{ユーザ名}"
}
```
### チャット相手選択画面

- Send
```
GET /select
```
- Received チャット相手選択画面(HTML)

### チャット相手選択

- Send
```
POST /select
```
```
{
    "partner_id": "チャット相手のid"
}
```
- Received　partner_idを返して/chat/{parner_id}にリダイレクト。

### チャット画面

- Send

```
GET /chat/{チャット相手のid}
```
- Received チャット画面(HTML)

### チャット

- Send

```
POST /chat/{チャット相手のid}
```
```
{
    "id": "{contentsのid}",
    "from_id": "{発信元のユーザid}",
    "to_id": "{発信先のユーザid}",
    "content": "{会話のtxtデータ}",
    "datetime": "{作成日時}"
}
```

- Received

  Contentテーブルにクエリを追加して、/chat/{チャット相手のid} にリダイレクト。


## 仕様の理由

1. ログイン画面で存在しないユーザ名を入力した時に、その値をboxに保存したままユーザ作成画面に移り>たい
2. まずは単純に チャット相手選択→チャット画面でチャット を行うために必要な機能だけをつけたい
