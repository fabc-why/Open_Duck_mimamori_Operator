# Operator

OpenDuckの外部動作要求を受け取り、対応するローカルプロセスやROSトピックへ
振り分けるエントリポイントです。

## 動作フロー

`Open_Duck`の機能ハンドラーが動作要求をpublishします。

```text
Open_Duckの機能ハンドラー
    ↓ std_msgs/String
/openduck/operation/actions
    ↓
Operator
    ↓
コマンドハンドラー
```

例えば、`ComeHereHandler`は`come_here`要求を次のJSONとして送ります。

```json
{"command":"come_here","target":"speaker"}
```

Operatorはこの要求を受け取り、`come_here`ハンドラーを実行して
`seek_person.py`を起動します。

```text
command=come_here
    ↓
src/commands/come_here.py
    ↓ subprocess
/home/openduck/openduck_function/seek/src/seek_person.py
```

同じコマンドが再度来ても、対応するプロセスは二重起動しません。

## Subscriber

- トピック: `/openduck/operation/actions`
- 型: `std_msgs/String`
- `data`: コマンド情報を含むJSON文字列
- `command`: 必須
- その他のフィールド: オプション

例:

```json
{"command":"come_here","target":"speaker"}
```

`command`がない場合、空文字列の場合、またはJSONとして解釈できない場合はエラーとして
処理せずログを出力します。

## 対応コマンド

### come_here

人追従処理を起動します。

- 実行ファイル:
  `/home/openduck/openduck_function/seek/.venv/bin/python`
- スクリプト:
  `/home/openduck/openduck_function/seek/src/seek_person.py`

`target`は任意で、現在はログ出力に利用します。

### stop

実行中のすべてのプロセスを停止し、停止信号をロボット制御トピックへ送ります。

- トピック: `/openduck/commands`
- 型: `std_msgs/String`
- データ:

```json
{"data":"[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]"}
```

## 起動

```bash
cd /home/openduck/openduck_function/operator
.venv/bin/python main.py
```

起動時にroslibpy経由でROS bridgeへ接続し、
`/openduck/operation/actions`を購読します。

## コマンドの追加

新しい動作は、コマンドごとにモジュールを分割します。

1. `src/commands/`にコマンド名のPythonファイルを追加する
2. `operation`と`process_manager`を受け取るハンドラー関数を実装する
3. `src/commands/__init__.py`の`COMMAND_HANDLERS`へ登録する

例:

```python
COMMAND_HANDLERS = {
    "come_here": come_here,
    "stop": stop,
}
```