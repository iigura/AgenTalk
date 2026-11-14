# これは何？
AgenTalk でも map reduce 的な処理
（scatter gather 的な処理）が実現
できることを示すサンプルプログラムです。

worker Phase にて分散して処理を行い、
gather Phase にてそれらの処理の合流を行います。

# 実行方法
helloReactor を参考に Reactor を起動し（agt start）、
`agt reg .` として、entry, worker, gather の各 Phase を登録しておきます。

次に

```bash
 agt run mapReduce.entry
```

として entry Phase を起動します。

# worker Phase での処理
本サンプルプログラムでは各 worker には
それぞれ 1 から 10 までの値が渡され
各 worker では、それらの値をそのまま
処理後の値として gather Phase で渡します。

実際の値のやりとりは AgenTalk の各ノードからアクセス可能な
Redis server （AgenTalk では、この Redis server を **Global Redis** と呼んでいます）
を介して行われます。

# gather Phase での処理
gather Phase では、各 worker Phase より方向された値を
順次取得し、全ての値を足し合わせます。
全ての worker Phase から、値の報告が終わったら、
合計値を Reactor 側に出力して終了します。

