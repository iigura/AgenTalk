# これは何？
AgenTalk では複数の Phase を登録できます。
このサンプルプログラムでは、Ready, Set, Go という
Phase を登録し、Ready が Set を呼び出し、
Set が Go を呼び出します。

なお実際の Phase 名は、それぞれ
helloPhases.Ready,
helloPhases.Set,
helloPhases.Go です。

また、Phase の実行関数 act は引数を取ることができ、
その引数の値は agt run PhaseName の後に記すことができます。

```bash
agt run helloPhases.Ready 3
```

は、helloPhases.Ready という Phase に対し 3 という引数を与えて、
つまり helloPhases.Ready の act 関数を act(3) として呼び出す、という意味となります。

# 実行方法
helloReactor を参考に Reactor を起動し（agt start）、
agt reg . として、Ready, Set, Go の各 Phase を登録しておきます。

次に agt run helloPhases.Ready として Ready を起動すると、
Ready が Set を呼び出し、Set が Go を呼び出します。

各 Phase においては helloReactor と同様に
Reactor 側のターミナルに Ready などの文字列を表示します。

act 関数への引数の例としては、
agt run helloPhases.Ready 3 と実行すれば、
Ready, Set, Go という一連の処理が 3 回実行されます。

