# これは何？
複数のノードが参加している場合において、
本当にそれらが分散処理を実施しているのかを確認する
サンプルプログラムです。

この stamp.py で定義されている stampAllNodes.main という
フェイズを実行すると、参加しているノードの
/tmp に `AgenTalk_stamp_YYYYmmdd_HHMMSS.txt` という
空のファイルを作成します。

`YYYYmmdd_HHMMSS` の部分には実行した時の
年月日と時分秒が入ります。

# 実行方法
他のサンプルプログラムと同様に本ディレクトリ
samples/stampAllNodes にて、`agt reg .` を実行します。

その後、

```bash
agt run stampAllNodes.main
```

とすれば全てのノードの `/tmp` にファイルが作られます。

実行にはチケットが 1 枚必要ですので、

```bash
agt at
```

を実行し、チケットを追加しておいて下さい。

