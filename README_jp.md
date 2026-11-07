# AgenTalk
開発しやすく、スケールしやすい。
ローカル LLM 向け AI エージェントフレームワークです。

提供される関数群により処理フローを素早く組み立て、
実行時には Ray による並列・分散処理でスケールアウトできます。
処理の割り振りを行う「リアクタ」とは Redis で連携し、
途中に決定的な検証処理を挟むことで、
AI エージェントをシステムの制御下に置いたまま堅牢な処理を構築できます。

AI に丸投げしない。
検証と制御を組み込んだ AI エージェントを、
安心して運用できる形で開発・構築できます。

注: 現在は公開初期段階のため、API や内部構成は変更される可能性があります。

## ライセンス
MIT ライセンスです。
詳細は `LICENSE` を参照してください。

## インストール（editable install）
開発版としてインストールします。
本リポジトリの直下にて、
以下のコマンドを実行してインストールして下さい。

```bash
pip install -r requirements.txt
pip install -e .
```

requirements.txt により、以下のパッケージがインストールされます。

- redis, ray, pyyaml, asttokens, ollama, dateparser, pdfminer.six, chardet

無事にインストールできたかどうかは、
Python インタプリタ上で import AgenTalk を実行し、
エラーが出なければインストール成功です。

## 使用方法
詳細は samples/fitText にある README をご覧ください。
その他、samples ディレクトリにある helloReactor や helloPhases などにも
簡単な説明がありますので参考にして下さい。

## 実行環境の準備（分散実行の準備）
全てのノード上で AgenTalk をインストールして下さい。
Ray を使うので、Python のバージョンは全てのノードで
揃えておいた方が良いと思います。

### Redis
AgenTalk では Redis を利用します。
Ubuntu 等であれば

```
sudo apt install redis
```

として Redis server が起動できるようにして下さい。

Ubuntu では、インストール時に Redis のサービスが自動起動し、
デフォルトの 6379 番ポートを使用する場合があります。
このポートは Ray のデフォルトポートと競合するため、
他のアプリケーションがこの Redis サービスを使用していない場合は、
自動起動を無効化して停止して下さい。

```
sudo systemctl disable --now redis-server
```

Redis が 6379 番ポートを使用していても、
上記のコマンドを実行すれば、
そのポートの使用は停止するはずです
（なので再起動は不要です）。

次に redis-server を起動します。

```
redis-server --port 6789 &
```

正しく起動できているか否かは、次のコマンドで確認して下さい
（PONG と返ってくれば無事起動しています）。

```
redis-cli -p 6789 ping
```

### ray
#### ヘッドノードの起動
ヘッドノード用の環境にて、Ray のヘッドノードの起動を行います。

```
ray start --head
```

正しく起動すれば、シェルの入力モードに戻って来ますので、
そこで、

```
ray status
```

として、Ray ノードの稼働状況を確認して下さい。

#### リモートノードの参加
現在のセッションを Ray のヘッドノードに参加させるには、
次のコマンドを実行して下さい。

```
ray start --address='ヘッドノードの IP アドレス:6379'
```

特に開発時等、同じ計算機上の異なるセッションを
リモートノードとして参加させる場合は、

```
ray start --address='127.0.0.1:6379'
```

を実行して下さい。
リモートノードの参加状況も、

```
ray status
```

にて確認できます。
active のところに node_... という感じで、
node が 2 行表示されれば、ray start にて、リモートノードが
追加されていることとなる（ヘッドノードだけ起動している時は
active のところに表示される node は 1 つだけとなります）。

### 複数のコンピュータを使う場合（Tailscale を利用する場合）
複数のコンピュータを利用して AgenTalk を実行する場合は、
Ray および Redis に他のコンピュータから接続できるように設定する必要があります。

ここでは Tailscale を使った構成例を示します。
すべてのコンピュータに Tailscale がインストールされ、同じ tailnet に参加しているものとします。

#### Tailscale のアクセス制御
Tailscale の ACL / Grants によって、ノード間の通信が許可されている必要があります。

Redis は TCP 6789 番ポート、Ray の GCS は標準で TCP 6379 番ポートを使用します。
ただし、Ray はこれら以外にも複数のポートを使ってノード間通信を行います。

例えば、信頼できる 2 台のコンピュータ間で TCP 通信を許可する場合は、
Tailscale の管理画面にある Access controls の JSON editor で、
既存の `grants` 配列に次のルールを追加します。

```json
{
    "src": ["HEAD_NODE_IP", "REMOTE_NODE_IP"],
    "dst": ["HEAD_NODE_IP", "REMOTE_NODE_IP"],
    "ip": ["tcp:*"]
}
```

`HEAD_NODE_IP` や `REMOTE_NODE_IP` は、Tailscale で割り振られた IP アドレスに置き換えて下さい。

この設定は、指定した2台の間のすべての TCP ポートへの通信を双方向に許可します。
Ray の内部通信ポートは動的に割り当てられる場合があるため、実験用の構成を簡単にするための設定例です。

他のサービスへのアクセスも許可されるため、信頼できるノードに限定して使用して下さい。
運用環境では、Ray の通信ポートを明示的に設定し、必要なポートだけを許可することを推奨します。

#### Redis の起動
ヘッドノード側で Redis を起動します。

他のコンピュータから接続できるように、ローカルアドレスと Tailscale の IP アドレスを指定します。

```bash
redis-server \
  --port 6789 \
  --bind 127.0.0.1 "$(tailscale ip -4)" \
  --protected-mode no &
```

すでに Redis が 6789 番ポートで起動している場合は、
必要なデータや処理に影響しないことを確認してから、既存の Redis を停止して起動し直して下さい。

```bash
redis-cli -p 6789 shutdown
```

上記は信頼できる Tailscale ノードだけが接続する実験用の設定例です。
Redis 自体の認証は設定していないため、外部ネットワークへの公開は避け、
長期運用では Redis ACL 等による認証も検討して下さい。

リモートノード側から、次のコマンドで接続を確認できます。

```bash
redis-cli -h HEAD_NODE_HOST -p 6789 ping
```

上記コマンド中の `HEAD_NODE_HOST` は、ヘッドノードのホスト名もしくは IP アドレスに置き換えて下さい。

`PONG` が返ってくれば正常です。

#### Ray の起動
ヘッドノード側では、Tailscale の IP アドレスを明示的に指定して Ray を起動します。

```bash
ray start --head --node-ip-address=$(tailscale ip -4)
```

リモートノード側では、次のようにしてクラスタに参加します。

```bash
ray start \
  --address=HEAD_NODE_HOST:6379 \
  --node-ip-address=$(tailscale ip -4)
```

ヘッドノード上で以下を実行すると、参加しているノードを確認できます。

```bash
ray status
```

#### AgenTalk の設定
各コンピュータの `config.yaml` にある、Ray および Redis の接続先も指定して下さい。

例えば、上記の構成であれば、次のように設定します。

```yaml
rayHeadNodeAddress: HEAD_NODE_HOST:6379
talkChannel:        redis://HEAD_NODE_HOST:6789/0
```

すべてのノードが同じ Ray クラスタおよび Redis サーバーを参照するようにします。
以上の設定が完了したら、ヘッドノード側で `agt start` を実行して Reactor を起動して下さい。

### リアクタの起動
ヘッドノードを担当するターミナル上のシェルより、
以下のコマンドを実行して下さい。

```
agt start
```

### チケットの登録
処理を担うリモートノード上にて、
同時に実行する処理の分だけチケットを登録しておいて下さい。
ローカル LLM を使う場合は GPU メモリの使用量を考慮して、
チケットの枚数を決めて下さい
（良くわからない場合はとりあえず 1 枚だけ登録すれば良いと思います）。

- agt cl にてチケットのクリア（チケット数を 0 にします）ができます。
- agt at でチケットが 1 枚追加されます（at = add ticket）
- agt ct でチケット数が確認できます（ct = count ticket）

詳しくは agt help を実行して下さい。

### フェイズの登録
agt reg を使ってフェイズの登録は行われます。
詳細は samples/fitText の README を参照して下さい。

### フェイズの実行
agt run にてフェイズの実行指示をリアクタに通知できます。
詳しくは agt help を実行し、agt run 部分の説明をご覧下さい。

### 終了
ヘッドノード上で動作しているリアクタに対し Ctrl-C を押下、
もしくはリモートノード上で

```
agt stop
```

を実行して下さい。

