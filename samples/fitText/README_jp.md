```
filename: README_jp.md
title: fitText について
author: 飯倉宏治
```

# fitText
## fitText って何？
fitText は、指定された文字数やキーワードを守るようにローカル LLM に文章を書かせるサンプルプログラムです。
外部から与えられるイベントをきっかけに処理が起動し、
生成結果を検証しながら必要に応じて書き直す、
段階的な文書生成処理を行うものです。

## 動作概要
gate ディレクトリに .json ファイルが追加されると、
それをきっかけに fitText.firstDraft フェイズが起動します。

この .json ファイルの検知は AgenTalk とは独立しています。
この処理は gateToAgenTalk.py が担っています。
fitText.firstDraft フェイズの起動は
AgenTalk.newSession() 関数と invoke() メソッドにて
行われます。
gateToAgenTalk.py はあくまでも AgenTalk の機能を
呼び出しているだけであり、
AgenTalk に組み込まれるプログラムではありません。

fitText.firstDarft では初稿を作成し、その文章量を確認します。
必要に応じて fitText.rewrite フェイズや
fitText.finish フェイズを起動し、
result ディレクトリに生成した文章を保存し、
archive ディレクトリに生成時の条件を示した .json フィアルを移動します。
なお、エラーが発生した時は error ディレクトリに
.json ファイルは移動します。

## ディレクトリ構成

以下は、このリポジトリに含まれているディレクトリおよびファイルの構成です。

```
fitText/
+- gateToAgenTalk.py      # gate ディレクトリを監視し、AgenTalk セッションを起動するスクリプト
+- phases/                # fitText を構成する各処理フェイズ
|   +- firstDraft.py      # 初稿を生成するフェイズ
|   +- rewrite.py         # 文字数調整のために文章を書き直すフェイズ
|   +- finish.py          # 最終的な文章を確定するフェイズ
|   +- error.py           # エラー発生時の処理フェイズ
|   +- util.py            # 各フェイズで共有されるユーティリティ
+- prompts/               # 各フェイズで使用されるプロンプトテンプレート
|   +- firstDraft.txt
|   +- rewriteLess.txt
|   +- rewriteMore.txt
+- sampleParam.json       # 入力用 JSON ファイルのサンプル
+- requirements.txt
+- README.md
+- README_jp.md
```

なお、以下のディレクトリは `gateToAgenTalk.py` の実行時に
**自動的に作成されるものであり、リポジトリには含まれていません**。

- `gate/`  
  処理のトリガとなる `.json` ファイルを配置するディレクトリ

- `result/`  
  生成された文章ファイルが保存されるディレクトリ

- `archive/`  
  正常に処理が完了した `.json` ファイルが移動されるディレクトリ

- `error/`  
  処理中にエラーが発生した `.json` ファイルが移動されるディレクトリ

## 入力用 JSON フォーマット
fitText は、`gate/` ディレクトリに `.json` ファイルを配置することで起動します。  
この JSON には、文章生成時の制約条件（目標文字数や必須キーワード）と、
任意の補助的な執筆指示を記述します。

### スキーマ
- `schema`（string, 必須）  
  `"fitText"` を指定してください。

- `version`（number, 必須）  
  スキーマのバージョン番号です。現在は `1` のみがサポートされています。

- `target`（object, 必須）  
  - `target.chars`（number, 必須）  
    生成される文章の目標文字数を指定します。  
  - `target.tolerance_ratio`（number, 必須）  
    `target.chars` に対する相対的な許容誤差を指定します  
    （例：`0.10` は ±10% の範囲を意味します）。

- `keywords`（object, 必須）  
  - `keywords.required`（string の配列, 必須）  
    ここに指定したすべての文字列は、生成される文章中に  
    **表記を変更せずそのまま** 含まれている必要があります。

- `prompt`（object, 任意）  
  文章の内容や文体を調整するための補助的な指示です。  
  - `prompt.topic`（string, 任意）  
    文章全体のテーマや話題を簡潔に指定します。  
  - `prompt.notes`（string, 任意）  
    追加の制約やスタイルに関する指示を記述します  
    （例：「箇条書きを使用しない」など）。

### 例
```json
{
  "schema": "fitText",
  "version": 1,
  "target": {
    "chars": 600,
    "tolerance_ratio": 0.10
  },
  "keywords": {
    "required": ["AI エージェント","並列分散処理の必要性"]
  },
  "prompt": {
    "topic": "AI が切り開く未来社会",
    "notes": "専門用語は...(詳細は下の説明をみて下さい)"
  }
}
```

notes の全文は次の通りです：
"notes": "専門用語は最小限にし、読み手が一般の技術者でも理解できる文章にする。箇条書きは禁止。"

### 補足
実際に許容される文字数の範囲は、次の式で計算されます。

chars * (1-tolerance_ratio) から
chars * (1+tolerance_ratio) まで

書き込み途中のファイルを誤って読み込むのを避けるため、
.json ファイルは mv コマンドを用いて gate/ ディレクトリに配置することを推奨します。

## 簡易的な実行手順
AgenTalk は並列実行基盤であるため、
実際に動作させようとすると、
どうしても大掛かりなことになりがちです。
ここでは、手順の簡便さを重視し、
スケールアウトなどには考慮せず、
単一ノード上で fitText を動作させる
方法を紹介します。

### 実行環境の準備
ターミナルを 3 つ開き、それぞれから
同一の Linux ホストへログインします。

ひとつはリアクタ用ターミナル、
もう一つはディレクトリ監視用ターミナル、
残るひとつは作業用ターミナルと呼ぶこととします。
いずれのターミナルも同じ Linux ホスト上での実行なので、
AgenTalk のノードとしては単一の計算ノードとなります。

#### リアクタ用ターミナルでの作業
このターミナルでは AgenTalk のリアクタを
起動しておきます。
詳細は本リポジトリ直下の README に譲りますが、
Redis サーバーを起動した後、
本リポジトリ直下にて agt start として、
リアクタを起動して下さい。
すでに AgenTalk のリアクタが起動している場合は、
本作業は不要です。

#### 作業用ターミナルでの作業
##### リモートノードの登録
こちらも本リポジトリ直下の REAMD を参考に、
リモートノード登録を行っておきます
（同じ Linux ホスト上でリモートノードが動作している、
という状況となります）。

##### チケットの確認
AgenTalk のフェイズ処理は、チケットによる
負荷制御のもとに実施されます。
そのため、AgenTalk の処理チケットを
確認しておきます。

agt at でチケットを追加し（addTicket）、
agt ct でチケット数を確認します（countTicket）。

チケットは 1 以上あれば十分です。

##### fitText フェイズの登録
phases ディレクトリに移動し、
agt reg . を実行して下さい。
無事登録できた場合は、
ヘッドノード側のターミナルに、

```
Phase 'fitText.rewrite' is loaded.
Phase 'fitText.error' is loaded.
Phase 'fitText.firstDraft' is loaded.
Phase 'fitText.finish' is loaded.
```

と表示されます。

ここで一旦、作業用のターミナルから
ディレクトリ監視用ターミナルに切り替えます。

#### 監視用ターミナルでの作業
カレントディレクトリが、
本リポジトリのトップディレクトリであることを
確認した上で、python gateToAgenTalk.py とし、
gate ディレクトリの監視用スクリプトを実行します。
無事に起動できれば、
started gateToAgenTalk.py という文字列が表示されます。

### 文書生成の開始
作業用ターミナルにて、本リポジトリの
トップディレクトリに移動します。
cp sampleParam.json gate
として、sampleParam.json を gate ディレクトリに
コピーします。

監視用ターミナルで起動している gateToAgenTalk.py にて 
sampleParam.json が gate ディレクトリに追加されたことを
検知し、

```
[0] detect new file: ./gate/sampleParam.json
```

という文字列を出力します。
これにより fitText.firstDraft フェイズが
gateToAgenTalk.py スクリプトにより起動され、
リアクタ用ターミナルで動作している
AgenTalk リアクタ側にて

```
=== START GENERATION: sampleParam.json
```

という文字列が出力され、しばらく待っていると
生成した文章が表示された後に、

```
FINISH gate/sampleParam.json
```

という表示が出力され、sampleParam.json による文書生成が完了します。
生成されたファイルは result ディレクトリに出力されるので、
確認してみて下さい。

gate ディレクトリにコピーした sampleParam.json は
処理を行った年月日と時間の情報をファイル名に付加されて
archive ディレクトリに移動しています。

文書生成時に何かエラーが発生した場合は、
archive ディレクトリではなく error ディレクトリに
移動されます。

もし、文書生成が開始されない場合は、
gate ディレクトリに sampleParam.json が既に存在していないか
どうかを確認して下さい。
gateToAgenTalk.py は、あくまでも gate ディレクトリに
ファイルが新規追加されたことを検知するため、
既に同名のファイルが gate ディレクトリに存在している場合は
fitText.firstDarft フェイズは起動しません。

## うまく動かない場合
### ollama はインストールされていますか？
fitText は ollama 経由でローカル LLM を起動します。
そのため、もし ollama がインストールされていなければ、
fitText による文書の生成はできません。

ollama がインストールされており、
コマンドラインから利用できる状態であることを確認してください。
インストール方法については、
ollama の公式ドキュメントを参照してください。

なお、ollama が使えるか否かは次のコマンドにて確認できます：

```
ollama list
```

もしこのコマンドが正常に動作しない場合は、
ollama をインストールした後に、
fitText の実行を試してみて下さい。

