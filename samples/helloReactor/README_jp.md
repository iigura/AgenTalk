# これは何？
Reactor 側に HELLO という文字列を表示する、
最も単純な AgenTalk のサンプルプログラムです。

# 実行方法
## 前提条件
AgenTalk 直下の README.md を参考にして、
AgenTalk が editable install してあるものとします。
redis ならびに Ray のサーバーも起動しておいて下さい。

## リアクタの起動
agt start として Reactor を起動します。

```bash
agt start
```

## greet Phase の登録
Reactor を起動したターミナルとは別のターミナルを開き、
helloReactor ディレクトリ直下にて agt reg . を実行します
（**reg の後のピリオドを忘れないようにして下さい**）。

```bash
agt reg .
```

正常に登録ができれば、Reactor を実行しているターミナルに、
Phase 'helloReactor.greet' is loaded.
という文字列が出力されます。

## helloReactor.greet Phase の実行
agt run helloReactor.greet を実行します。

```bash
agt run helloReactor.greet
```

しかしこの時点では、Reactor には HELLO という文字列は
まだ表示されていないと思います。

AgenTalk の Phase は原則的にチケット制を導入しています。
実行のためのチケットの獲得ができなければ
Phase は実行されません。

helloReactor.greet を実行するためのチケットを
agt at を実行して発行します。

```bash
agt at
```

チケットを発行すると、Reactor 側のターミナルに
HELLO という文字列が表示されます。

なお、チケットは agt cl を実行してクリアするまで
残っています。

```bash
agt cl
```

残存するチケット数は agt ct の実行にて確認できます。

```bash
agt ct
```

